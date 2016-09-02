import collections
import copy
import json
import logging
import sys
from datetime import datetime

from application import esec_client
from application.akuma.service import Akuma
from application.borrower.model import Borrower
from application.deed.deed_render import create_deed_pdf
from application.deed.model import Deed, deed_json_adapter, deed_pdf_adapter
from application.deed.service import update_deed, update_deed_signature_timestamp, apply_registrar_signature, \
    make_deed_effective_date
from application.deed.utils import convert_json_to_xml
from application.deed.validation_order import Validation
from flask import Blueprint
from flask import request, abort, jsonify, Response
from flask.ext.api import status

LOGGER = logging.getLogger(__name__)

deed_bp = Blueprint('deed', __name__,
                    template_folder='templates',
                    static_folder='static')


@deed_bp.route('/<deed_reference>', methods=['GET'])
def get_deed(deed_reference):
    if 'application/pdf' in request.headers.get("Accept", ""):
        return create_deed_pdf(deed_pdf_adapter(deed_reference)), status.HTTP_200_OK
    return jsonify(deed_json_adapter(deed_reference)), status.HTTP_200_OK


@deed_bp.route('/<deed_reference>', methods=['PUT'])
def get_existing_deed_and_update(deed_reference):
    deed = Deed()
    deed_update_json = request.get_json()

    validator = Validation()

    credentials = validator.validate_organisation_credentials()
    if credentials is None:
        return jsonify({"message": "Unable to process organisation credentials"}), status.HTTP_401_UNAUTHORIZED

    result_deed = deed.get_deed(deed_reference)
    if result_deed is None:
        LOGGER.error("Deed with reference - %s not found" % str(deed_reference))
        return jsonify({"message": "There is no deed associated with this deed id."}), \
            status.HTTP_400_BAD_REQUEST

    # Deed Status check
    if str(result_deed.status) != "DRAFT":
        return jsonify({"message": "This deed is not in a draft state"}), \
            status.HTTP_400_BAD_REQUEST

    ids = []
    for borrower in deed_update_json["borrowers"]:
        if 'id' in borrower:
            ids.append(borrower['id'])

    duplicates = [item for item, count in collections.Counter(ids).items() if count > 1]
    if duplicates:
        return jsonify({"message": "Error duplicate borrower ID's in payload"}), \
            status.HTTP_400_BAD_REQUEST

    for borrower_id in ids:
        borrower_check = Borrower.get_by_id(borrower_id)

        if borrower_check is None or borrower_check.deed_token != deed_reference:
            return jsonify({"message": "Borrowers provided do not match the selected deed"}), \
                   status.HTTP_400_BAD_REQUEST

    error_count, error_message = validator.validate_payload(deed_update_json)
    if error_count > 0:
        return error_message, status.HTTP_400_BAD_REQUEST

    validate_title_number = validator.validate_title_number(deed_update_json)
    if validate_title_number != "title OK":
        return jsonify({"message": validate_title_number}), status.HTTP_400_BAD_REQUEST

    # From here - errors are grouped
    error_list = []

    validate_borrower_names, msg = validator.validate_borrower_names(deed_update_json)
    if not validate_borrower_names:
        error_list.append(msg)

    akuma_call = validator.call_akuma(deed_update_json, deed.token,
                                      credentials['organisation_name'],
                                      credentials['organisation_locale'],
                                      deed_type="create deed")

    # This will be replaced in full with US329
    if akuma_call['result'] != "B":
        return jsonify({"message": "Unable to use this service. This might be because of technical difficulties or "
                                   "entries on the register not being suitable for digital applications. "
                                   "You will need to complete this transaction using a paper deed."}), \
            status.HTTP_200_OK

    dob_validate, msg = validator.validate_dob(deed_update_json)
    if not dob_validate:
        error_list.append(msg)

    phone_validate, msg = validator.validate_phonenumbers(deed_update_json)
    if not phone_validate:
        error_list.append(msg)

    md_validate, msg = validator.validate_md_exists(deed_update_json['md_ref'])
    if not md_validate:
        error_list.append(msg)

    # Error List Print Out
    if len(error_list) > 0:
        compiled_list = send_error_list(error_list)
        return compiled_list

    success, msg = update_deed(result_deed, deed_update_json)
    if not success:
        LOGGER.error("Update deed 400_BAD_REQUEST")
        return msg, status.HTTP_400_BAD_REQUEST

    return jsonify({"path": '/deed/' + str(deed_reference)}), status.HTTP_200_OK


@deed_bp.route('', methods=['GET'])
def get_deeds_status_with_mdref_and_title_number():
    md_ref = request.args.get("md_ref")
    title_number = request.args.get("title_number")

    if md_ref and title_number:
        deeds_status = Deed.get_deed_status(title_number, md_ref)

        if len(deeds_status) == 0:
            abort(status.HTTP_404_NOT_FOUND)

        return Response(
            json.dumps({"deed_references": deeds_status}),
            status=200,
            mimetype='application/json'
        )

    return abort(status.HTTP_400_BAD_REQUEST)


