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
    make_deed_effective_date, modify_deed
from application.deed.utils import validate_helper, process_organisation_credentials, convert_json_to_xml
from application.deed.validate_borrowers import check_borrower_names, BorrowerNamesException
from application.title_adaptor.service import TitleAdaptor
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
        return create_deed_pdf(deed_pdf_adapter(deed_reference))
    return jsonify(deed_json_adapter(deed_reference)), status.HTTP_200_OK


@deed_bp.route('/<deed_reference>', methods=['PUT'])
def get_existing_deed_and_update(deed_reference):
    # Firstly check payload coming in is valid:
    deed = Deed()
    updated_deed_json = request.get_json()

    error_count, error_message = validate_helper(updated_deed_json)

    if error_count > 0:
        return error_message, status.HTTP_400_BAD_REQUEST
    else:

        try:
            # Borrower Validation on new JSON
            check_borrower_names(updated_deed_json)

            # If Valid: Get Current Deed using Deed Ref in request
            result = deed.get_deed(deed_reference)

            if result is None:
                return jsonify({"message": "Deed not Found"}), \
                       status.HTTP_400_BAD_REQUEST

            # Deed Status check
            deed_status = str(result.status)
            if deed_status != "DRAFT":
                return jsonify({"message": "This deed is not in a draft state"}), \
                       status.HTTP_400_BAD_REQUEST

            organisation_credentials = process_organisation_credentials()

            # Inform Akuma
            check_result = Akuma.do_check(updated_deed_json, "modify deed",
                                          organisation_credentials["O"][0], organisation_credentials["C"][0])
            LOGGER.info("Check ID - MODIFY: " + check_result['id'])

            # Title Check
            valid_title = TitleAdaptor.do_check(updated_deed_json['title_number'])
            if valid_title != "title OK":
                return jsonify({"message": valid_title}), status.HTTP_400_BAD_REQUEST

            # Deed update call from CREATE
            success, msg = update_deed(result, updated_deed_json, check_result['result'])

            if not success:
                LOGGER.error("Update deed 400_BAD_REQUEST")
                return msg, status.HTTP_400_BAD_REQUEST

            return jsonify({"path": '/deed/' + str(deed_reference)}), status.HTTP_200_OK

            ##Unhappy verification
            # else:
            #     LOGGER.error("Unable to process headers")
            #     return "Unable to process headers", status.HTTP_401_UNAUTHORIZED

        except BorrowerNamesException:
            return (jsonify({'message':
                                 "a digital mortgage cannot be created as there is a discrepancy between the names given and those held on the register."}),
                    status.HTTP_400_BAD_REQUEST)
        except:
            msg = str(sys.exc_info())
            LOGGER.error("Database Exception - %s" % msg)
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)

    #########################################################################
    # Code not reformatted from here onwards                                #
    #########################################################################
    #  Get existing borrowers and loop through to get
    #  the ID's that the pasted JSON will overwrite
    LOGGER.info("Interpreting Existing Borrowers")
    existing_deed_borrowers = result.deed['borrowers']
    for (i, existing_borrower) in enumerate(existing_deed_borrowers):
        updated_deed_json['borrowers'][i]['id'] = existing_borrower['id']


    else:
        result.deed = updated_deed_json
        json_doc = {
            "title_number": updated_deed_json['title_number'],
            "md_ref": updated_deed_json['md_ref'],
            "borrowers": []
        }

    # Make a deed out of new information
    valid_dob_result = _(updated_deed_json['borrowers']).chain() \
        .map(lambda x, *a: x['dob']) \
        .reduce(valid_dob, True).value()

    if not valid_dob_result:
        abort(status.HTTP_400_BAD_REQUEST)

    phone_number_list = _(updated_deed_json['borrowers']).chain() \
        .map(lambda x, *a: x['phone_number']) \
        .value()

    if not is_unique_list(phone_number_list):
        abort(status.HTTP_400_BAD_REQUEST)
    LOGGER.info("New Deed Created")
    try:
        LOGGER.info("Iterating PUT borrowers into existing borrowers")
        for borrower in updated_deed_json['borrowers']:
            borrower_json = {
                "id": borrower['id'],
                "forename": borrower['forename'],
                "surname": borrower['surname']
            }
            if 'middle_name' in borrower:
                borrower_json['middle_name'] = borrower['middle_name']
            json_doc['borrowers'].append(borrower_json)

        LOGGER.info("Saving the borrowers")
        borrowerService.saveBorrower(borrower, borrower_json["id"])

        result.deed = json_doc
        LOGGER.info("Saving the deed")
        result.save()
        url = request.base_url
        LOGGER.info("Deed Saved, returned URL = " + url)
        return url, status.HTTP_200_OK
    except Exception as e:
        print("Database Exception - %s" % e)
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)


