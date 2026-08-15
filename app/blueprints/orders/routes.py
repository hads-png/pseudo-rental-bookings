from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required
from sqlalchemy import select
from app.blueprints.orders import orders_bp
from app.blueprints.orders.forms import OrderForm
from app.extensions import db
from app.models.customer import Customer
from app.models.product import Product
from app.models.order import Order
from app.services.order_service import (
    create_order,
    update_order,
    update_order_status,
    calculate_duration_hours
)
from app.services.availability import check_availability


def _get_customer_choices() -> list[tuple[int, str]]:
    customers = db.session.scalars(
        select(Customer).order_by(Customer.first_name, Customer.last_name)
    ).all()
    return [(c.id, f"{c.full_name} ({c.email})") for c in customers]


def _get_product_choices() -> list[tuple[int, str]]:
    products = db.session.scalars(
        select(Product).where(Product.is_active == True).order_by(Product.name)
    ).all()
    return [(p.id, f"{p.name} (${p.daily_rate:.2f}/day)") for p in products]


@orders_bp.route('/')
@login_required
def index():
    """List orders with status, keyword search, date range filters, and pagination."""
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '', type=str).strip()
    status = request.args.get('status', '', type=str).strip()
    start_date_str = request.args.get('start_date', '', type=str).strip()
    end_date_str = request.args.get('end_date', '', type=str).strip()

    query = db.select(Order).join(Customer)

    if q:
        full_name_concat = db.func.concat(Customer.first_name, ' ', Customer.last_name)
        query = query.where(
            Order.order_number.ilike(f"%{q}%") |
            Customer.first_name.ilike(f"%{q}%") |
            Customer.last_name.ilike(f"%{q}%") |
            full_name_concat.ilike(f"%{q}%")
        )

    if status:
        query = query.where(Order.status == status)

    if start_date_str:
        try:
            start_d = datetime.strptime(start_date_str, '%Y-%m-%d')
            query = query.where(Order.rental_start >= start_d)
        except ValueError:
            pass

    if end_date_str:
        try:
            end_d = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query = query.where(Order.rental_end <= end_d)
        except ValueError:
            pass

    query = query.order_by(Order.created_at.desc())
    pagination = db.paginate(query, page=page, per_page=10, error_out=False)

    return render_template(
        'orders/list.html',
        orders=pagination.items,
        pagination=pagination,
        q=q,
        status=status,
        start_date=start_date_str,
        end_date=end_date_str
    )


