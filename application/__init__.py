import json
from flask import Flask, request
from flask.ext.sqlalchemy import SQLAlchemy
import os

app = Flask(__name__, static_folder ='static')
db = SQLAlchemy(app)

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
