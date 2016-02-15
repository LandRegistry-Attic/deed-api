import logging
from application.deed.utils import valid_dob, is_unique_list
from application.borrower.server import BorrowerService
from underscore import _
from application.mortgage_document.model import MortgageDocument
from functools import partial
import json

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


def update_borrower(borrower, idx, borrowers, deed_token):
    borrower_service = BorrowerService()

    borrower_json = {
        "id": "",
        "token": "",
        "forename": borrower['forename'],
        "surname": borrower['surname'],
        "middle_name": borrower['middle_name'] if 'middle_name' in borrower else None
    }

    created_borrower = borrower_service.saveBorrower(borrower, deed_token)

    borrower_json["id"] = created_borrower.id
    borrower_json["token"] = created_borrower.token

    return borrower_json


def update_md_clauses(json_doc, md_ref):
    mortgage_document = MortgageDocument.query.filter_by(md_ref=str(md_ref)).first()
    if mortgage_document is not None:
        md_json = json.loads(mortgage_document.data)
        json_doc["charge_clause"] = md_json["charge_clause"]
        json_doc["additional_provisions"] = md_json["additional_provisions"]
        json_doc["lender"] = md_json["lender"]

    return mortgage_document is not None


def build_json_deed_document(deed_json):

    json_doc = {
        "title_number": deed_json['title_number'],
        "md_ref": deed_json['md_ref'],
        "borrowers": [],
        "charge_clause": [],
        "additional_provisions": [],
        "property_address": deed_json['property_address']
    }

    return json_doc


def update_deed(deed, deed_json):
    deed.identity_checked = deed_json["identity_checked"]
    json_doc = build_json_deed_document(deed_json)

    borrowers = deed_json["borrowers"]

    if not valid_borrowers(borrowers):
        msg = "borrower data failed validation"
        LOGGER.error(msg)
        return False, msg

    update_borrower_for_token = partial(update_borrower, deed_token=deed.token)

    borrower_json = _(borrowers).chain()\
        .map(update_borrower_for_token)\
        .value()

    json_doc['borrowers'] = borrower_json

    if not update_md_clauses(json_doc, deed_json["md_ref"]):
        msg = "mortgage document associated with supplied md_ref is not found"
        LOGGER.error(msg)
        return False, msg

    deed.deed = json_doc

    deed.save()

    return True, "OK"
