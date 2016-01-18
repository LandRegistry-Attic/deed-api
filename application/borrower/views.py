from application.borrower.model import Borrower
from flask import Blueprint, abort
from flask.ext.api import status
import json

borrower_bp = Blueprint('borrower', __name__,
                        template_folder='templates',
                        static_folder='static')


@borrower_bp.route('/<borrower_token>', methods=['GET'])
def validate_borrower(borrower_token):

    borrower = None
    borrower = Borrower.get_by_token(borrower_token)

    if borrower is None:
        abort(status.HTTP_404_NOT_FOUND)
    else:
        return json.dumps({"deed_token": borrower.deed_token}),\
            status.HTTP_200_OK
