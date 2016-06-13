import logging
from application.deed.utils import valid_dob, is_unique_list
from application.borrower.server import BorrowerService
from underscore import _
from application.mortgage_document.model import MortgageDocument
from functools import partial
from flask.ext.api import status
from flask import abort
from application.deed.deed_status import DeedStatus
import json
import datetime
import copy
from application import esec_client
import sys
from lxml import etree


LOGGER = logging.getLogger(__name__)


def valid_borrowers(borrowers):
    valid = _(borrowers).chain()\
        .map(lambda x, *a: x['dob'])\
        .reduce(valid_dob, True).value()

    phone_number_list = _(borrowers).chain()\
        .map(lambda x, *a: x['phone_number'])\
        .value()

    valid &= is_unique_list(phone_number_list)

    return valid


def check_effective_status(deed_status):
    if DeedStatus.not_lr_signed.value not in deed_status:
        msg = "Deed has a wrong status. Status should be {0}".format(DeedStatus.not_lr_signed.value)
        LOGGER.error(msg)
        raise ValueError(msg)


def add_effective_date_to_xml(deed_xml, effective_date):
    tree = etree.fromstring(deed_xml)
    for val in tree.xpath("/dm-application/effectiveDate"):
        val.text = effective_date
        return etree.tostring(tree)


def apply_registrar_signature(deed, effective_date):

    check_effective_status(deed.status)

    deed_xml = deed.deed_xml

    effective_xml = add_effective_date_to_xml(deed_xml, effective_date)

    LOGGER.info("Applying registrar's signature to deed {}".format(deed.token))

    deed.deed_xml = esec_client.sign_document_with_authority(effective_xml)

    deed.status = DeedStatus.effective.value

    deed.save()
    LOGGER.info("Signed and saved document to DB")


def update_borrower(borrower, idx, borrowers, deed_token):
    borrower_service = BorrowerService()

    borrower_json = {
        "id": "",
        "token": "",
        "forename": borrower['forename'],
        "surname": borrower['surname']
    }

    if 'middle_name' in borrower:
        borrower_json["middle_name"] = borrower["middle_name"]

    created_borrower = borrower_service.saveBorrower(borrower, deed_token)

    borrower_json["id"] = created_borrower.id
    borrower_json["token"] = created_borrower.token

    return borrower_json


def update_md_clauses(json_doc, md_ref, organisation_name):
    mortgage_document = MortgageDocument.query.filter_by(md_ref=str(md_ref)).first()
    if mortgage_document is not None:
        md_json = json.loads(mortgage_document.data)
        json_doc["charge_clause"] = md_json["charge_clause"]
        json_doc["additional_provisions"] = md_json["additional_provisions"]
        json_doc["lender"] = md_json["lender"]
        json_doc["effective_clause"] = make_effective_text(organisation_name)

    return mortgage_document is not None


def build_json_deed_document(deed_json):

    json_doc = {
        "title_number": deed_json['title_number'],
        "md_ref": deed_json['md_ref'],
        "borrowers": [],
        "charge_clause": [],
        "additional_provisions": [],
        "property_address": deed_json['property_address'],
        "effective_clause": ""
    }

    return json_doc


def update_deed(deed, deed_json, akuma_flag):
    deed.identity_checked = deed_json["identity_checked"]
    json_doc = build_json_deed_document(deed_json)

    borrowers = deed_json["borrowers"]

    if not valid_borrowers(borrowers):
        msg = "borrower data failed validation"
        LOGGER.error(msg)
        return False, msg

    update_borrower_for_token = partial(update_borrower, deed_token=deed.token)

    borrower_json = _(borrowers).chain()\
        .map(update_borrower_for_token).value()

    json_doc['borrowers'] = borrower_json

    if not update_md_clauses(json_doc, deed_json["md_ref"], deed.organisation_name):
        msg = "mortgage document associated with supplied md_ref is not found"
        LOGGER.error(msg)
        return False, msg

    deed.deed = json_doc

    deed.save()

    return True, "OK"


def update_deed_signature_timestamp(deed, borrower_token):
    modify_deed = copy.deepcopy(deed.deed)
    for borrower in modify_deed['borrowers']:
        if borrower['token'] == borrower_token:
            borrower['signature'] = datetime.datetime.now().strftime("%d %B %Y %I:%M%p")

    deed.deed = modify_deed

    try:
        set_signed_status(deed)
        deed.save()
        deed.deed['token'] = deed.token
        return deed.deed

    except Exception as e:
        LOGGER.error("Database Exception - %s" % e)
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)


def make_effective_text(organisation_name):
    effective_clause = "This charge takes effect when the registrar receives notification from %s that the charge" + \
                       " is to take effect."

    return effective_clause % organisation_name


def set_signed_status(deed):
    LOGGER.info("updating Deed signed Status")
    signed_count = 0

    for idx, borrower in enumerate(deed.deed["borrowers"], start=0):
        if 'signature' in borrower:
            signed_count += 1

    if signed_count == len(deed.deed['borrowers']):
        deed.status = DeedStatus.all_signed.value
    elif signed_count > 0:
        deed.status = DeedStatus.partial.value


def make_deed_effective_date(deed, signed_time):
    # We deepcopy to ensure that effective_date key is generated.
    # Assigning effective date directly to the existing deed will not generate the key.
    modify_deed = copy.deepcopy(deed.deed)
    modify_deed['effective_date'] = signed_time
    deed.status = "NOT-LR-SIGNED"
    deed.deed = modify_deed
    deed.save()
