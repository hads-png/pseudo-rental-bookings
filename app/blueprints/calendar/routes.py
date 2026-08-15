from datetime import date, datetime, timedelta
from flask import render_template, request
from flask_login import login_required
from sqlalchemy import select, and_

from app.extensions import db
from app.blueprints.calendar import calendar_bp
from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem


@calendar_bp.route('/')
@login_required
def index():
    """Global Availability Calendar.
    
    Rows: Products
    Cols: Next 14 days
    Cells: Available stock / Total stock, plus list of active Order IDs if booked.
    """
    start_date_str = request.args.get('start_date')
    if start_date_str:
        try:
            current_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            current_date = date.today()
    else:
        current_date = date.today()

    num_days = 14
    dates = [current_date + timedelta(days=i) for i in range(num_days)]
    
    products = db.session.scalars(
        select(Product).where(Product.is_active == True).order_by(Product.name)
    ).all()
    
    # Pre-fetch orders that overlap with this 14-day window to avoid N+1 queries.
    window_start = datetime.combine(dates[0], datetime.min.time())
    window_end = datetime.combine(dates[-1], datetime.max.time())
    
    # We want orders that are confirmed or picked_up.
    active_orders = db.session.scalars(
        select(Order).where(
            Order.status.in_(['confirmed', 'picked_up']),
            Order.rental_start <= window_end,
            Order.rental_end >= window_start
        )
    ).all()
    
    # Map product_id -> date -> [orders]
    # And we'll calculate available stock on the fly.
    calendar_data = []
    for p in products:
        row = {
            'product': p,
            'days': []
        }
        for d in dates:
            d_start = datetime.combine(d, datetime.min.time())
            d_end = datetime.combine(d, datetime.max.time())
            
            # Find orders overlapping this day that contain this product
            day_orders = []
            booked_qty = 0
            for o in active_orders:
                if o.rental_start <= d_end and o.rental_end >= d_start:
                    for item in o.order_items:
                        if item.product_id == p.id:
                            day_orders.append(o)
                            booked_qty += item.quantity
                            
            row['days'].append({
                'date': d,
                'available': p.total_stock - booked_qty,
                'booked': booked_qty,
                'total': p.total_stock,
                'orders': day_orders
            })
        calendar_data.append(row)
        
    return render_template(
        'calendar/index.html',
        dates=dates,
        calendar_data=calendar_data,
        current_date=current_date,
        prev_date=current_date - timedelta(days=14),
        next_date=current_date + timedelta(days=14)
    )
