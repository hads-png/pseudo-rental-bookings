from flask import Blueprint, render_template
from flask_login import login_required

invoices_bp = Blueprint('invoices', __name__, url_prefix='/invoices')


@invoices_bp.route('/')
@login_required
def index():
    return render_template('dashboard/index.html', info_message="Invoices module will be fully active in Phase 6.")
