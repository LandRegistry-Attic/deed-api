from application.deed.model import Deed
from flask import request, abort
from flask import Blueprint
from flask.ext.api import status
import re


deed_bp = Blueprint('deed', __name__,
                    template_folder='templates',
                    static_folder='static')


@deed_bp.route('/', methods=['POST'])
def create():
    deed = Deed()
    deed_json = request.get_json()

    if validate_title_number(deed_json['title_number']):
        json_doc = {
            "deed": {
                "title_number": deed_json['title_number']
            }
        }

        deed.deed = json_doc
        try:
            deed.save()
            url = request.base_url + str(deed.id)
            return url, status.HTTP_201_CREATED
        except Exception as inst:
            print(str(type(inst)) + ":" + str(inst))
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        abort(status.HTTP_400_BAD_REQUEST)


def validate_title_number(title_number):
    TITLE_NUMBER_REGEX = \
        re.compile('^([A-Z]{0,3}[1-9][0-9]{0,5}|[0-9]{1,6}[ZT])$')
    return TITLE_NUMBER_REGEX.match(title_number)
