from flask import send_from_directory
from application import app


def get_oc2():
    resp = send_from_directory(app.static_folder,"oc2.pdf", as_attachment=False)
    return resp