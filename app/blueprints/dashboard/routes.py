from datetime import date, timedelta
from flask import render_template
from flask_login import login_required
from sqlalchemy import func, select, extract
from app.blueprints.dashboard import dashboard_bp
from app.extensions import db
from app.models.product import Product
from app.models.customer import Customer
from app.models.order import Order
from app.models.order_item import OrderItem


@dashboard_bp.route('/')
@login_required
def index():
    """Dashboard homepage with real-time business metrics, recent orders, and analytics."""
    today = date.today()

    # 1. Summary Cards Data
    active_orders_count = db.session.scalar(
        select(func.count(Order.id)).where(Order.status.in_(['confirmed', 'picked_up']))
    ) or 0

    customer_count = db.session.scalar(
        select(func.count(Customer.id))
    ) or 0

    product_count = db.session.scalar(
        select(func.count(Product.id)).where(Product.is_active == True)
    ) or 0

    monthly_revenue = db.session.scalar(
        select(func.coalesce(func.sum(Order.total), 0)).where(
            extract('year', Order.rental_start) == today.year,
            extract('month', Order.rental_start) == today.month,
            Order.status != 'cancelled'
        )
    ) or 0.0

    # 2. Recent Orders (Last 5)
    recent_orders = db.session.scalars(
        select(Order).order_by(Order.created_at.desc()).limit(5)
    ).all()

    # 3. Orders by Status Breakdown
    status_counts_raw = db.session.execute(
        select(Order.status, func.count(Order.id)).group_by(Order.status)
    ).all()
    orders_by_status = {s: count for s, count in status_counts_raw}

    # 4. Top 5 Products in Last 30 Days
    thirty_days_ago = today - timedelta(days=30)
    top_products_raw = db.session.execute(
        select(Product, func.sum(OrderItem.quantity).label('total_rented'))
        .join(OrderItem, Product.id == OrderItem.product_id)
        .join(Order, OrderItem.order_id == Order.id)
        .where(
            Order.rental_start >= thirty_days_ago,
            Order.status != 'cancelled',
            Product.is_active == True
        )
        .group_by(Product.id)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(5)
    ).all()

    top_products = [
        {'product': p, 'total_rented': rented}
        for p, rented in top_products_raw
    ]

    return render_template(
        'dashboard/index.html',
        active_orders_count=active_orders_count,
        customer_count=customer_count,
        product_count=product_count,
        monthly_revenue=float(monthly_revenue),
        recent_orders=recent_orders,
        orders_by_status=orders_by_status,
        top_products=top_products
    )

