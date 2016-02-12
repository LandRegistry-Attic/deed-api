from application.borrower.model import Borrower
from flask import Blueprint, request
from flask.ext.api import status
import json
from datetime import datetime

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
                return json.dumps({"deed_token": borrower.deed_token}),\
                    status.HTTP_200_OK

    return "Matching deed not found", status.HTTP_404_NOT_FOUND
