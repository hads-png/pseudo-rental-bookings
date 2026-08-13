from flask import Blueprint, render_template
from flask_login import login_required

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')


@orders_bp.route('/')
@login_required
def index():
    return render_template('dashboard/index.html', info_message="Orders module will be fully active in Phase 4.")
