from application import config
from flask.ext.api import status
from flask import g, abort
import application


def perform_check(payload):  # pragma: no cover
    data = None

    application.app.logger.info("Making call to Akuma")

    resp = g.requests.post(config.AKUMA_BASE_HOST + "/", json=payload)

    if resp.status_code == status.HTTP_200_OK:
        data = resp.json()
    else:
        application.app.logger.error('Call to Akuma returned with a %s status code', resp.status_code)
    return data
