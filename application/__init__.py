from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from .deed.views import deed

app = Flask(__name__)
db = SQLAlchemy(app)

app.config.from_pyfile("config.py")
app.register_blueprint(deed, url_prefix='/deed')


@app.route("/health")
def check_status():
    return "Status OK"
