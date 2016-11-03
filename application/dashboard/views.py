from flask import Blueprint
from application.deed.model import Deed

dashboard_bp = Blueprint('dashboard', __name__,
                         template_folder='templates',
                         static_folder='static')


@dashboard_bp.route('/<status>', methods=['GET'])
def get_deeds_by_status(status):
    deed = Deed()
    result = deed.get_deeds_by_status(status)
    return str(result)
