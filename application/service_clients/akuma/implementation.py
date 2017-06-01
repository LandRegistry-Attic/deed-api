import requests
from application import config
from flask.ext.api import status
from flask import current_app


def perform_check(payload):  # pragma: no cover
    data = None

    resp = requests.post(config.AKUMA_BASE_HOST + "/", json=payload)

    current_app.logger.info("Making call to Akuma")

    if resp.status_code == status.HTTP_200_OK:
        data = resp.json()
    return data
