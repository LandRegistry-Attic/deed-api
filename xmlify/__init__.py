from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import json


app = Flask(__name__)
db = SQLAlchemy(app)

# Register routes after establishing the db prevents improperly loaded modules
# caused from circular imports
from .deed.views import deed_bp
app.config.from_pyfile("config.py")
app.register_blueprint(deed_bp, url_prefix='/deed')


@app.route("/health")
def check_status():
    return json.dumps({"Status": "OK"})
