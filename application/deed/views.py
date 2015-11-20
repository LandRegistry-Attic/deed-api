from application.deed.model import Deed
from application.deed.utils import validate_helper
from flask import request, abort
from flask import Blueprint
from flask.ext.api import status
import json


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

    return json.dumps(result.deed), status.HTTP_200_OK


@deed_bp.route('/', methods=['POST'])
def create():
    deed = Deed()
    deed_json = request.get_json()

    error_count, error_message = validate_helper(deed_json)

    if error_count > 0:
        return error_message, status.HTTP_400_BAD_REQUEST
    else:
        deed.deed = deed_json
        deed.token = Deed.generate_token()
        try:
            deed.save()
            url = request.base_url + str(deed.token)
            return url, status.HTTP_201_CREATED
        except Exception as e:
            print("Database Exception - %s" % e)
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
