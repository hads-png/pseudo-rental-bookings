import math
from datetime import datetime, date
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


def calculate_duration_hours(start_time: datetime, end_time: datetime) -> int:
    """Calculates inclusive rental duration in hours (min 0)."""
    if not start_time or not end_time or end_time <= start_time:
        return 0
    return math.ceil((end_time - start_time).total_seconds() / 3600)

def calculate_item_total(quantity: int, product: Product, start_time: datetime, end_time: datetime) -> Decimal:
    """Calculates the line item total using PricingTiers (greedy algorithm) or falling back to daily rate."""
    duration_hours = calculate_duration_hours(start_time, end_time)
    
    if duration_hours == 0:
        return Decimal('0.00')

    tiers = sorted(product.pricing_tiers, key=lambda t: t.duration_hours, reverse=True)
    
    total_price_for_one_item = Decimal('0.00')
    remaining_hours = duration_hours

    for tier in tiers:
        if tier.duration_hours <= 0:
            continue
        if remaining_hours <= 0:
            break
        num_tiers = remaining_hours // tier.duration_hours
        if num_tiers > 0:
            total_price_for_one_item += Decimal(str(tier.price)) * num_tiers
            remaining_hours %= tier.duration_hours

    # Fallback for remaining hours (charge in 24h blocks using daily_rate)
    if remaining_hours > 0:
        num_days = math.ceil(remaining_hours / 24.0)
        total_price_for_one_item += Decimal(str(product.daily_rate)) * num_days

    qty_dec = Decimal(str(quantity))
    return (qty_dec * total_price_for_one_item).quantize(Decimal('0.01'))


def calculate_order_totals(order: Order) -> None:
    """Recalculates subtotals, tax, and total on an Order instance in-place."""
    subtotal = Decimal('0.00')
    for item in order.order_items:
        subtotal += item.line_total
        
    order.subtotal = subtotal.quantize(Decimal('0.01'))
    
    discount = Decimal(str(order.discount or 0)).quantize(Decimal('0.01'))
    tax_rate = Decimal(str(order.tax_rate or 0))
    
    taxable_base = max(Decimal('0.00'), order.subtotal - discount)
    tax_amount = (taxable_base * tax_rate).quantize(Decimal('0.01'))
    
    order.total = (taxable_base + tax_amount).quantize(Decimal('0.01'))


def generate_order_number(target_time: datetime | None = None) -> str:
    """Generates unique sequential order number in format ORD-YYYYMMDD-XXX."""
    if target_time is None:
        target_time = datetime.now()
    
    date_str = target_time.strftime('%Y%m%d')
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
    rental_start: datetime,
    rental_end: datetime,
    items_data: list[dict[str, Any]],
    discount: Decimal = Decimal('0.00'),
    tax_rate: Decimal = Decimal('0.0000'),
    notes: str | None = None
) -> Order:
    """Creates a new order with calculated item rates and computed totals."""
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
        
        for item in items_data:
            product_id = item['product_id']
            quantity = int(item['quantity'])
            
            product = db.session.get(Product, product_id)
            if not product:
                raise ValueError(f"Product ID {product_id} not found.")
                
            line_total = calculate_item_total(quantity, product, rental_start, rental_end)
            
            # Note: We reuse daily_rate field to store the effective unit price to avoid schema changes
            effective_unit_price = (line_total / Decimal(str(quantity))).quantize(Decimal('0.01')) if quantity > 0 else Decimal('0.00')
            
            order_item = OrderItem(
                product_id=product_id,
                quantity=quantity,
                daily_rate=effective_unit_price,
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
    rental_start: datetime,
    rental_end: datetime,
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
        
        for item in items_data:
            product_id = item['product_id']
            quantity = int(item['quantity'])
            
            product = db.session.get(Product, product_id)
            if not product:
                raise ValueError(f"Product ID {product_id} not found.")
                
            line_total = calculate_item_total(quantity, product, rental_start, rental_end)
            effective_unit_price = (line_total / Decimal(str(quantity))).quantize(Decimal('0.01')) if quantity > 0 else Decimal('0.00')
            
            order_item = OrderItem(
                product_id=product_id,
                quantity=quantity,
                daily_rate=effective_unit_price,
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
