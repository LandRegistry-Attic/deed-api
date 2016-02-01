import datetime
import io
import json
import os
import sys
import logging

LOGGER = logging.getLogger(__name__)

from jsonschema.validators import validator_for
from lxml import etree
from underscore import _

import application.deed.generated.deed_xmlify as api

XML_SCHEMA_FILE = "deed-schema-v0-1.xsd"


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
                          "/application/deed/schemas/deed-api.json")


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
            LOGGER.error(
                "ACCESS ERROR:\nlocation in schema: %s\n with key: %s \n%s."
                % (schema, key, sys.exc_info()[0]))
            raise

    return _.reduce(path.strip("/").split("/"), down_one_level, schema)


def load_json_file(file_path):
    with open(file_path, 'rt') as file:
        json_data = json.load(file)

    return json_data


def convert_json_to_signature_slot(borrower_json):
    sig_slot = api.signatureSlotType()
    borrower_name_xml = api.nameType()
    borrower_name_xml.set_forename(borrower_json["forename"])
    borrower_name_xml.set_middlename("middlename")
    borrower_name_xml.set_surname(borrower_json["surname"])
    sig_slot.set_signatory(borrower_name_xml)
    sig_slot.set_signature(api.signatureType())
    return sig_slot


def convert_json_to_borrower(borrower_json):
    borrower = api.borrowerType()
    borrower_name_xml = api.nameType()
    borrower_name_xml.set_forename(borrower_json["forename"])
    borrower_name_xml.set_middlename("middlename")
    borrower_name_xml.set_surname(borrower_json["surname"])
    borrower.set_name(borrower_name_xml)
    borrower.set_address("borrower address")

    return borrower


def validate_generated_xml(xml):

    with open(os.getcwd() + '/application/deed/schemas/' + XML_SCHEMA_FILE, "rb") as f:
        schema_str = f.read().decode()
        # replace externally reference element with a dummy local one
        schema_str = schema_str.replace('ref="dsig:Signature"', 'name="DummySigSlot"')
        schema_root = etree.XML(schema_str.encode())
        schema = etree.XMLSchema(schema_root)
        xml_parser = etree.XMLParser(schema=schema, resolve_entities=True)

        try:
            etree.fromstring(xml, xml_parser)
            return True
        except:
            msg = str(sys.exc_info())
            print(msg)
    return False


def convert_json_to_xml(deed_json):  # pragma: no cover

    deed_app_xml = api.dmApplicationType()
    deed_app_xml.original_tagname_ = "dm-application"
    operative_deed_xml = api.operativeDeedType()
    deed_data_xml = api.deedDataType()
    borrowers = api.borrowersType()
    borrower_sig_slots = api.signatureSlotsType()

    for borrower_json in deed_json["borrowers"]:
        borrowers.add_borrower(convert_json_to_borrower(borrower_json))
        borrower_sig_slots.add_borrower_signature(convert_json_to_signature_slot(borrower_json))

    deed_data_xml.set_borrowers(borrowers)
    deed_data_xml.set_Id("deedData")
    deed_data_xml.set_mdRef(deed_json["md_ref"])
    deed_data_xml.set_titleNumber(deed_json["title_number"])
    deed_data_xml.set_propertyDescription("property description")
    operative_deed_xml.set_deedData(deed_data_xml)
    deed_app_xml.set_effectiveDate("23/5/15")
    auth_sig = api.authSignatureType()
    deed_app_xml.set_authSignature(auth_sig)
    operative_deed_xml.set_signatureSlots(borrower_sig_slots)
    deed_app_xml.set_operativeDeed(operative_deed_xml)

    deed_stream = io.StringIO()
    deed_app_xml.export(deed_stream, 0,
                        namespacedef_='xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                                      'xsi:noNamespaceSchemaLocation="http://localhost:9080/schemas/' +
                                      XML_SCHEMA_FILE + '"'
                        )
    deed_xml = deed_stream.getvalue()

    return deed_xml

_title_validator = _create_title_validator()
