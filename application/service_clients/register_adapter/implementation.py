from functools import reduce
import requests
import json
import logging
from urllib.parse import urljoin


from application import config


LOGGER = logging.getLogger(__name__)


def get_proprietor_names(title_number):
    LOGGER.info("Calling get-proprietor-names...")
    request_url = reduce(urljoin, [config.DM_REGISTER_ADAPTER, 'get-proprietor-names/', title_number])
    txt = requests.get(request_url).text
    LOGGER.debug("Response: '%s'", txt)
    return json.loads(txt).get('proprietor_names')


def check_health():
    service_response = requests.get(config.DM_REGISTER_ADAPTER + '/health/service-check')

    return service_response
