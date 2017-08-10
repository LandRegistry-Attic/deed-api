import copy
import json
from application.deed.deed_status import DeedStatus
from application.deed.utils import valid_dob, is_unique_list
from flask import abort
from flask.ext.api import status
from functools import partial
from lxml import etree
from underscore import _

from application.borrower.model import Borrower as BorrowerModel
from application.borrower.server import BorrowerService
from application.mortgage_document.model import MortgageDocument
from application.service_clients.esec import make_esec_client
from application.service_clients.organisation_adapter import make_organisation_adapter_client
import application


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
        application.app.logger.error(msg)
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

    application.app.logger.info("Applying registrar's signature to deed {}".format(deed.token))
    esec_client = make_esec_client()
    deed.deed_xml = esec_client.sign_document_with_authority(effective_xml)
    deed.status = DeedStatus.effective.value
    deed.save()
    application.app.logger.info("Signed and saved document to DB")


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

    if 'id' not in borrower:
        created_borrower = borrower_service.saveBorrower(borrower, deed_token)

        borrower_json["id"] = created_borrower.id
        borrower_json["token"] = created_borrower.token
    else:
        borrower_updater = BorrowerModel()
        updated_borrower = borrower_updater.update_borrower_by_id(borrower)

        borrower_json["id"] = int(borrower["id"])
        borrower_json["token"] = updated_borrower.token

    return borrower_json


def update_md_clauses(json_doc, md_ref, reference, date_of_mortgage_offer, miscellaneous_information,
                      organisation_name):
    mortgage_document = MortgageDocument.query.filter_by(md_ref=str(md_ref)).first()
    if mortgage_document is not None:
        md_json = json.loads(mortgage_document.data)
        json_doc["charge_clause"] = md_json["charge_clause"]
        json_doc["additional_provisions"] = md_json["additional_provisions"]
        json_doc["lender"] = md_json["lender"]
        json_doc["effective_clause"] = make_effective_text(organisation_name)

        if "lender_reference_name" in md_json and reference.strip():
            json_doc["reference_details"] = {
                "lender_reference_name": md_json["lender_reference_name"],
                "lender_reference_value": reference
            }
        if "date_of_mortgage_offer_heading" in md_json and date_of_mortgage_offer.strip():
            json_doc["date_of_mortgage_offer_details"] = {
                "date_of_mortgage_offer_heading": md_json["date_of_mortgage_offer_heading"],
                "date_of_mortgage_offer_value": date_of_mortgage_offer
            }

        if "miscellaneous_information_heading" in md_json and miscellaneous_information.strip():
            json_doc["miscellaneous_information_details"] = {
                "miscellaneous_information_heading": md_json["miscellaneous_information_heading"],
                "miscellaneous_information_value": miscellaneous_information
            }

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


def update_deed(deed, deed_json):
    deed.identity_checked = deed_json["identity_checked"]
    json_doc = build_json_deed_document(deed_json)

    borrowers = deed_json["borrowers"]
    update_borrower_for_token = partial(update_borrower, deed_token=deed.token)

    borrower_json = _(borrowers).chain()\
        .map(update_borrower_for_token).value()

    json_doc['borrowers'] = borrower_json

    reference = ""
    if "reference" in deed_json:
        reference = deed_json["reference"]

    date_of_mortgage_offer = ""
    if "date_of_mortgage_offer" in deed_json:
        date_of_mortgage_offer = deed_json["date_of_mortgage_offer"]

    miscellaneous_information = ""
    if "miscellaneous_information" in deed_json:
        miscellaneous_information = deed_json["miscellaneous_information"]

    if not update_md_clauses(json_doc, deed_json["md_ref"], reference, date_of_mortgage_offer,
                             miscellaneous_information, get_organisation_name(deed)):
        msg = "mortgage document associated with supplied md_ref is not found"
        application.app.logger.error(msg)
        return False, msg

    assign_deed(deed, json_doc)

    deed.payload_json = deed_json

    deed.save()

    delete_orphaned_borrowers(deed)

    return True, "OK"


def get_organisation_name(deed):
    organisation_interface = make_organisation_adapter_client()
    return organisation_interface.get_organisation_name(deed.organisation_name)


def update_deed_signature_timestamp(deed, borrower_token, datetime):

    modify_deed = copy.deepcopy(deed.deed)
    for borrower in modify_deed['borrowers']:
        if str(borrower['token']).upper() == borrower_token:
            borrower['signature'] = datetime

    deed.deed = modify_deed

    try:
        set_signed_status(deed)
        deed.save()

    except Exception as e:
        application.app.logger.error("Database Exception occurred whilst updating deed signature timestamp - %s" % e)
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)


def make_effective_text(organisation_name):
    effective_clause = "This charge takes effect when the registrar receives notification from %s that the charge" + \
                       " is to take effect."

    return effective_clause % organisation_name


def set_signed_status(deed):
    application.app.logger.info("updating Deed signed Status")
    signed_count = 0

    for idx, borrower in enumerate(deed.deed["borrowers"], start=0):
        if 'signature' in borrower:
            signed_count += 1

    if signed_count == len(deed.deed['borrowers']):
        deed.status = DeedStatus.all_signed.value
        application.app.logger.info('Deed status has been changed to ALL-SIGNED')
    elif signed_count > 0:
        deed.status = DeedStatus.partial.value
        application.app.logger.info('Deed status has been changed to PARTIAL')


def make_deed_effective_date(deed, signed_time):
    # We deepcopy to ensure that effective_date key is generated.
    # Assigning effective date directly to the existing deed will not generate the key.
    modify_deed = copy.deepcopy(deed.deed)
    modify_deed['effective_date'] = signed_time
    deed.status = "NOT-LR-SIGNED"
    application.app.logger.info('Deed status has been changed to NOT-LR-SIGNED')
    deed.deed = modify_deed
    deed.save()


def assign_deed(deed, json_doc):
    deed.deed = json_doc


def delete_orphaned_borrowers(deed):
    borrower_list = []

    for borrower in deed.deed["borrowers"]:
        borrower_list.append(borrower["id"])

        borrower_model_delete = BorrowerModel()

    borrower_model_delete.delete_borrowers_not_on_deed(borrower_list, deed.token)
    return True
