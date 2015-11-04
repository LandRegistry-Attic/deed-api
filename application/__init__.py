from flask import Flask
from .deed.views import deed
import os

app = Flask(__name__)

app.config.from_object(os.environ.get('SETTINGS'))
app.register_blueprint(deed, url_prefix='/deed')


@app.route("/health")
def check_status():
    return "Status OK"
