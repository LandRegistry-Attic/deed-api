from underscore import _
from schema_tests.utils import load_json_file, get_from_schema, is_valid_regex
from application.deed.utils import validate_helper, call_once_only
import os
import sys


@call_once_only
def get_test_data():
    return load_json_file(os.path.dirname(os.path.realpath(__file__)) +
                          "/schema_tests/payload_tests/payload.json")


@call_once_only
def get_schema():
    return load_json_file(os.path.dirname(os.path.realpath(__file__)) +
                          get_from_schema(get_test_data(), "schema"))


def verify_patterns(element, key, obj, idx):
    pattern_path = str("test_patterns/"+key)
    path_to_pattern_in_schema = get_from_schema(get_test_data(),
                                                pattern_path+"/pattern_path")
    obj_in_schema = get_from_schema(get_schema(),
                                    path_to_pattern_in_schema)
    pattern = obj_in_schema["pattern"] if "pattern" in obj_in_schema else None
    enum = obj_in_schema["enum"] if "enum" in obj_in_schema else None
    test_payloads = get_from_schema(get_test_data(),
                                    pattern_path+"/payload_tests")
    print("Checking patterns for '%s'" % key)

    # we need to merge in pattern and enum data from parent context
    # unfortunately, functional library does not support passing in
    #  context data
    for i, test in enumerate(test_payloads):
        if enum:
            test["pattern"] = "(" + ")|(".join(enum) + ")"
        else:
            test["pattern"] = pattern

    return _.every(test_payloads, is_valid_regex)


def verify_against_schema(element, key, obj):
    error_count, error_message = validate_helper(element["payload"])

    print(
        "%s - checking for %s - errors expected: %s, errors received: %s"
        % (error_count == element["expected"], element["description"],
           element["expected"], str(error_count)))
    return error_count == element["expected"]


def run_checks():

    print("\nStarting schema tests")
    print("---------------------\n")
    pattern_results = _.every(
        get_from_schema(get_test_data(), "test_patterns"),
        verify_patterns)

    print("\nSchema pattern tests passed: %s\n" % pattern_results)

    full_payload_tests = get_from_schema(get_test_data(), "test_payloads")

    payload_results = _.every(full_payload_tests, verify_against_schema)
    print("\nPayload tests passed: %s" % payload_results)

    return pattern_results and payload_results

res = 0 if run_checks() else 1

sys.exit(res)
