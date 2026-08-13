from flask import render_template
from flask_login import login_required
from app.blueprints.invoices import invoices_bp


@invoices_bp.route('/')
@login_required
def index():
    return render_template('dashboard/index.html', info_message="Invoices module will be fully active in Phase 6.")
