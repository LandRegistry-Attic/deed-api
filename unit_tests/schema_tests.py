from underscore import _
from application.deed.utils import validate_helper,\
    call_once_only, get_obj_by_path, load_json_file, load_json_schema
import os
import sys
import re
from termcolor import colored


@call_once_only
def get_test_data():
    return load_json_file(os.getcwd() + "/unit_tests/schema_tests.json")


@call_once_only
def get_schema():
    return load_json_schema()


def is_valid_regex(value, *context):
    matches = re.match(value["pattern"], value["payload"]) is not None
    print("%s: Checking: '%s' matches: '%s' exp: %s got: %s desc: %s"
          % (colored('PASS', 'green') if matches == value["expected"]
             else colored('FAIL', 'red'),
             value["payload"], value["pattern"],
             value["expected"], matches, value["description"]))
    return matches == value["expected"]


def verify_pattern(element, key, obj, idx):
    print("Checking patterns for '%s'" % key)
    pattern_path = str("test_patterns/"+key)
    path_to_pattern_in_schema = get_obj_by_path(get_test_data(),
                                                pattern_path + "/pattern_path")
    obj_in_schema = get_obj_by_path(get_schema(),
                                    path_to_pattern_in_schema)
    pattern = obj_in_schema["pattern"] if "pattern" in obj_in_schema else None
    enum = obj_in_schema["enum"] if "enum" in obj_in_schema else None
    test_payloads = get_obj_by_path(get_test_data(),
                                    pattern_path + "/payload_tests")

    # we need to merge in pattern and enum data from parent context
    # unfortunately, functional library does not support passing in
    #  context data
    for i, test in enumerate(test_payloads):
        test["pattern"] = pattern if not enum else "(" + ")|(".join(enum) + ")"

    return _.every(test_payloads, is_valid_regex)


def verify_against_schema(element, key, obj):
    error_message = validate_helper(element["payload"])

    error_count = len(error_message)
    print(
        "%s: checking for %s - errors expected: %s, errors received: %s"
        % (colored('PASS', 'green') if error_count == element["expected"]
           else colored('FAIL', 'red'), element["description"],
           element["expected"], str(error_count)))
    return error_count == element["expected"]


def run_schema_checks():

    print("\nStarting schema tests")
    print("---------------------\n")
    pattern_results = _.every(
        get_obj_by_path(get_test_data(), "test_patterns"),
        verify_pattern)

    print("\nSchema pattern tests passed: %s\n" % pattern_results)

    full_payload_tests = get_obj_by_path(get_test_data(), "test_payloads")

    payload_results = _.every(full_payload_tests, verify_against_schema)
    print("\nPayload tests passed: %s" % payload_results)

    return pattern_results and payload_results

if __name__ == "__main__":
    res = 0 if run_schema_checks() else 1
    sys.exit(res)
