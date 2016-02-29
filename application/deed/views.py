import logging
from application.akuma.service import Akuma
from application.deed.model import Deed
from application.deed.utils import validate_helper, process_organisation_credentials
from application.deed.service import update_deed, update_deed_signature_timestamp
from flask import request, abort, jsonify, Response
from flask import Blueprint
from flask.ext.api import status
from application.borrower.model import Borrower
from twilio.rest import TwilioRestClient
import json
import sys
from application import config


LOGGER = logging.getLogger(__name__)

deed_bp = Blueprint('deed', __name__,
                    template_folder='templates',
                    static_folder='static')


@deed_bp.route('/<deed_reference>', methods=['GET'])
def get_deed(deed_reference):

    result = Deed.get_deed(deed_reference)

    if result is None:
        abort(status.HTTP_404_NOT_FOUND)
    else:
        result.deed['token'] = result.token

        # 2 Factor auth initialisations
        bor_token = "abcdef"
        res_token = result.token
        phone_number = "insert phone_number here"
        bor_code = "0c4def"

        send_simulation = send_sms(res_token, bor_token, phone_number)
        verify_simulation = verify_sms(res_token, bor_token, bor_code)

        print (send_simulation)
        print (verify_simulation)

    return jsonify({"deed": result.deed}), status.HTTP_200_OK


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
            deed = Deed()
            deed.token = Deed.generate_token()
            check_result = Akuma.do_check(deed_json, "create deed")
            LOGGER.info("Check ID: " + check_result['id'])

            organisation_credentials = process_organisation_credentials()

            if organisation_credentials:
                deed.organisation_id = organisation_credentials["O"][1]
                deed.organisation_name = organisation_credentials["O"][0]
                success, msg = update_deed(deed, deed_json, check_result['result'])

                if not success:
                    LOGGER.error("Update deed 400_BAD_REQUEST")
                    return msg, status.HTTP_400_BAD_REQUEST
            else:
                LOGGER.error("Unable to process headers")
                return "Unable to process headers", status.HTTP_401_UNAUTHORIZED

            if check_result['result'] != "A":
                LOGGER.error("Akuma endpoint 503_SERVICE_UNAVAILABLE")
                return abort(status.HTTP_503_SERVICE_UNAVAILABLE)

            return jsonify({"path": '/deed/' + str(deed.token)}), status.HTTP_201_CREATED

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


@deed_bp.route('/<deed_reference>/sign', methods=['POST'])
def sign_deed(deed_reference):
    request_json = request.get_json()
    borrower_token = request_json['borrower_token']
    result = Deed.get_deed(deed_reference)

    if result is None:
        LOGGER.error("Database Exception 404 for deed reference - %s" % deed_reference)
        abort(status.HTTP_404_NOT_FOUND)
    else:
        LOGGER.info("Signing deed for borrower_id %s against deed reference %s" % (borrower_token, deed_reference))

        result.deed = update_deed_signature_timestamp(result, borrower_token)

    return jsonify({"deed": result.deed}), status.HTTP_200_OK


@deed_bp.route('/<deed_reference>/make-effective', methods=['POST'])
def make_effective(deed_reference):
    return status.HTTP_200_OK


@deed_bp.route('/<deed_reference>/send-sms', methods=['POST'])
def send_sms(deed_reference, borrower_token, borrower_phone_number):
    if borrower_token is not None and borrower_token != '':
        if borrower_phone_number is not None and borrower_phone_number != '':
            code = generate_sms_code(deed_reference, borrower_token)
            print (code)

            message = code + " is your digital mortgage authentication code."
            twilio_phone_number = "+441442796219"

            client = TwilioRestClient(config.account, config.auth)

            client.messages.create(
                to=borrower_phone_number,
                from_=twilio_phone_number,
                body=message,
            )
            return True, status


@deed_bp.route('/<deed_reference>/verify-sms', methods=['POST'])
def verify_sms(deed_reference, borrower_token, borrower_code):
    #get submitted code
    #compare submitted code
    #notify user of the authenication outcome
    if borrower_token is not None and borrower_token != '':
        if borrower_code is not None and borrower_code != '':
            code = generate_sms_code(deed_reference, borrower_token)
            if borrower_code != code:
                LOGGER.error("Invalid code")
                return "Unable to complete authentication", status.HTTP_401_UNAUTHORIZED
            else:
                return True, status.HTTP_200_OK


def generate_sms_code(deed_reference, borrower_token):
    gen_code = deed_reference[-3:] + borrower_token[-3:]
    return gen_code
