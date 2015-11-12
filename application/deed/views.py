from application.deed.model import Deed
from flask import request, abort
from flask import Blueprint
from flask.ext.api import status


deed_bp = Blueprint('deed', __name__,
                    template_folder='templates',
                    static_folder='static')


@deed_bp.route('/', methods=['POST'])
def create():
    deed = Deed()
    deed_json = request.get_json()

    json_doc = {
        "deed": {
            "title-number": deed_json['title-number']
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
