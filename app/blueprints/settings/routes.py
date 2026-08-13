from flask import render_template
from flask_login import login_required
from app.blueprints.settings import settings_bp


@settings_bp.route('/')
@login_required
def index():
    return render_template('dashboard/index.html', info_message="Settings module will be fully active in Phase 8.")
