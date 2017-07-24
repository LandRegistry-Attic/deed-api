from flask import Blueprint
from flask.ext.api import status
from application.mortgage_document.model import MortgageDocument

mortgage_document_bp = Blueprint('mortgage_document', __name__, template_folder='templates', static_folder='static')


@mortgage_document_bp.route('/get-legal-warning/<md_ref>', methods=['GET'])
def get_legal_warning(md_ref):

    legal_warning = MortgageDocument.get_by_md(md_ref)
    if legal_warning:
        if legal_warning.legal_warning:
            return legal_warning.legal_warning, status.HTTP_200_OK

    return "", status.HTTP_404_NOT_FOUND
