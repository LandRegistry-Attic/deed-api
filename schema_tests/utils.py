import json
import re


def load_json_file(file_name):
    with open(file_name, 'rt') as file:
        json_data = json.load(file)

    return json_data


def is_valid_regex(value, *context):
    matches = re.match(value["pattern"], value["payload"]) is not None
    print("Pass: %s, Checking: '%s' matches: '%s' exp: %s got: %s desc: %s"
          % (matches == value["expected"], value["payload"], value["pattern"],
             value["expected"], matches, value["description"]))
    return matches == value["expected"]
