from flask import Flask
from .helloworld.views import helloworld
import os

app = Flask(__name__)

app.config.from_object(os.environ.get('SETTINGS'))
app.register_blueprint(helloworld, url_prefix='/helloworld')

@app.route("/health")
def check_status():
    return "Status OK"
