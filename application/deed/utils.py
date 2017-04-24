import datetime
import io
import json
import os
import sys
import logging
from jsonschema.validators import validator_for
from lxml import etree
from underscore import _
import application.deed.generated.deed_xmlify as api
from flask import request
import urllib
from application import config


LOGGER = logging.getLogger(__name__)


XML_SCHEMA_FILE = "deed-schema-v0-4.xsd"

SCHEMA_LOCATION = config.ESEC_SCHEMA_LOCATION


def call_once_only(func):
    def decorated(*args, **kwargs):
        try:
            return decorated._once_result
        except AttributeError:
            decorated._once_result = func(*args, **kwargs)
            return decorated._once_result
    return decorated


def validate_helper(json_to_validate):
    schema_errors = []

    error_list = sorted(_title_validator.iter_errors(json_to_validate),
                        key=str, reverse=True)

    for count, error in enumerate(error_list, start=1):
        schema_errors.append(str(error))

    return schema_errors


@call_once_only
def get_swagger_file():
    dirname = os.path.dirname(os.path.abspath(__file__))
    return load_json_file(dirname +
                          "/schemas/deed-api.json")


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
    with open(file_path, 'rt', encoding='utf-8') as file:
        json_data = json.load(file)

    return json_data


def convert_json_to_signature_slot(borrower_json):
    sig_slot = api.signatureSlotType()
    borrower_name_xml = api.nameType()
    private_individual = api.privateIndividualType()
    private_individual.set_forename(borrower_json["forename"])

    if 'middle_name' in borrower_json:
        private_individual.set_middlename(borrower_json["middle_name"])

    private_individual.set_surname(borrower_json["surname"])
    borrower_name_xml.set_privateIndividual(private_individual)
    sig_slot.set_signatory(borrower_name_xml)
    sig_slot.set_signature(api.signatureType())
    return sig_slot


def convert_json_to_borrower(borrower_json):
    borrower = api.borrowerType()
    borrower_name_xml = api.nameType()
    private_individual = api.privateIndividualType()
    private_individual.set_forename(borrower_json["forename"])

    if 'middle_name' in borrower_json:
        private_individual.set_middlename(borrower_json["middle_name"])

    private_individual.set_surname(borrower_json["surname"])
    borrower_name_xml.set_privateIndividual(private_individual)
    borrower.set_name(borrower_name_xml)
    borrower.set_address("borrower address")

    return borrower


def convert_json_to_lender(lender_json):
    lender = api.lenderType()
    lender_name_xml = api.nameType()
    company = api.companyType()
    company.set_name(lender_json["name"])
    lender_name_xml.set_company(company)
    lender.set_organisationName(lender_name_xml)
    lender.set_address(lender_json["address"])
    lender.set_companyRegistrationDetails(lender_json["registration"])

    return lender


def convert_json_to_provision(provision_json, pos):
    additional_provision_xml = api.provisionType()
    additional_provision_xml.set_code(provision_json["additional_provision_code"])
    additional_provision_xml.set_entryText("<![CDATA["+provision_json["description"]+"]]>")
    additional_provision_xml.set_sequenceNumber(pos)

    return additional_provision_xml


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


def convert_json_to_xml(deed_json):

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
    deed_data_xml.set_propertyDescription(deed_json["property_address"])

    charge_clause_xml = api.chargeClauseType()
    charge_clause_xml.set_creCode(deed_json["charge_clause"]["cre_code"])
    charge_clause_xml.set_entryText(deed_json["charge_clause"]["description"])
    deed_data_xml.set_chargeClause(charge_clause_xml)

    additional_provisions = api.additionalProvisionsType()

    for idx, provision_json in enumerate(deed_json["additional_provisions"]):
        additional_provisions.add_provision(convert_json_to_provision(provision_json, idx))

    deed_data_xml.set_additionalProvisions(additional_provisions)

    deed_data_xml.set_lender(convert_json_to_lender(deed_json["lender"]))

    deed_data_xml.set_effectiveClause(deed_json["effective_clause"])

    if 'reference' in deed_json:
        deed_data_xml.set_reference(deed_json["reference"])

    if 'date_of_mortgage_offer' in deed_json:
        deed_data_xml.set_date_of_mortgage_offer(deed_json["date_of_mortgage_offer"])

    if 'miscellaneous_information' in deed_json:
        deed_data_xml.set_miscellaneous_information(deed_json["miscellaneous_information"])

    operative_deed_xml.set_deedData(deed_data_xml)
    deed_app_xml.set_effectiveDate("tbc")
    auth_sig = api.authSignatureType()
    deed_app_xml.set_authSignature(auth_sig)
    operative_deed_xml.set_signatureSlots(borrower_sig_slots)
    deed_app_xml.set_operativeDeed(operative_deed_xml)

    deed_stream = io.StringIO()
    deed_app_xml.export(deed_stream, 0,
                        namespacedef_='xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                                      'xsi:noNamespaceSchemaLocation="' + SCHEMA_LOCATION +
                                      XML_SCHEMA_FILE + '"'
                        )
    deed_xml = deed_stream.getvalue()

    return deed_xml


def is_internal():
    return True if os.getenv('LR_HEADER_INTERNAL_ORG') in request.headers else False


def process_organisation_credentials():
    header_dict = {}

    try:
        header_data = request.headers.get(os.getenv('WEBSEAL_HEADER_KEY'))

        for param in header_data.split(','):
            key, value = param.split('=')
            value = urllib.parse.unquote(value)
            if key in header_dict:
                header_dict[key].append(value)
            else:
                header_dict[key] = [value]
    except:
        msg = str(sys.exc_info())
        LOGGER.error("unable to process organisation credentials %s" % msg)
        header_dict = None

    return header_dict


def get_borrower_position(deed, borrower_token):
        for idx, borrower in enumerate(deed['borrowers'], start=1):
            if borrower_token == borrower['token']:
                return idx
        return -1


_title_validator = _create_title_validator()
