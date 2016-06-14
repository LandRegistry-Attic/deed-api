import json
from flask import Flask, request, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from application.service_clients.esec import make_esec_client
import os
import logging
from logger import logging_config

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


@app.errorhandler(Exception)
def unhandled_exception(e):
    app.logger.error('Unhandled Exception: %s', (e,), exc_info=True)
    return jsonify({"message": "Unexpected error."}), 500
