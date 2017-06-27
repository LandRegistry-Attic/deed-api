import requests
import logging
from application import config
from flask.ext.api import status
from flask import abort
from application.dependencies.rabbitmq import Emitter, broker_url
import datetime
import base64
from lxml import etree

from application.deed.model import Deed


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


def auth_sms(deed, borrower_pos, user_id, borrower_auth_code, borrower_token):  # pragma: no cover

    LOGGER.info("Calling dm-esec-client to verify OTP code and sign the deed")
    element_id = 'deedData'
    borrower_path = "/dm-application/operativeDeed/signatureSlots"

    parameters = {
        'borrower-pos': borrower_pos,
        'element-id': element_id,
        'borrowers-path': borrower_path,
        'user-id': user_id,
        'otp-code': borrower_auth_code,
        'service-id': 1,
    }

    extra_parameters = {
        'borrower-token': borrower_token,
        'datetime': datetime.datetime.now().strftime("%d %B %Y %I:%M%p"),
        'deed-id': deed.token
    }

    LOGGER.info("Calling esec_client to hit validateSMSOTP...")

    request_url = config.ESEC_CLIENT_BASE_HOST + "/esec/auth_sms"

    resp = requests.post(request_url, params=parameters, data=deed.deed_xml)

    if resp.status_code == status.HTTP_200_OK or resp.status_code == status.HTTP_401_UNAUTHORIZED:
        LOGGER.info("Response XML = %s" % resp.content)

        LOGGER.info("Hashing deed prior to sending message to queue...")
        # Check if deed_hash exists on table - if it does, break
        if deed.deed_hash:
            return "Hashed deed exists on table", 500
        else:
            tree = etree.fromstring(deed.deed_xml)
            deed_data_xml = tree.xpath('.//deedData')[0]

            deed.deed_hash = Deed().generate_hash(etree.tostring(deed_data_xml))
            extra_parameters.update({'deed-hash': deed.deed_hash})
            LOGGER.info("Marking deed as in progress immediately prior to sending message to queue...")
            deed.save()

            LOGGER.info("Preparing to send message to the queue...")

            try:
                url = broker_url('rabbitmq', 'guest', 'guest', 5672)
                with Emitter(url, config.EXCHANGE_NAME, 'esec-signing-key') as emitter:
                    emitter.send_message({'params': parameters, 'extra-parameters': extra_parameters, 'data': base64.b64encode(deed.deed_xml).decode()})
                    LOGGER.info("Message sent to the queue...")
                    return "", 200
            except Exception as e:
                LOGGER.info('Error returned when trying to place an item on the queue: %s' % e)

    else:
        LOGGER.error("ESecurity Client Exception when trying to verify the OTP code")
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)


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
