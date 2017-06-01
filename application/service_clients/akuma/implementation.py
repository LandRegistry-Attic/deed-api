from application import config
from flask.ext.api import status
from flask import current_app, g


def perform_check(payload):  # pragma: no cover
    data = None

    resp = g.requests.post(config.AKUMA_BASE_HOST + "/", json=payload)

    current_app.logger.info("Making call to Akuma")

    if resp.status_code == status.HTTP_200_OK:
        data = resp.json()
    return data
