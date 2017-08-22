import json
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask.ext.api import status
import application

from application.borrower.model import Borrower, VerifyMatch

borrower_bp = Blueprint('borrower', __name__,
                        template_folder='templates',
                        static_folder='static')


@borrower_bp.route('/validate', methods=['POST'])
def validate_borrower():
    payload = request.get_json()

    if 'borrower_token' in payload:
        borrower = Borrower.get_by_token(payload['borrower_token'].strip())
        if borrower:
            input_dob = datetime.strptime(payload['dob'], "%d/%m/%Y")
            db_dob = datetime.strptime(borrower.dob, "%d/%m/%Y")

            if input_dob == db_dob:
                borrower_id = borrower.id
                return json.dumps({"deed_token": borrower.deed_token, "phone_number": borrower.phonenumber, "borrower_id": borrower_id}),\
                    status.HTTP_200_OK
            else:
                application.app.logger.error("Matching DOB not found for provided borrower.")

    return "Matching deed not found", status.HTTP_404_NOT_FOUND


@borrower_bp.route('/verify/pid/<verify_pid>', methods=['GET'])
def get_borrower_details_by_verify_pid(verify_pid):
    borrower = Borrower.get_by_verify_pid(verify_pid)

    if borrower is not None:
        return json.dumps(
            {
                "borrower_token": borrower.token,
                "deed_token": borrower.deed_token,
                "phone_number": borrower.phonenumber,
                "borrower_id": borrower.id,
                "signing_in_progress": borrower.signing_in_progress
            }
        ), status.HTTP_200_OK

    return "Matching borrower not found", status.HTTP_404_NOT_FOUND


@borrower_bp.route('/verify-match/delete/<verify_pid>', methods=['DELETE'])
def delete_verify_match(verify_pid):
    verify_match_model = VerifyMatch()

    application.app.logger.info("Removing Verify Match Entry")
    application.app.logger.debug("Attempting to remove verify match entry with PID = %s" % verify_pid)

    if verify_match_model.remove_verify_match(verify_pid):
        match_message = "match found for PID provided. Row has been removed."
        application.app.logger.debug("match found for PID: row removed")
    else:
        match_message = "no match found for PID provided. Row has not been removed."
        application.app.logger.error("no match found for PID: nothing removed")

    return jsonify({'result': match_message}), status.HTTP_200_OK


@borrower_bp.route('/check_signing_in_progress/<borrower_token>', methods=['GET'])
def check_borrower_signing_in_progress(borrower_token):
    borrower = Borrower.get_by_token(borrower_token)
    if borrower:
        return jsonify({'result': borrower.signing_in_progress}), status.HTTP_200_OK

    return "Matching borrower not found", status.HTTP_404_NOT_FOUND
