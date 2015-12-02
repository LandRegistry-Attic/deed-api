from underscore import _
import json
import sys
import re


def down_one_level(schema, key, context):
    try:
        res = schema[key]
        return res
    except:
        print("ACCESS ERROR:\nlocation in schema: %s\n with key: %s \n%s."
              % (schema, key, sys.exc_info()[0]))
        raise


# schema is a json obj/dict
# path - contains the string path to a dict attribute
# with '/' separators e.g. /root/sub_ele/child1/attr_name
def get_from_schema(schema, path):
    return _.reduce(path.strip("/").split("/"), down_one_level, schema)


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
