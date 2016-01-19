import logging
from application.deed.model import Deed
from application.deed.utils import validate_helper, valid_dob, is_unique_list
from flask import request, abort, jsonify
from flask import Blueprint
from flask.ext.api import status
from application.borrower.server import BorrowerService
from underscore import _
from application.borrower.model import Borrower
import logging
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


@deed_bp.route('/', methods=['POST'])
def create():
    deed = Deed()
    deed_json = request.get_json()
    borrowerService = BorrowerService()

    error_count, error_message = validate_helper(deed_json)

    if error_count > 0:
        return error_message, status.HTTP_400_BAD_REQUEST
    else:
        deed.deed = deed_json

        json_doc = {
            "title_number": deed_json['title_number'],
            "md_ref": deed_json['md_ref'],
            "borrowers": [],
            "charge_clause": [],
            "additional_provisions": []
            }

        deed.token = Deed.generate_token()
        deed.identity_checked = deed_json["identity_checked"]

        valid_dob_result = _(deed_json['borrowers']).chain()\
            .map(lambda x, *a: x['dob'])\
            .reduce(valid_dob, True).value()

        if not valid_dob_result:
            abort(status.HTTP_400_BAD_REQUEST)

        phone_number_list = _(deed_json['borrowers']).chain()\
            .map(lambda x, *a: x['phone_number'])\
            .value()

        if not is_unique_list(phone_number_list):
            abort(status.HTTP_400_BAD_REQUEST)

        try:
            for borrower in deed_json['borrowers']:
                borrower_json = {
                    "id": "",
                    "token": "",
                    "forename": borrower['forename'],
                    "surname": borrower['surname']
                }

                if 'middle_name' in borrower:
                    borrower_json['middle_name'] = borrower['middle_name']

                borrower['deed_token'] = deed.token

                createdBorrower = borrowerService.saveBorrower(borrower,
                                                               deed.token)

                borrower_json["id"] = createdBorrower.id
                borrower_json["token"] = createdBorrower.token
                json_doc['borrowers'].append(borrower_json)

            md_ref = deed_json["md_ref"]
            mortgage_document = MortgageDocument.query.filter_by(md_ref=str(md_ref)).first()
            if mortgage_document is not None:
                md_json = json.loads(mortgage_document.data)
                json_doc["charge_clause"] = md_json["charge_clause"]
                json_doc["additional_provisions"] = md_json["additional_provisions"]
                json_doc["lender"] = md_json["lender"]
            else:
                msg = "mortgage document associated with supplied md_ref is not found"
                LOGGER.error(msg)
                return msg, status.HTTP_400_BAD_REQUEST

            deed.deed = json_doc

            deed.save()

            url = request.base_url + str(deed.token)

            return jsonify({"url": url}), status.HTTP_201_CREATED

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
