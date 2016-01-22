from application.borrower.model import Borrower
from flask import Blueprint, request
from flask.ext.api import status
import json

borrower_bp = Blueprint('borrower', __name__,
                        template_folder='templates',
                        static_folder='static')


@borrower_bp.route('/validate', methods=['POST'])
def validate_borrower():
    payload = request.get_json()
    borrower = Borrower.get_by_token(payload['borrower_token'])

    if borrower is None or borrower.dob != payload['dob']:
        return "Matching deed not found", status.HTTP_404_NOT_FOUND
    else:
        return json.dumps({"deed_token": borrower.deed_token}),\
            status.HTTP_200_OK
