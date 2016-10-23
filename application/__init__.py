import json
from builtins import FileNotFoundError
from flask import Flask, request, jsonify
from flask.ext.sqlalchemy import SQLAlchemy

from application.service_clients.esec import make_esec_client
from application.service_clients.esec.implementation import EsecException
from application import config

import os
import logging
from logger import logging_config

import requests

logging_config.setup_logging()
LOGGER = logging.getLogger(__name__)

LOGGER.info("Starting the server")


app = Flask(__name__, static_folder='static')

db = SQLAlchemy(app)

from .borrower.model import DatabaseException  # noqa

esec_client = make_esec_client()

# Register routes after establishing the db prevents improperly loaded modules
# caused from circular imports
from .deed.views import deed_bp  # noqa
from .borrower.views import borrower_bp  # noqa
from .casework.views import casework_bp  # noqa

app.config.from_pyfile("config.py")
app.register_blueprint(deed_bp, url_prefix='/deed')
app.register_blueprint(borrower_bp, url_prefix='/borrower')
app.register_blueprint(casework_bp, url_prefix='/casework')
app.url_map.strict_slashes = False


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.route("/health")
def check_status():

    return json.dumps({
        "Status": "OK",
        "headers": str(request.headers),
        "commit": str(os.getenv("COMMIT", "LOCAL"))
    })


@app.route("/health/service-check")
def service_check_routes():

    service_list = ''

    # Test the deeds database; try and connect to it and retrieve the version value
    try:
        # Attempt to retrieve the value of the alembic version
        # from the relevant deed_api table
        result = db.engine.execute("SELECT version_num FROM alembic_version;")

        rowResults = []

        for row in result:
            rowResults.append(row[0])

        # If the above statement passes, we can assume that a connection
        # to the database has been established.
        # If an exception occurs whilst retrieving the result, then the service
        # will not reach this point.
        service_list = {
            "services":
            [
                get_service_check_json(200, "deed-api", "postgres deeds (db)",
                                       "Connected successfully", rowResults[0])
            ]
        }

    except Exception as e:
        # If we have found an exception, then we can presume the connection to the database did not work
        app.logger.error('Database Exception: %s', (e,), exc_info=True)

        service_list = {
            "services":
            [
                get_service_check_json(500, "deed-api", "postgres deeds (db)",
                                       "A database exception has occured")
            ]
        }

    # Attempt to connect to the esec client and append the result to the service list
    esec_service_json = get_service_check_response(config.ESEC_CLIENT_BASE_HOST, "deed-api", "esec-client")
    service_list['services'].append(esec_service_json)

    # Attempt to connect to the title adapter (stub(local) or api(live))
    # and add the two results to the service list
    try:
        title_service_json = get_service_check_response(config.TITLE_ADAPTOR_BASE_HOST, "deed-api", "title adapter stub/api")
        if len(title_service_json) == 2:
            # For 200 success: two services
            service_list['services'].append(title_service_json[0])
            service_list['services'].append(title_service_json[1])
        else:
            # If there is an error response
            service_list['services'].append(title_service_json)
    except IndexError as e:
        serviceIndexError = get_service_check_json(500, "deed-api", "title adapter stub/api",
                                                   "The response has triggered an index exception")
        service_list['services'].append(serviceIndexError)
        app.logger.error('Index Error: %s', (e,), exc_info=True)

    return json.dumps(service_list)


def get_service_check_response(env_uri, service_from, service_to):

    # Attempt to connect to a specific service
    service_response = ""
    status_code = 500
    service_json = ""

    try:
        # Retrieve the string response from external services; the titial adapter api/stub/ and esec
        # responses from these services are in strings to avoid java/python JSONObject differences
        service_response = requests.get(env_uri + '/health/service-check')

        # Change the string into a json format
        status_code = service_response.status_code
        service_json = json.loads(service_response.text)

    except (requests.exceptions.RequestException, ValueError, TypeError) as e:
        # A RequestException resolves the error that occurs when a connection cant be established
        # and the ValueError/TypeError exception may occur if the json string / object is malformed
        status_code = 500
        app.logger.error('A Request or ValueError exception has occurred in get_service_check_response: %s', (e,), exc_info=True)

    if status_code != 200:
        # We either have a differing status code, add an error for this service
        # This would imply that we were not able to connect to the esec-client
        service_json = get_service_check_json(status_code, service_from, service_to,
                                              "Error: Could not connect")

    return service_json


def get_service_check_json(status_code, service_from, service_to, service_message, service_alembic_version=""):

    service_json = {"service_message": "default response"}

    if service_alembic_version == "":
        service_json = {
            "status_code": status_code,
            "service_from": service_from,
            "service_to": service_to,
            "service_message": service_message
        }
    else:
        service_json = {
            "status_code": status_code,
            "service_from": service_from,
            "service_to": service_to,
            "service_message": service_message,
            "service_alembic_version": service_alembic_version
        }

    return service_json


@app.errorhandler(EsecException)
def esecurity_error(e):
    app.logger.error('ESecurity has raised an Exception: %s', (e,), exc_info=True)
    return "", 200


@app.errorhandler(FileNotFoundError)
def not_found_exception(e):
    app.logger.error('Not found error: %s', (e,), exc_info=True)
    return jsonify({"message": "Deed not found"}), 404


@app.errorhandler(Exception)
def unhandled_exception(e):
    app.logger.error('Unhandled Exception: %s', (e,), exc_info=True)
    return jsonify({"message": "Unexpected error."}), 500


@app.errorhandler(DatabaseException)
def database_exception(e):
    app.logger.error('Database Exception: %s', (e,), exc_info=True)
    return jsonify({"message": "Database Error."}), 500
