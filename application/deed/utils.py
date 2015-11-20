import os
from jsonschema.validators import validator_for
import json


def validate_helper(json_to_validate):
    error_message = ""
    error_list_iterable = _title_validator.iter_errors(json_to_validate)

    for count, error in enumerate(sorted(error_list_iterable, key=str, reverse=True), start=1):
        error_message += "Problem %s:\n\n%s\n\n" % (count, str(error))

    return count, error_message


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
