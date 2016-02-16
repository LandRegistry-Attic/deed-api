import logging
from application.deed.model import Deed
from flask import abort
from flask import Blueprint
from flask.ext.api import status
import sys
from application.casework.service import get_document

LOGGER = logging.getLogger(__name__)

casework_bp = Blueprint('casework', __name__,
                        template_folder='templates',
                        static_folder='static')


@casework_bp.route('/<deed_reference>', methods=['GET'])
def get_deed(deed_reference):
    result = Deed.query.filter_by(token=str(deed_reference)).first()

    if result is None:
        abort(status.HTTP_404_NOT_FOUND)
    else:
        try:
            resp = get_document()
            return resp

        except:
            msg = str(sys.exc_info())
            LOGGER.log(msg)
            return msg
