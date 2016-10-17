from application.naa_audit.model import NAAAudit
from flask import Blueprint, request
from flask.ext.api import status
import datetime


naa_bp = Blueprint('naa', __name__,
                        template_folder='templates',
                        static_folder='static')

@naa_bp.route('/accept/<borrower_id>', methods=['POST'])
def accept_naa(borrower_id):
    naa = NAAAudit()
    naa.borrower_id = int(borrower_id)
    naa.date_accepted = datetime.datetime.now()

    naa.save()

    return '', status.HTTP_200_OK