@orders_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new order."""
    form = OrderForm()
    customer_choices = _get_customer_choices()
    product_choices = _get_product_choices()

    form.customer_id.choices = customer_choices

    if request.method == 'GET':
        if not form.items.entries:
            form.items.append_entry()
            
    for entry in form.items:
        entry.product_id.choices = product_choices

    if form.validate_on_submit():
        items_data = [
            {'product_id': item.product_id.data, 'quantity': item.quantity.data}
            for item in form.items
        ]
        avail_errors = check_availability(
            items=items_data,
            start_date=form.rental_start.data,
            end_date=form.rental_end.data
        )
        if avail_errors:
            for err in avail_errors:
                flash(err, 'danger')
        else:
            try:
                order = create_order(
                    customer_id=form.customer_id.data,
                    rental_start=form.rental_start.data,
                    rental_end=form.rental_end.data,
                    items_data=items_data,
                    discount=form.discount.data or 0,
                    tax_rate=form.tax_rate.data or 0,
                    notes=form.notes.data
                )
                flash(f"Order #{order.order_number} created successfully.", 'success')
                return redirect(url_for('orders.detail', id=order.id))
            except ValueError as ve:
                flash(str(ve), 'danger')
            except Exception:
                flash("An error occurred while creating the order. Please check inputs and try again.", 'danger')

    return render_template('orders/form.html', form=form, order=None, product_choices=product_choices)


@orders_bp.route('/<int:id>')
@login_required
def detail(id):
    """Show order detail invoice view with status action controls."""
    order = db.session.get(Order, id)
    if not order:
        abort(404)

    duration_hours = calculate_duration_hours(order.rental_start, order.rental_end)
    return render_template('orders/detail.html', order=order, duration_hours=duration_hours)


@orders_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit an existing order (draft or confirmed only)."""
    order = db.session.get(Order, id)
    if not order:
        abort(404)

    if order.status not in ('draft', 'confirmed'):
        flash(f"Cannot edit order #{order.order_number} because it is in '{order.status}' status.", 'danger')
        return redirect(url_for('orders.detail', id=order.id))

    customer_choices = _get_customer_choices()
    product_choices = _get_product_choices()

    if request.method == 'GET':
        form = OrderForm(obj=order)
        form.items.entries = []
        for item in order.order_items:
            form.items.append_entry({'product_id': item.product_id, 'quantity': item.quantity})
    else:
        form = OrderForm()

    form.customer_id.choices = customer_choices
    for entry in form.items:
        entry.product_id.choices = product_choices

    if form.validate_on_submit():
        items_data = [
            {'product_id': item.product_id.data, 'quantity': item.quantity.data}
            for item in form.items
        ]
        avail_errors = check_availability(
            items=items_data,
            start_date=form.rental_start.data,
            end_date=form.rental_end.data,
            exclude_order_id=order.id
        )
        if avail_errors:
            for err in avail_errors:
                flash(err, 'danger')
        else:
            try:
                updated_order = update_order(
                    order=order,
                    customer_id=form.customer_id.data,
                    rental_start=form.rental_start.data,
                    rental_end=form.rental_end.data,
                    items_data=items_data,
                    discount=form.discount.data or 0,
                    tax_rate=form.tax_rate.data or 0,
                    notes=form.notes.data
                )
                flash(f"Order #{updated_order.order_number} updated successfully.", 'success')
                return redirect(url_for('orders.detail', id=updated_order.id))
            except ValueError as ve:
                flash(str(ve), 'danger')
            except Exception:
                flash("An error occurred while updating the order. Please try again.", 'danger')

    return render_template('orders/form.html', form=form, order=order, product_choices=product_choices)


@orders_bp.route('/<int:id>/status', methods=['POST'])
@login_required
def change_status(id):
    """Change order status."""
    order = db.session.get(Order, id)
    if not order:
        abort(404)

    new_status = request.form.get('status')
    if not new_status:
        flash("No target status provided.", 'danger')
        return redirect(url_for('orders.detail', id=order.id))

    success, message = update_order_status(order, new_status)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('orders.detail', id=order.id))


@orders_bp.route('/<int:id>/cancel', methods=['POST'])
@login_required
def cancel(id):
    """Cancel an order."""
    order = db.session.get(Order, id)
    if not order:
        abort(404)

    success, message = update_order_status(order, 'cancelled')
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('orders.detail', id=order.id))


@orders_bp.route('/<int:id>/invoice')
@login_required
def invoice(id):
    """Render printable invoice page for an order."""
    order = db.session.get(Order, id)
    if not order:
        abort(404)

    duration_hours = calculate_duration_hours(order.rental_start, order.rental_end)
    return render_template('invoices/detail.html', order=order, duration_hours=duration_hours)


@orders_bp.route('/<int:id>/payment', methods=['POST'])
@login_required
def record_payment(id):
    """Record a payment towards an order and update payment_status."""
    order = db.session.get(Order, id)
    if not order:
        abort(404)

    try:
        amount = float(request.form.get('amount', 0))
    except (ValueError, TypeError):
        flash("Invalid payment amount.", 'danger')
        return redirect(url_for('orders.detail', id=order.id))

    if amount <= 0:
        flash("Payment amount must be greater than zero.", 'danger')
        return redirect(url_for('orders.detail', id=order.id))

    current_paid = float(order.amount_paid or 0)
    new_paid = current_paid + amount
    order.amount_paid = new_paid

    order_total = float(order.total or 0)
    if new_paid >= order_total:
        order.payment_status = 'paid'
    elif new_paid > 0:
        order.payment_status = 'partially_paid'
    else:
        order.payment_status = 'unpaid'

    try:
        db.session.commit()
        flash(f"Payment of ${amount:.2f} recorded for order #{order.order_number}.", 'success')
    except Exception:
        db.session.rollback()
        flash("Failed to record payment. Please try again.", 'danger')

    return redirect(url_for('orders.detail', id=order.id))