@deed_bp.route('', methods=['GET'])
def get_deeds_status_with_mdref_and_title_number():
    md_ref = request.args.get("md_ref")
    title_number = request.args.get("title_number")

    if md_ref and title_number:
        deeds_status = Deed.get_deed_status(title_number, md_ref)

        if len(deeds_status) == 0:
            abort(status.HTTP_404_NOT_FOUND)

        return Response(
            json.dumps(deeds_status),
            status=200,
            mimetype='application/json'
        )

    return abort(status.HTTP_400_BAD_REQUEST)


@deed_bp.route('/', methods=['POST'])
def create():
    deed_json = request.get_json()
    error_count, error_message = validate_helper(deed_json)

    if error_count > 0:
        LOGGER.error("Schema validation 400_BAD_REQUEST")
        return error_message, status.HTTP_400_BAD_REQUEST
    else:

        try:
            check_borrower_names(deed_json)
            deed = Deed()
            deed.token = Deed.generate_token()

            organisation_credentials = process_organisation_credentials()

            if organisation_credentials:
                deed.organisation_id = organisation_credentials["O"][1]
                deed.organisation_name = organisation_credentials["O"][0]
                organisation_locale = organisation_credentials["C"][0]
                check_result = Akuma.do_check(deed_json, "create deed",
                                              deed.organisation_name, organisation_locale)
                LOGGER.info("Check ID: " + check_result['id'])
                valid_title = TitleAdaptor.do_check(deed_json['title_number'])
                if valid_title != "title OK":
                    return jsonify({"message": valid_title}), status.HTTP_400_BAD_REQUEST

                success, msg = update_deed(deed, deed_json, check_result['result'])

                if not success:
                    LOGGER.error("Update deed 400_BAD_REQUEST")
                    return msg, status.HTTP_400_BAD_REQUEST
            else:
                LOGGER.error("Unable to process headers")
                return "Unable to process headers", status.HTTP_401_UNAUTHORIZED

            return jsonify({"path": '/deed/' + str(deed.token)}), status.HTTP_201_CREATED
        except BorrowerNamesException:
            return (jsonify({'message':
                                 "a digital mortgage cannot be created as there is a discrepancy between the names given and those held on the register."}),
                    status.HTTP_400_BAD_REQUEST)
        except:
            msg = str(sys.exc_info())
            LOGGER.error("Database Exception - %s" % msg)
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        abort(status.HTTP_404_NOT_FOUND)
    else:

        deed_status = str(result.status)

        if deed_status == "ALL-SIGNED":
            Akuma.do_check(result.deed, "make effective", result.organisation_id, result.organisation_name)

            signed_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            make_deed_effective_date(result, signed_time)

            apply_registrar_signature(result, signed_time)

            return '', status.HTTP_200_OK

        elif deed_status == "EFFECTIVE" or deed_status == "NOT-LR-SIGNED":
            return jsonify({"message": "This deed is already made effective."}), \
                   status.HTTP_400_BAD_REQUEST

        else:
            return jsonify({"message": "You can not make this deed effective "
                                       "as it is not fully signed."}), \
                   status.HTTP_400_BAD_REQUEST


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
