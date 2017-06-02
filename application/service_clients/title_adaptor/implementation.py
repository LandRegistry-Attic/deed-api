from application import config
from flask import g
import application


def perform_check(title):  # pragma: no cover
    application.app.logger.info("Making title validator call")
    resp = g.requests.get(config.TITLE_ADAPTOR_BASE_HOST + "/titlenumber/" + title)

    return resp


def check_health():
    service_response = g.requests.get(config.TITLE_ADAPTOR_BASE_HOST + '/health/service-check')
    return service_response
