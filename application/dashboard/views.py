from flask import Blueprint
from flask import request, abort, jsonify, Response

dashboard_bp = Blueprint('dashboard', __name__,
                    template_folder='templates',
                    static_folder='static')

@dashboard_bp.route('/hello', methods=['GET'])
def get_all_deeds():
    return "hello world"
