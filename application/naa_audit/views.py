from application.naa_audit.model import NAAAudit
from flask import Blueprint
from flask.ext.api import status
import datetime
import json


naa_bp = Blueprint('naa', __name__, template_folder='templates', static_folder='static')


@naa_bp.route('/accept/<borrower_id>', methods=['POST'])
def accept_naa(borrower_id):
    naa = NAAAudit()
    naa.borrower_id = int(borrower_id)
    naa.date_accepted = datetime.datetime.now()

    result = naa.save()

    return json.dumps({"id": naa.id}), result



@naa_bp.route('/accept/<id>', methods=['GET'])
def get_naa(id):
    naa = NAAAudit()
    res = naa.get_by_id(id)

    return json.dumps({"id": res.id, "borrower_id": res.borrower_id, "date_accepted": str(res.date_accepted)}), status.HTTP_200_OK
