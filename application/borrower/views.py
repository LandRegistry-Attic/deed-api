import json
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask.ext.api import status

from application.borrower.model import Borrower, VerifyMatch

borrower_bp = Blueprint('borrower', __name__,
                        template_folder='templates',
                        static_folder='static')


@borrower_bp.route('/validate', methods=['POST'])
def validate_borrower():
    payload = request.get_json()

    if 'borrower_token' in payload:
        borrower = Borrower.get_by_token(payload['borrower_token'].strip())
        if borrower is not None:
            input_dob = datetime.strptime(payload['dob'], "%d/%m/%Y")
            db_dob = datetime.strptime(borrower.dob, "%d/%m/%Y")

            if input_dob == db_dob:
                stripped_number = strip_number_to_four_digits(borrower.phonenumber)
                borrower_id = borrower.id
                return json.dumps({"deed_token": borrower.deed_token, "phone_number": stripped_number, "borrower_id": borrower_id}),\
                    status.HTTP_200_OK

    return "Matching deed not found", status.HTTP_404_NOT_FOUND


@borrower_bp.route('/verify/pid/<verify_pid>', methods=['GET'])
def get_borrower_details_by_verify_pid(verify_pid):
    borrower = Borrower.get_by_verify_pid(verify_pid)

    if borrower is not None:
        stripped_number = strip_number_to_four_digits(borrower.phonenumber)
        return json.dumps(
            {
                "borrower_token": borrower.token,
                "deed_token": borrower.deed_token,
                "phone_number": stripped_number,
                "borrower_id": borrower.id
            }
        ), status.HTTP_200_OK

    return "Matching borrower not found", status.HTTP_404_NOT_FOUND


@borrower_bp.route('/verify-match/delete/<verify_pid>', methods=['DELETE'])
def delete_verify_match(verify_pid):
    verify_match_model = VerifyMatch()

    current_app.logger.info("trying to remove verify match entry - PID = %s" % verify_pid)

    if verify_match_model.remove_verify_match(verify_pid):
        match_message = "match found for PID %s: row removed" % verify_pid
        current_app.logger.info(match_message)
    else:
        match_message = "no match found for PID %s: nothing removed" % verify_pid
        current_app.logger.error(match_message)

    return jsonify({'result': match_message}), status.HTTP_200_OK


def strip_number_to_four_digits(phone_number):
    stripped_number = phone_number[-4:]
    return stripped_number
