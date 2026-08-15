from datetime import date
from decimal import Decimal
import pytest
from app.models.customer import Customer
from app.models.product import Product
from app.services.order_service import (
    calculate_rental_days,
    calculate_line_total,
    calculate_order_totals,
    generate_order_number,
    validate_status_transition,
    create_order,
    update_order,
    update_order_status
)


def test_calculate_rental_days():
    # Single day rental
    d1 = date(2026, 8, 15)
    assert calculate_rental_days(d1, d1) == 1

    # 3-day rental: 15, 16, 17
    d2 = date(2026, 8, 17)
    assert calculate_rental_days(d1, d2) == 3

    # Fallback when end date < start date
    assert calculate_rental_days(d2, d1) == 1


def test_calculate_line_total():
    # 2 items * $15.50 * 3 days = $93.00
    total = calculate_line_total(2, Decimal('15.50'), 3)
    assert total == Decimal('93.00')


def test_generate_order_number(app, db):
    with app.app_context():
        target_d = date(2026, 8, 15)
        num1 = generate_order_number(target_d)
        assert num1 == "ORD-20260815-001"

        # Create customer & product to insert order 1
        c = Customer(first_name="John", last_name="Doe", email="john@example.com")
        p = Product(name="Camera", slug="camera", daily_rate=Decimal('50.00'))
        db.session.add_all([c, p])
        db.session.commit()

        create_order(
            customer_id=c.id,
            rental_start=target_d,
            rental_end=target_d,
            items_data=[{'product_id': p.id, 'quantity': 1}]
        )

        num2 = generate_order_number(target_d)
        assert num2 == "ORD-20260815-002"


def test_validate_status_transition():
    # Valid transitions
    assert validate_status_transition('draft', 'confirmed') is True
    assert validate_status_transition('draft', 'cancelled') is True
    assert validate_status_transition('confirmed', 'picked_up') is True
    assert validate_status_transition('picked_up', 'returned') is True

    # Invalid transitions
    assert validate_status_transition('draft', 'returned') is False
    assert validate_status_transition('picked_up', 'draft') is False
    assert validate_status_transition('returned', 'picked_up') is False
    assert validate_status_transition('cancelled', 'confirmed') is False


def test_create_and_update_order_service(app, db):
    with app.app_context():
        customer = Customer(first_name="Jane", last_name="Smith", email="jane@example.com")
        p1 = Product(name="Lens 50mm", slug="lens-50mm", daily_rate=Decimal('20.00'))
        p2 = Product(name="Tripod", slug="tripod", daily_rate=Decimal('10.00'))
        db.session.add_all([customer, p1, p2])
        db.session.commit()

        start_d = date(2026, 9, 1)
        end_d = date(2026, 9, 2)  # 2 days

        # Create order: (20 * 1 * 2 days) + (10 * 2 * 2 days) = 40 + 40 = 80
        order = create_order(
            customer_id=customer.id,
            rental_start=start_d,
            rental_end=end_d,
            items_data=[
                {'product_id': p1.id, 'quantity': 1},
                {'product_id': p2.id, 'quantity': 2}
            ],
            discount=Decimal('10.00'),
            tax_rate=Decimal('0.10')  # 10% tax on (80 - 10) = 7 -> Total = 77
        )

        assert order.order_number.startswith("ORD-20260901-")
        assert order.subtotal == Decimal('80.00')
        assert order.total == Decimal('77.00')
        assert len(order.order_items) == 2

        # Status transition
        success, msg = update_order_status(order, 'confirmed')
        assert success is True
        assert order.status == 'confirmed'

        # Edit order while confirmed
        updated_order = update_order(
            order=order,
            customer_id=customer.id,
            rental_start=start_d,
            rental_end=start_d,  # 1 day
            items_data=[{'product_id': p1.id, 'quantity': 1}],  # 20 * 1 * 1 day = 20
            discount=Decimal('0.00'),
            tax_rate=Decimal('0.00')
        )
        assert updated_order.subtotal == Decimal('20.00')
        assert updated_order.total == Decimal('20.00')
        assert len(updated_order.order_items) == 1

        # Advance to picked_up
        update_order_status(order, 'picked_up')

        # Try to edit in picked_up -> should raise ValueError
        with pytest.raises(ValueError, match="Cannot edit order"):
            update_order(
                order=order,
                customer_id=customer.id,
                rental_start=start_d,
                rental_end=start_d,
                items_data=[{'product_id': p1.id, 'quantity': 1}]
            )
