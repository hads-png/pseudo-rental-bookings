from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.blueprints.customers import customers_bp
from app.blueprints.customers.forms import CustomerForm
from app.extensions import db
from app.models.customer import Customer
from app.services.customer_service import create_customer, update_customer, delete_customer


@customers_bp.route('/')
@login_required
def index():
    """List customers with search and pagination (10 per page)."""
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '', type=str).strip()

    query = Customer.query

    if q:
        full_name_concat = db.func.concat(Customer.first_name, ' ', Customer.last_name)
        query = query.filter(
            Customer.first_name.ilike(f"%{q}%") |
            Customer.last_name.ilike(f"%{q}%") |
            Customer.email.ilike(f"%{q}%") |
            full_name_concat.ilike(f"%{q}%")
        )

    query = query.order_by(Customer.created_at.desc())
    pagination = query.paginate(page=page, per_page=10, error_out=False)

    return render_template(
        'customers/list.html',
        customers=pagination.items,
        pagination=pagination,
        q=q
    )


@customers_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new customer."""
    form = CustomerForm()

    if form.validate_on_submit():
        try:
            customer = create_customer(form.data)
            flash(f"Customer '{customer.full_name}' created successfully.", 'success')
            return redirect(url_for('customers.index'))
        except Exception:
            flash('An error occurred while creating the customer. Please try again.', 'danger')

    return render_template('customers/form.html', form=form, customer=None)


@customers_bp.route('/<int:id>')
@login_required
def detail(id):
    """Show customer detail page with order history section."""
    customer = db.session.get(Customer, id)
    if not customer:
        from flask import abort
        abort(404)
    return render_template('customers/detail.html', customer=customer)


@customers_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit an existing customer."""
    customer = db.session.get(Customer, id)
    if not customer:
        from flask import abort
        abort(404)
    form = CustomerForm(obj=customer, customer_id=customer.id)

    if form.validate_on_submit():
        try:
            update_customer(customer, form.data)
            flash(f"Customer '{customer.full_name}' updated successfully.", 'success')
            return redirect(url_for('customers.detail', id=customer.id))
        except Exception:
            flash('An error occurred while updating the customer. Please try again.', 'danger')

    return render_template('customers/form.html', form=form, customer=customer)


@customers_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Hard-delete customer if zero orders exist; else flash error."""
    customer = db.session.get(Customer, id)
    if not customer:
        from flask import abort
        abort(404)
    success, message = delete_customer(customer)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')

    return redirect(url_for('customers.index'))
