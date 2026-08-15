from datetime import datetime
from flask import request, jsonify
from flask_login import login_required
from app.blueprints.api import api_bp
from app.services.availability import get_available_quantity, get_booked_quantity
from app.models.product import Product
from app.models.order import Order
from app.extensions import db



@api_bp.route('/availability', methods=['GET'])
@login_required
def check_availability():
    """
    JSON API endpoint for checking product availability.
    Params: product_id (int), start (YYYY-MM-DD), end (YYYY-MM-DD), exclude_order_id (int, optional)
    """
    product_id = request.args.get('product_id', type=int)
    start_str = request.args.get('start', type=str)
    end_str = request.args.get('end', type=str)
    exclude_order_id = request.args.get('exclude_order_id', type=int)

    if not product_id or not start_str or not end_str:
        return jsonify({'error': 'Missing required query parameters: product_id, start, end'}), 400

    try:
        start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Expected YYYY-MM-DD'}), 400

    if end_date < start_date:
        return jsonify({'error': 'End date must be on or after start date'}), 400

    product = db.session.get(Product, product_id)
    if not product or not product.is_active:
        return jsonify({'error': 'Product not found or inactive'}), 404

    available = get_available_quantity(
        product_id=product_id,
        start_date=start_date,
        end_date=end_date,
        exclude_order_id=exclude_order_id
    )
    booked = get_booked_quantity(
        product_id=product_id,
        start_date=start_date,
        end_date=end_date,
        exclude_order_id=exclude_order_id
    )

    return jsonify({
        'product_id': product_id,
        'total_stock': product.total_stock,
        'booked': booked,
        'available': available
    })


@api_bp.route('/dashboard/revenue', methods=['GET'])
@login_required
def get_revenue_chart_data():
    """Return 6-month monthly revenue data for Chart.js dashboard chart."""
    today = datetime.now().date()
    months = []

    for i in range(5, -1, -1):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1
        months.append((y, m))

    labels = []
    data = []

    for y, m in months:
        dt = datetime(y, m, 1)
        month_label = dt.strftime('%b %Y')
        rev = db.session.scalar(
            db.select(db.func.coalesce(db.func.sum(Order.total), 0)).where(
                db.extract('year', Order.rental_start) == y,
                db.extract('month', Order.rental_start) == m,
                Order.status != 'cancelled'
            )
        ) or 0.0
        labels.append(month_label)
        data.append(float(rev))

    return jsonify({'labels': labels, 'data': data})

