from flask import render_template, redirect, url_for, abort
from flask_login import login_required
from app.blueprints.invoices import invoices_bp
from app.models.order import Order
from app.services.order_service import calculate_rental_days
from app.extensions import db


from app.models.settings import Settings


@invoices_bp.route('/')
@login_required
def index():
    """Redirect sidebar invoices link to orders list."""
    return redirect(url_for('orders.index'))


@invoices_bp.route('/<int:id>')
@login_required
def detail(id):
    """Render printable invoice page via invoices blueprint."""
    order = db.session.get(Order, id)
    if not order:
        abort(404)

    settings = Settings.get_settings()
    rental_days = calculate_rental_days(order.rental_start, order.rental_end)
    return render_template('invoices/detail.html', order=order, rental_days=rental_days, settings=settings)

