from functools import reduce
import requests
import json
import logging
from urllib.parse import urljoin
from application import config

LOGGER = logging.getLogger(__name__)


def get_organisation_name(organisation_id, organisation_name):

    # Connect to organisation-api and get the name for the id provided
    LOGGER.info("Calling get-organisation-name...")
    request_url = reduce(urljoin, [config.ORGANISATION_API_BASE_HOST,
                                   'organisation-name/', organisation_id])

    # Collect the organisation name and return it
    json_response = json.loads(requests.get(request_url).text)
    new_organisation_name = json_response["organisation_name"]
    LOGGER.debug("Response get_organisation_name: '%s'", new_organisation_name)

    if new_organisation_name == "not found":
        # Use the organisation name with brackets
        return organisation_name
    else:
        # If an organisation is found, return it
        return new_organisation_name


def check_health():
    service_response = requests.get(config.ORGANISATION_API_BASE_HOST + '/health/service-check')
    return service_response
