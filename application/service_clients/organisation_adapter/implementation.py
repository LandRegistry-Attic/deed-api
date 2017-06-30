from functools import reduce
import json
from urllib.parse import urljoin
from application import config
from flask import g
import application


def get_organisation_name(organisation_name):

    # Connect to organisation-api and get the name for the id provided
    application.app.logger.info("Calling get-organisation-name...")
    request_url = reduce(urljoin, [config.ORGANISATION_API_BASE_HOST,
                                   'organisation-name/', organisation_name])

    # Collect the organisation name and return it
    new_organisation_name = _get_request(request_url)

    if new_organisation_name == "not found":
        # Use the organisation name with brackets
        return organisation_name
    else:
        # If an organisation is found, return it
        return new_organisation_name


def _get_request(request_url):
    json_response = json.loads(g.requests.get(request_url).text)
    new_organisation_name = json_response["organisation_name"]
    application.app.logger.debug("Response get_organisation_name: '%s'", new_organisation_name)
    return new_organisation_name


def check_health():
    service_response = g.requests.get(config.ORGANISATION_API_BASE_HOST + '/health/service-check')
    return service_response
