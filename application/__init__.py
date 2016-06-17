import json
from flask import Flask, request, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from application.service_clients.esec import make_esec_client
from application.service_clients.esec.implementation import EsecDownException
import os
import logging
from logger import logging_config
from flask import jsonify

logging_config.setup_logging()
LOGGER = logging.getLogger(__name__)

LOGGER.info("Starting the server")


app = Flask(__name__, static_folder='static')
db = SQLAlchemy(app)
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


@app.route("/div_zero")
def div_zero():
    app.logger.debug("div_zero")
    1/0


@app.errorhandler(EsecDownException)
def esecurity_error(e):
    app.logger.error('ESecurity is Down: %s', (e,), exc_info=True)
    return jsonify({"message": "Make Effective Successful"}), 200


@app.errorhandler(Exception)
def unhandled_exception(e):
    app.logger.error('Unhandled Exception: %s', (e,), exc_info=True)
    return jsonify({"message": "Unexpected error."}), 500
