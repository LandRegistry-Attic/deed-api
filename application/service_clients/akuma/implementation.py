import requests
from application import config
from flask.ext.api import status
import logging

LOGGER = logging.getLogger(__name__)


def perform_check(payload):  # pragma: no cover
    data = None

    resp = requests.post(config.AKUMA_BASE_HOST + "/", json=payload)

    LOGGER.info("Making call to Akuma")

    if resp.status_code == status.HTTP_200_OK:
        data = resp.json()
    return data
