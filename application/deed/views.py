import logging
from application.deed.model import Deed
from application.deed.utils import validate_helper, valid_dob, is_unique_list, is_internal
from flask import request, abort, jsonify, Response
from flask import Blueprint
from flask.ext.api import status
from application.borrower.server import BorrowerService
from underscore import _
from application.borrower.model import Borrower
from application.mortgage_document.model import MortgageDocument
import json


LOGGER = logging.getLogger(__name__)

deed_bp = Blueprint('deed', __name__,
                    template_folder='templates',
                    static_folder='static')


@deed_bp.route('/<deed_reference>', methods=['GET'])
def get_deed(deed_reference):
    result = Deed.query.filter_by(token=str(deed_reference)).first()

    if result is None:
        abort(status.HTTP_404_NOT_FOUND)
    else:
        result.deed['token'] = result.token

    return jsonify({"deed": result.deed}), status.HTTP_200_OK


@deed_bp.route('', methods=['GET'])
def get_deeds_status_with_mdref_and_title_number():
    md_ref = request.args.get("md_ref")
    title_number = request.args.get("title_number")

    if md_ref and title_number:
        deeds_status = Deed.get_deed_status(title_number, md_ref)

        if len(deeds_status) == 0:
            abort(status.HTTP_404_NOT_FOUND)

        return Response(
            json.dumps(deeds_status),
            status=200,
            mimetype='application/json'
        )

    return abort(status.HTTP_400_BAD_REQUEST)


def valid_borrowers(borrowers):
    valid = _(borrowers).chain()\
        .map(lambda x, *a: x['dob'])\
        .reduce(valid_dob, True).value()

    valid &= _(borrowers).chain()\
        .map(lambda x, *a: x['phone_number'])\
        .value()\
        .is_unique_list()

    return valid


def format_borrower(borrower, idx , deed_token):
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
        abort(status.HTTP_400_BAD_REQUEST)

    borrower_json = _(borrowers).chain()\
        .map(format_borrower, deed.token)\
        .value()

    json_doc['borrowers'].append(borrower_json)

    if not update_md_clauses(json_doc, deed_json["md_ref"]):
        msg = "mortgage document associated with supplied md_ref is not found"
        LOGGER.error(msg)
        return msg, status.HTTP_400_BAD_REQUEST

    deed.deed = json_doc

    deed.save()


@deed_bp.route('/', methods=['POST'])
def create():

    deed_json = request.get_json()
    error_count, error_message = validate_helper(deed_json)

    if error_count > 0:
        return error_message, status.HTTP_400_BAD_REQUEST
    else:

        try:
            deed = Deed()

            deed.token = Deed.generate_token()

            update_deed(deed, deed_json)

            path = "/deed/" + str(deed.token)
            return jsonify({"path": path}), status.HTTP_201_CREATED

        except Exception as e:
            LOGGER.error("Database Exception - %s" % e)
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)


@deed_bp.route('/borrowers/delete/<borrower_id>', methods=['DELETE'])
def delete_borrower(borrower_id):
    borrower = None
    borrowerModel = Borrower()
    try:
        borrower = borrowerModel.delete(borrower_id)
    except Exception as inst:
        LOGGER.error(str(type(inst)) + ":" + str(inst))

    if borrower is None:
        abort(status.HTTP_404_NOT_FOUND)
    else:
        return jsonify({"id": borrower_id}), status.HTTP_200_OK
