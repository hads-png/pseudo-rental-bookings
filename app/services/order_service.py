from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any
from sqlalchemy import select
from app.extensions import db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product


ALLOWED_TRANSITIONS = {
    'draft': ['confirmed', 'cancelled'],
    'confirmed': ['picked_up', 'cancelled'],
    'picked_up': ['returned'],
    'returned': [],
    'cancelled': []
}


def calculate_rental_days(start_date: date, end_date: date) -> int:
    """Calculates inclusive rental days (min 1)."""
    if not start_date or not end_date:
        return 1
    if end_date < start_date:
        return 1
    return max(1, (end_date - start_date).days + 1)


def calculate_line_total(quantity: int, daily_rate: Decimal | float | str, num_days: int) -> Decimal:
    """Calculates line item total with decimal precision."""
    qty_dec = Decimal(str(quantity))
    rate_dec = Decimal(str(daily_rate))
    days_dec = Decimal(str(num_days))
    return (qty_dec * rate_dec * days_dec).quantize(Decimal('0.01'))


def calculate_order_totals(order: Order) -> None:
    """Recalculates subtotals, tax, and total on an Order instance in-place."""
    rental_days = calculate_rental_days(order.rental_start, order.rental_end)
    
    subtotal = Decimal('0.00')
    for item in order.order_items:
        item.line_total = calculate_line_total(item.quantity, item.daily_rate, rental_days)
        subtotal += item.line_total
        
    order.subtotal = subtotal.quantize(Decimal('0.01'))
    
    discount = Decimal(str(order.discount or 0)).quantize(Decimal('0.01'))
    tax_rate = Decimal(str(order.tax_rate or 0))
    
    taxable_base = max(Decimal('0.00'), order.subtotal - discount)
    tax_amount = (taxable_base * tax_rate).quantize(Decimal('0.01'))
    
    order.total = (taxable_base + tax_amount).quantize(Decimal('0.01'))


def generate_order_number(target_date: date | None = None) -> str:
    """Generates unique sequential order number in format ORD-YYYYMMDD-XXX."""
    if target_date is None:
        target_date = date.today()
    
    date_str = target_date.strftime('%Y%m%d')
    prefix = f"ORD-{date_str}-"
    
    # Query highest sequence for the day
    existing_numbers = db.session.scalars(
        select(Order.order_number).where(Order.order_number.like(f"{prefix}%"))
    ).all()
    
    highest_seq = 0
    for num in existing_numbers:
        try:
            seq_part = int(num.split('-')[-1])
            if seq_part > highest_seq:
                highest_seq = seq_part
        except (ValueError, IndexError):
            continue
            
    new_seq = highest_seq + 1
    return f"{prefix}{new_seq:03d}"


def validate_status_transition(current_status: str, new_status: str) -> bool:
    """Validates if status transition is allowed."""
    allowed = ALLOWED_TRANSITIONS.get(current_status, [])
    return new_status in allowed


def create_order(
    customer_id: int,
    rental_start: date,
    rental_end: date,
    items_data: list[dict[str, Any]],
    discount: Decimal = Decimal('0.00'),
    tax_rate: Decimal = Decimal('0.0000'),
    notes: str | None = None
) -> Order:
    """Creates a new order with snapshotted item rates and computed totals."""
    try:
        order_number = generate_order_number(rental_start)
        
        order = Order(
            order_number=order_number,
            customer_id=customer_id,
            status='draft',
            rental_start=rental_start,
            rental_end=rental_end,
            discount=discount,
            tax_rate=tax_rate,
            notes=notes
        )
        db.session.add(order)
        
        rental_days = calculate_rental_days(rental_start, rental_end)
        
        for item in items_data:
            product_id = item['product_id']
            quantity = int(item['quantity'])
            
            product = db.session.get(Product, product_id)
            if not product:
                raise ValueError(f"Product ID {product_id} not found.")
                
            daily_rate = Decimal(str(product.daily_rate))
            line_total = calculate_line_total(quantity, daily_rate, rental_days)
            
            order_item = OrderItem(
                product_id=product_id,
                quantity=quantity,
                daily_rate=daily_rate,
                line_total=line_total
            )
            order.order_items.append(order_item)
            
        calculate_order_totals(order)
        db.session.commit()
        return order
    except Exception:
        db.session.rollback()
        raise


def update_order(
    order: Order,
    customer_id: int,
    rental_start: date,
    rental_end: date,
    items_data: list[dict[str, Any]],
    discount: Decimal = Decimal('0.00'),
    tax_rate: Decimal = Decimal('0.0000'),
    notes: str | None = None
) -> Order:
    """Updates existing draft or confirmed order."""
    if order.status not in ('draft', 'confirmed'):
        raise ValueError(f"Cannot edit order #{order.order_number} in status '{order.status}'.")
        
    try:
        order.customer_id = customer_id
        order.rental_start = rental_start
        order.rental_end = rental_end
        order.discount = discount
        order.tax_rate = tax_rate
        order.notes = notes
        
        order.order_items.clear()
        rental_days = calculate_rental_days(rental_start, rental_end)
        
        for item in items_data:
            product_id = item['product_id']
            quantity = int(item['quantity'])
            
            product = db.session.get(Product, product_id)
            if not product:
                raise ValueError(f"Product ID {product_id} not found.")
                
            daily_rate = Decimal(str(product.daily_rate))
            line_total = calculate_line_total(quantity, daily_rate, rental_days)
            
            order_item = OrderItem(
                product_id=product_id,
                quantity=quantity,
                daily_rate=daily_rate,
                line_total=line_total
            )
            order.order_items.append(order_item)
            
        calculate_order_totals(order)
        db.session.commit()
        return order
    except Exception:
        db.session.rollback()
        raise


def update_order_status(order: Order, new_status: str) -> tuple[bool, str]:
    """Transitions order status if allowed."""
    if not validate_status_transition(order.status, new_status):
        return False, f"Transition from '{order.status}' to '{new_status}' is not allowed."
        
    try:
        order.status = new_status
        db.session.commit()
        return True, f"Order status updated to '{new_status}'."
    except Exception as e:
        db.session.rollback()
        return False, f"Error updating status: {str(e)}"
