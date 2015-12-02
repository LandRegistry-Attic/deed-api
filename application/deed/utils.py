from jsonschema.validators import validator_for
from underscore import _
import os
import json
import datetime
import sys


def validate_helper(json_to_validate):
    error_message = ""
    error_list = sorted(_title_validator.iter_errors(json_to_validate),
                        key=str, reverse=True)

    for count, error in enumerate(error_list, start=1):
        error_message += "Problem %s:\n\n%s\n\n" % (count, str(error))

    return len(error_list), error_message


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


def call_once_only(func):
    def decorated(*args, **kwargs):
        try:
            return decorated._once_result
        except AttributeError:
            decorated._once_result = func(*args, **kwargs)
            return decorated._once_result
    return decorated


# schema is a json obj/dict
# path - contains the string path to a dict attribute
# with '/' separators e.g. /root/sub_ele/child1/attr_name
def get_obj_by_path(schema, path):

    def down_one_level(schema, key, context):
        try:
            res = schema[key]
            return res
        except:
            print("ACCESS ERROR:\nlocation in schema: %s\n with key: %s \n%s."
                  % (schema, key, sys.exc_info()[0]))
            raise

    return _.reduce(path.strip("/").split("/"), down_one_level, schema)


_title_validator = _create_title_validator()
