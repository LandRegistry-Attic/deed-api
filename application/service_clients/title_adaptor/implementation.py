from application import config
from flask import g
import application


def perform_check(title):  # pragma: no cover
    application.app.logger.info("Making title validator call")
    application.app.logger.debug("Using title number '%s' for request", title)
    resp = g.requests.get(config.TITLE_ADAPTOR_BASE_HOST + "/titlenumber/" + title)

    application.app.logger.info('Call to Title Adapter has been successful.') if resp.status_code == 200 \
        else application.app.logger.error('Call to Title Adapter has failed.')

    return resp


def check_health():
    service_response = g.requests.get(config.TITLE_ADAPTOR_BASE_HOST + '/health/service-check')
    return service_response
