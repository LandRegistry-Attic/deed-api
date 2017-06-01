from application import config
from flask import current_app, g


def perform_check(title):  # pragma: no cover
    resp = g.requests.get(config.TITLE_ADAPTOR_BASE_HOST + "/titlenumber/" + title)

    current_app.logger.info("Making title validator call")

    return resp


def check_health():
    service_response = g.requests.get(config.TITLE_ADAPTOR_BASE_HOST + '/health/service-check')
    return service_response
