from flask import render_template
from flask_login import login_required, current_user
from app.blueprints.dashboard import dashboard_bp
from app.models.product import Product
from app.models.customer import Customer
from app.models.order import Order


@dashboard_bp.route('/')
@login_required
def index():
    # Phase 1: Provide high level counts and welcome
    product_count = Product.query.count()
    customer_count = Customer.query.count()
    order_count = Order.query.count()
    
    return render_template(
        'dashboard/index.html',
        product_count=product_count,
        customer_count=customer_count,
        order_count=order_count
    )
