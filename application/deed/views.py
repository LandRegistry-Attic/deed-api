from application.deed.model import Deed
from flask import request, abort
from flask import Blueprint
from flask.ext.api import status
from jsonschema.validators import validator_for
import re
import os
import json

deed_bp = Blueprint('deed', __name__,
                    template_folder='templates',
                    static_folder='static')

_title_validator = None


@deed_bp.route('/<deed_reference>', methods=['GET'])
def get_deed(deed_reference):
    result = Deed.query.filter_by(id=int(deed_reference)).first()

    if result is None:
        abort(status.HTTP_404_NOT_FOUND)
    else:
        result.deed['id'] = result.id

    return json.dumps(result.deed), status.HTTP_200_OK


@deed_bp.route('/', methods=['POST'])
def create():
    deed = Deed()
    deed_json = request.get_json()

    try:
        _title_validator.validate(deed_json)
    except Exception as e:
        print("Invalid JSON - %s" % e)
        abort(status.HTTP_400_BAD_REQUEST)

    if validate_title_number(deed_json['title_number']):

        print (deed_json)
        json_doc = {
            "deed": {
                "title_number": deed_json['title_number'],
                "borrowers": deed_json['borrowers']
            }
        }

        deed.deed = deed_json
        try:
            deed.save()
            url = request.base_url + str(deed.id)
            return url, status.HTTP_201_CREATED
        except Exception as e:
            print("Database Exception - %s" % e)
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        abort(status.HTTP_400_BAD_REQUEST)


def validate_title_number(title_number):
    TITLE_NUMBER_REGEX = \
        re.compile('^([A-Z]{0,3}[1-9][0-9]{0,5}|[0-9]{1,6}[ZT])$')
    return TITLE_NUMBER_REGEX.match(title_number)


def _load_json_schema():
    script_path = os.path.dirname(os.path.realpath(__file__))
    json_path = os.path.join(script_path, 'schema.json')
    schema_file = open(json_path)
    schema_contents = schema_file.read()
    return json.loads(schema_contents)


def _create_title_validator():
    schema = _load_json_schema()
    validator = validator_for(schema)
    validator.check_schema(schema)
    return validator(schema)


_title_validator = _create_title_validator()