@deed_bp.route('/', methods=['POST'])
def create():
    deed = Deed()
    deed.token = Deed.generate_token()
    deed_json = request.get_json()

    validator = Validation()

    credentials = validator.validate_organisation_credentials()
    if credentials is None:
        return jsonify({"message": "Unable to process organisation credentials."}), status.HTTP_401_UNAUTHORIZED

    deed.organisation_id = credentials['organisation_id']
    deed.organisation_name = credentials['organisation_name']

    error_count, error_message = validator.validate_payload(deed_json)
    if error_count > 0:
        return error_message, status.HTTP_400_BAD_REQUEST

    validate_title_number = validator.validate_title_number(deed_json)
    if validate_title_number != "title OK":
        return jsonify({"message": validate_title_number}), status.HTTP_400_BAD_REQUEST

    # From here - errors are grouped
    error_list = []

    validate_borrower_names, msg = validator.validate_borrower_names(deed_json)
    if not validate_borrower_names:
        error_list.append(msg)

    akuma_call = validator.call_akuma(deed_json, deed.token,
                                      credentials['organisation_name'],
                                      credentials['organisation_locale'],
                                      deed_type="create deed")

    print(akuma_call['result'])
    # This will be replaced in full with US329
    if akuma_call['result'] != "B":
        return jsonify({"message": "Unable to use this service. This might be because of technical difficulties or "
                                   "entries on the register not being suitable for digital applications. "
                                   "You will need to complete this transaction using a paper deed."}), \
            status.HTTP_403_FORBIDDEN

    dob_validate, msg = validator.validate_dob(deed_json)
    if not dob_validate:
        error_list.append(msg)

    phone_validate, msg = validator.validate_phonenumbers(deed_json)
    if not phone_validate:
        error_list.append(msg)

    md_validate, msg = validator.validate_md_exists(deed_json['md_ref'])
    if not md_validate:
        error_list.append(msg)

    # Error List Print Out
    if len(error_list) > 0:
        compiled_list = send_error_list(error_list)
        return compiled_list

    success, msg = update_deed(deed, deed_json)
    if not success:
        LOGGER.error("Update deed 400_BAD_REQUEST")
        return msg, status.HTTP_400_BAD_REQUEST

    return jsonify({"path": '/deed/' + str(deed.token)}), status.HTTP_201_CREATED


@deed_bp.route('/borrowers/delete/<borrower_id>', methods=['DELETE'])
def delete_borrower(borrower_id):
    borrower = None
    borrowerModel = Borrower()
    try:
        borrower = borrowerModel.delete(borrower_id)
    except Exception as inst:
        LOGGER.error(str(type(inst)) + ":" + str(inst))

    if borrower is None:
        abort(status.HTTP_404_NOT_FOUND)
    else:
        return jsonify({"id": borrower_id}), status.HTTP_200_OK


def auth_sms(deed_reference, borrower_token, borrower_code):
    deed_instance = Deed()
    deed = deed_instance.get_deed(deed_reference)

    if deed is None:
        LOGGER.error("Database Exception 404 for deed reference - %s" % deed_reference)
        abort(status.HTTP_404_NOT_FOUND)
    else:
        LOGGER.info("Signing deed for borrower_token %s against deed reference %s" % (borrower_token, deed_reference))

        # check if XML already exist
        if deed.deed_xml is None:
            LOGGER.info("Generating DEED_XML")
            deed_XML = convert_json_to_xml(deed.deed)
            deed.deed_xml = deed_XML.encode("utf-8")

        try:
            LOGGER.info("getting existing XML")
            modify_xml = copy.deepcopy(deed.deed_xml)
            borrower_pos = deed.get_borrower_position(borrower_token)
            borrower = Borrower.get_by_token(borrower_token)
            esec_id = borrower.esec_user_name

            if esec_id:
                result_xml, status_code = esec_client.auth_sms(modify_xml, borrower_pos,
                                                               esec_id, borrower_code)
                LOGGER.info("signed status code: %s", str(status_code))
                LOGGER.info("signed XML: %s" % result_xml)

                if status_code == 200:
                    deed.deed_xml = result_xml

                    LOGGER.info("Saving XML to DB")
                    deed.save()

                    LOGGER.info("updating JSON with Signature")
                    deed.deed = update_deed_signature_timestamp(deed, borrower_token)
                    check_result = Akuma.do_check(deed.deed, "borrower sign",
                                                  deed.organisation_name, "", deed.token)
                    LOGGER.info("Check ID - Borrower SIGNING: " + check_result['id'])
                else:
                    LOGGER.error("Failed to sign Mortgage document")
                    return "Failed to sign Mortgage document", status_code
            else:
                LOGGER.error("Failed to sign Mortgage document - unable to create user")
                abort(status.HTTP_500_INTERNAL_SERVER_ERROR)

        except:
            msg = str(sys.exc_info())
            LOGGER.error("Failed to sign Mortgage document: %s" % msg)
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)

    return jsonify({"deed": deed.deed}), status.HTTP_200_OK


