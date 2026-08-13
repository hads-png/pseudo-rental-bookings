from flask import render_template
from flask_login import login_required
from app.blueprints.customers import customers_bp


@customers_bp.route('/')
@login_required
def index():
    return render_template('dashboard/index.html', info_message="Customers module will be fully active in Phase 3.")
