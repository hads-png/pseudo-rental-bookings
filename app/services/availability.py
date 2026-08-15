from datetime import date
from typing import Any
from sqlalchemy import select, func
from app.extensions import db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product


def get_booked_quantity(
    product_id: int,
    start_date: date,
    end_date: date,
    exclude_order_id: int | None = None
) -> int:
    """
    Calculates the total quantity of a product booked in non-cancelled orders
    that overlap with [start_date, end_date].
    
    Overlap condition:
    Order.rental_start <= end_date AND Order.rental_end >= start_date
    """
    if not start_date or not end_date or start_date > end_date:
        return 0

    stmt = (
        select(func.coalesce(func.sum(OrderItem.quantity), 0))
        .join(Order, OrderItem.order_id == Order.id)
        .where(
            OrderItem.product_id == product_id,
            Order.status != 'cancelled',
            Order.rental_start <= end_date,
            Order.rental_end >= start_date
        )
    )

    if exclude_order_id is not None:
        stmt = stmt.where(Order.id != exclude_order_id)

    booked_qty = db.session.scalar(stmt)
    return int(booked_qty or 0)


def get_available_quantity(
    product_id: int,
    start_date: date,
    end_date: date,
    exclude_order_id: int | None = None
) -> int:
    """
    Calculates available stock for a product in [start_date, end_date].
    Available = total_stock - booked_quantity
    """
    product = db.session.get(Product, product_id)
    if not product or not product.is_active:
        return 0

    booked = get_booked_quantity(product_id, start_date, end_date, exclude_order_id=exclude_order_id)
    return max(0, product.total_stock - booked)


def check_availability(
    items: list[dict[str, Any]],
    start_date: date,
    end_date: date,
    exclude_order_id: int | None = None
) -> list[str]:
    """
    Validates a list of items [{'product_id': int, 'quantity': int}] for availability.
    Returns a list of error messages (empty if all requested items are available).
    """
    errors = []
    if not start_date or not end_date:
        return ["Rental start and end dates are required."]

    if end_date < start_date:
        return ["Rental end date must be on or after rental start date."]

    # Aggregate quantities per product in case form submits duplicate product rows
    product_totals: dict[int, int] = {}
    for item in items:
        pid = item.get('product_id')
        qty = item.get('quantity', 0)
        if pid and qty > 0:
            product_totals[pid] = product_totals.get(pid, 0) + int(qty)

    for pid, req_qty in product_totals.items():
        product = db.session.get(Product, pid)
        if not product:
            errors.append(f"Product ID {pid} does not exist.")
            continue

        available = get_available_quantity(pid, start_date, end_date, exclude_order_id=exclude_order_id)
        if req_qty > available:
            errors.append(
                f"Cannot book {req_qty} units of '{product.name}'. Only {available} available for selected dates."
            )

    return errors
