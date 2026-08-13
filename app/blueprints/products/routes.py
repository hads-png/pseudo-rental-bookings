from flask import render_template
from flask_login import login_required
from app.blueprints.products import products_bp


@products_bp.route('/')
@login_required
def index():
    return render_template('dashboard/index.html', info_message="Products module will be fully active in Phase 2.")