def issue_sms(deed_reference, borrower_token):
    deed_instance = Deed()
    deed = deed_instance.get_deed(deed_reference)

    if deed is None:
        LOGGER.error("Database Exception 404 for deed reference - %s" % deed_reference)
        abort(status.HTTP_404_NOT_FOUND)
    else:
        LOGGER.info("Signing deed for borrower_token %s against deed reference %s" % (borrower_token, deed_reference))

        try:
            LOGGER.info("getting existing XML")
            borrower = Borrower.get_by_token(borrower_token)

            if not borrower.esec_user_name:
                LOGGER.info("creating esec user for borrower[token:%s]", borrower.token)
                user_id, status_code = esec_client.issue_sms(borrower.forename, borrower.surname,
                                                             deed.organisation_id, borrower.phonenumber)
                if status_code == 200:
                    LOGGER.info("Created new esec user: %s for borrower[token:%s]", str(user_id.decode()),
                                borrower.token)
                    borrower.esec_user_name = user_id.decode()
                    borrower.save()
                else:
                    LOGGER.error("Unable to create new e-sec user for borrower [token:%s]", borrower.token)
                    abort(status.HTTP_500_INTERNAL_SERVER_ERROR)

            else:
                result, status_code = esec_client.reissue_sms(borrower.esec_user_name)

            if status_code != 200:
                LOGGER.error("Unable to reissue new sms code for esec user: %s", borrower.esec_user_name)
                abort(status.HTTP_500_INTERNAL_SERVER_ERROR)

        except:
            msg = str(sys.exc_info())
            LOGGER.error("Failed to issue auth code via sms: %s" % msg)
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)

    return status.HTTP_200_OK


@deed_bp.route('/retrieve-signed', methods=['GET'])
def retrieve_signed_deed():
    deed = Deed()
    result = deed.get_signed_deeds()

    if not result:
        return jsonify({"message": "There are no deeds which have been fully signed"}), status.HTTP_404_NOT_FOUND
    else:
        return jsonify({"deeds": result}), status.HTTP_200_OK


@deed_bp.route('/<deed_reference>/make-effective', methods=['POST'])
def make_effective(deed_reference):
    deed = Deed()
    result = deed.get_deed(deed_reference)
    if result is None:
        LOGGER.error("Deed with reference - %s not found" % str(deed_reference))
        abort(status.HTTP_404_NOT_FOUND)
    else:

        deed_status = str(result.status)

        if deed_status == "ALL-SIGNED":
            check_result = Akuma.do_check(result.deed, "make effective", result.organisation_id,
                                          result.organisation_name, result.token)
            LOGGER.info("Check ID - Make Effective: " + check_result['id'])

            signed_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            make_deed_effective_date(result, signed_time)

            apply_registrar_signature(result, signed_time)

            return '', status.HTTP_200_OK

        elif deed_status == "EFFECTIVE" or deed_status == "NOT-LR-SIGNED":
            LOGGER.error("Deed with reference - %s is in %s status and can not be registrar signed" %
                         (str(deed_reference), str(deed_status)))
            return jsonify({"message": "This deed has already been made effective."}), \
                status.HTTP_400_BAD_REQUEST

        else:
            LOGGER.error("Deed with reference - %s is not fully signed and can not be registrar signed" %
                         str(deed_reference))
            return jsonify({"message": "This deed cannot be made effective as not all borrowers "
                                       "have signed the deed."}), status.HTTP_400_BAD_REQUEST


@deed_bp.route('/<deed_reference>/request-auth-code', methods=['POST'])
def request_auth_code(deed_reference):
    request_json = request.get_json()

    status_code = issue_sms(deed_reference, request_json['borrower_token'])

    if status_code == status.HTTP_200_OK:
        return jsonify({"result": True}), status_code
    else:
        LOGGER.error("Unable to send SMS")
        return jsonify({"result": False}), status.HTTP_500_INTERNAL_SERVER_ERROR


@deed_bp.route('/<deed_reference>/verify-auth-code', methods=['POST'])
def verify_auth_code(deed_reference):
    request_json = request.get_json()
    borrower_token = request_json['borrower_token']
    borrower_code = request_json['authentication_code']

    deed, status_code = auth_sms(deed_reference, borrower_token, borrower_code)

    if status_code == status.HTTP_200_OK:
        LOGGER.info("Borrower with token %s successfully authenticated using valid authentication code: %s",
                    borrower_token, borrower_code)
        return jsonify({"result": True}), status.HTTP_200_OK
    elif status_code == status.HTTP_401_UNAUTHORIZED:
        LOGGER.error("Invalid authentication code: %s for borrower token %s ", borrower_code, borrower_token)
        return jsonify({"result": False}), status_code
    else:
        LOGGER.error("Not able to sign the deed")
        return jsonify({"result": False}), status_code


def send_error_list(error_list):
    LOGGER.error("Update deed 400_BAD_REQUEST - Error List")
    error_message = []
    for count, error in enumerate(error_list, start=1):
        error_message.append("Problem %s: %s" % (count, str(error)))

    return jsonify({"Errors": error_message}), status.HTTP_400_BAD_REQUEST
