from application import config
from flask.ext.api import status
from flask import abort, current_app, g


class ExternalServiceError(Exception):
    pass


class EsecException(Exception):
    pass


def issue_sms(forenames, last_name, organisation_id, phone_number):  # pragma: no cover
    current_app.logger.info("Calling dm-esec-client to initiate signing")
    request_url = config.ESEC_CLIENT_BASE_HOST + '/esec/issue_sms'

    parameters = {
        'forenames': forenames,
        'last-name': last_name,
        'organisation-id': organisation_id,
        'phone-number': phone_number
    }

    resp = g.requests.post(request_url, params=parameters)

    if resp.status_code == status.HTTP_200_OK:
        current_app.logger.info("Response XML = %s" % resp.content)
        return resp.content, resp.status_code
    else:
        current_app.logger.error("Esecurity Client Exception when trying to initiate signing process and issue auth code")
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)


def reissue_sms(esec_user_name):  # pragma: no cover
    current_app.logger.info("Calling dm-esec-client to reissue auth code")
    request_url = config.ESEC_CLIENT_BASE_HOST + '/esec/reissue_sms'

    parameters = {
        'esec-username': esec_user_name
    }

    resp = g.requests.post(request_url, params=parameters)

    if resp.status_code == status.HTTP_200_OK:
        current_app.logger.info("Response XML = %s" % resp.content)
        return resp.content, resp.status_code
    else:
        current_app.logger.error("Esecurity Client Exception when trying to reissue auth code")
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)


def auth_sms(deed_xml, borrower_pos, user_id, borrower_auth_code):  # pragma: no cover
    current_app.logger.info("Calling dm-esec-client to verify OTP code and sign the deed")
    request_url = config.ESEC_CLIENT_BASE_HOST + '/esec/auth_sms'
    element_id = 'deedData'
    borrower_path = "/dm-application/operativeDeed/signatureSlots"

    parameters = {
        'borrower-pos': borrower_pos,
        'element-id': element_id,
        'borrowers-path': borrower_path,
        'user-id': user_id,
        'otp-code': borrower_auth_code
    }

    resp = g.requests.post(request_url, params=parameters, data=deed_xml)

    if resp.status_code == status.HTTP_200_OK or resp.status_code == status.HTTP_401_UNAUTHORIZED:
        current_app.logger.info("Response XML = %s" % resp.content)
        return resp.content, resp.status_code
    else:
        current_app.logger.error("Esecurity Client Exception when trying to verify OTP code and sign the deed ")
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)


def _post_request(url, data):
    current_app.logger.info("Calling: %s", url)
    resp = g.requests.post(url, data=data)
    if resp.status_code == status.HTTP_200_OK:
        return resp.content
    else:
        msg = resp.content
        current_app.logger.error("{0}".format(msg,))
        raise ExternalServiceError(msg)


def sign_document_with_authority(deed_xml):
    current_app.logger.info("Calling dm-esec-client to sign the deed with the registrar's signature")
    request_url = config.ESEC_CLIENT_BASE_HOST + '/esec/sign_document_with_authority'
    try:
        return _post_request(request_url, deed_xml)
    except (g.requests.exceptions.ConnectionError, ExternalServiceError):
        raise EsecException


def check_health():
    service_response = g.requests.get(config.ESEC_CLIENT_BASE_HOST + "/health/service-check")

    return service_response
