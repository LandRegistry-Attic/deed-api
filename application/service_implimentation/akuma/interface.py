import requests
from application import config
from flask.ext.api import status


def perform_check(payload):  # pragma: no cover
    data = None

    resp = requests.get(config.AKUMA_BASE_HOST,json=payload)

    if resp.status_code == status.HTTP_200_OK:
        data = resp.json()

    return data