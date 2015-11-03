
from flask import Blueprint

deed = Blueprint('deed', __name__,
                    template_folder='templates',
                    static_folder='static')

@helloworld.route('/')
def deedmain():
    return "deed route"
