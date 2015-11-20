import os
from jsonschema.validators import validator_for
import json


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


_title_validator = _create_title_validator()
