from flask import render_template
from flask_login import login_required
from app.blueprints.orders import orders_bp


@orders_bp.route('/')
@login_required
def index():
    return render_template('dashboard/index.html', info_message="Orders module will be fully active in Phase 4.")
