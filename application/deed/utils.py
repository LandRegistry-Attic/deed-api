from jsonschema.validators import validator_for
from underscore import _
import os
import json
import datetime
import sys
import logging

LOGGER = logging.getLogger(__name__)


def call_once_only(func):
    def decorated(*args, **kwargs):
        try:
            return decorated._once_result
        except AttributeError:
            decorated._once_result = func(*args, **kwargs)
            return decorated._once_result
    return decorated


def validate_helper(json_to_validate):
    error_message = ""
    error_list = sorted(_title_validator.iter_errors(json_to_validate),
                        key=str, reverse=True)

    for count, error in enumerate(error_list, start=1):
        error_message += "Problem %s:\n\n%s\n\n" % (count, str(error))

    return len(error_list), error_message


@call_once_only
def get_swagger_file():
    return load_json_file(os.getcwd() +
                          "/application/deed/deed-api.json")


def load_json_schema():
    swagger = get_swagger_file()

    definitions = swagger["definitions"]
    deed_application_definition = definitions["Deed_Application"]

    deed_application = {
        "definitions": definitions,
        "properties": deed_application_definition["properties"],
        "required": deed_application_definition["required"],
        "type": "object",
        "additionalProperties": False
    }

    return deed_application


def _create_title_validator():
    schema = load_json_schema()
    validator = validator_for(schema)
    validator.check_schema(schema)
    return validator(schema)


def valid_dob(result, date_string, index):
    try:
        if not result:
            return False

        borrower_date = datetime.datetime.strptime(
            date_string, '%d/%m/%Y')

        if borrower_date > datetime.datetime.now():
            return False

        return True
    except:
        return False


def is_unique_list(list):
    return len(dict.fromkeys(list, 0)) == len(list)


# schema is a json obj/dict
# path - contains the string path to a dict attribute
# with '/' separators e.g. /root/sub_ele/child1/attr_name
def get_obj_by_path(schema, path):

    def down_one_level(schema, key, context):
        try:
            res = schema[key]
            return res
        except:
            LOGGER.info(
                "ACCESS ERROR:\nlocation in schema: %s\n with key: %s \n%s."
                % (schema, key, sys.exc_info()[0]))
            raise

    return _.reduce(path.strip("/").split("/"), down_one_level, schema)


def load_json_file(file_path):
    with open(file_path, 'rt') as file:
        json_data = json.load(file)

    return json_data


_title_validator = _create_title_validator()
