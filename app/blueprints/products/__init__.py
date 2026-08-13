from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required

products_bp = Blueprint('products', __name__, url_prefix='/products')


@products_bp.route('/')
@login_required
def index():
    return render_template('dashboard/index.html', info_message="Products module will be fully active in Phase 2.")
