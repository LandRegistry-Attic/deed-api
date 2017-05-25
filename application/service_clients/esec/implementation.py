import requests
import logging
from application import config
from flask.ext.api import status
from flask import abort
from application.dependencies.rabbitmq import Emitter, broker_url

LOGGER = logging.getLogger(__name__)


class ExternalServiceError(Exception):
    pass


class EsecException(Exception):
    pass


def issue_sms(forenames, last_name, organisation_id, phone_number):  # pragma: no cover
    LOGGER.info("Calling dm-esec-client to initiate signing")
    request_url = config.ESEC_CLIENT_BASE_HOST + '/esec/issue_sms'

    parameters = {
        'forenames': forenames,
        'last-name': last_name,
        'organisation-id': organisation_id,
        'phone-number': phone_number
    }

    resp = requests.post(request_url, params=parameters)

    if resp.status_code == status.HTTP_200_OK:
        LOGGER.info("Response XML = %s" % resp.content)
        return resp.content, resp.status_code
    else:
        LOGGER.error("Esecurity Client Exception when trying to initiate signing process and issue auth code")
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)


def reissue_sms(esec_user_name):  # pragma: no cover
    LOGGER.info("Calling dm-esec-client to reissue auth code")
    request_url = config.ESEC_CLIENT_BASE_HOST + '/esec/reissue_sms'

    parameters = {
        'esec-username': esec_user_name
    }

    resp = requests.post(request_url, params=parameters)

    if resp.status_code == status.HTTP_200_OK:
        LOGGER.info("Response XML = %s" % resp.content)
        return resp.content, resp.status_code
    else:
        LOGGER.error("Esecurity Client Exception when trying to reissue auth code")
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)


def auth_sms(deed_xml, borrower_pos, user_id, borrower_auth_code, borrower_token):  # pragma: no cover

    LOGGER.info("Calling dm-esec-client to verify OTP code and sign the deed")
    element_id = 'deedData'
    borrower_path = "/dm-application/operativeDeed/signatureSlots"

    parameters = {
        'borrower-pos': borrower_pos,
        'element-id': element_id,
        'borrowers-path': borrower_path,
        'user-id': user_id,
        'otp-code': borrower_auth_code,
    }

    extra_parameters = {
        'borrower-token': borrower_token
    }

    LOGGER.info("Preparing to send message to the queue...")

    try:
        url = broker_url('rabbitmq', 'guest', 'guest', 5672)
        with Emitter(url, config.EXCHANGE_NAME, 'esec-signing-key') as emitter:
            emitter.send_message({'params': parameters, 'extra-parameters': extra_parameters, 'data': str(deed_xml)})
            LOGGER.info("Message sent to the queue...")
            return "", 200
    except Exception as e:
        LOGGER.info('Error returned when trying to place an item on the queue: %s' % e)


def _post_request(url, data):
    LOGGER.info("Calling: %s", url)
    resp = requests.post(url, data=data)
    if resp.status_code == status.HTTP_200_OK:
        return resp.content
    else:
        msg = resp.content
        LOGGER.error("{0}".format(msg,))
        raise ExternalServiceError(msg)


def sign_document_with_authority(deed_xml):
    LOGGER.info("Calling dm-esec-client to sign the deed with the registrar's signature")
    request_url = config.ESEC_CLIENT_BASE_HOST + '/esec/sign_document_with_authority'
    try:
        return _post_request(request_url, deed_xml)
    except (requests.exceptions.ConnectionError, ExternalServiceError):
        raise EsecException


def check_health():
    service_response = requests.get(config.ESEC_CLIENT_BASE_HOST + "/health/service-check")

    return service_response
