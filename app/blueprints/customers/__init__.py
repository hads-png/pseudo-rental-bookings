from flask import Blueprint, render_template
from flask_login import login_required

customers_bp = Blueprint('customers', __name__, url_prefix='/customers')


@customers_bp.route('/')
@login_required
def index():
    return render_template('dashboard/index.html', info_message="Customers module will be fully active in Phase 3.")
