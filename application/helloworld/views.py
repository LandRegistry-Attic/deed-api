
from flask import Blueprint, render_template

helloworld = Blueprint('helloworld', __name__,
                    template_folder='templates',
                    static_folder='static')

@helloworld.route('/')
def homemain():
    return render_template('hello.html')
