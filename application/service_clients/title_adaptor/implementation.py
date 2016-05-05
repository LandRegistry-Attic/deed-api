import requests
import logging
from application import config


LOGGER = logging.getLogger(__name__)


def perform_check(title):  # pragma: no cover

    resp = requests.post(config.TITLE_ADAPTOR_BASE_HOST + "/" + title)

    LOGGER.info("Making title validator call")

    return resp