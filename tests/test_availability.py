from datetime import date, timedelta
from decimal import Decimal
from app.extensions import db
from app.models.user import User
from app.models.product import Product
from app.models.customer import Customer
from app.models.order import Order
from app.models.order_item import OrderItem
from app.services.availability import (
    get_booked_quantity,
    get_available_quantity,
    check_availability
)
from app.services.order_service import create_order


def test_availability_service_math(app):
    """Test unit calculation logic of availability service functions."""
    with app.app_context():
        # Setup Product & Customer
        product = Product(
            name="Camera Tripod",
            slug="camera-tripod",
            daily_rate=Decimal('15.00'),
            total_stock=5,
            is_active=True
        )
        customer = Customer(
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com"
        )
        db.session.add_all([product, customer])
        db.session.commit()

        start = date(2026, 9, 1)
        end = date(2026, 9, 5)

        # Initially 0 booked, 5 available
        assert get_booked_quantity(product.id, start, end) == 0
        assert get_available_quantity(product.id, start, end) == 5

        # Create Order 1 (3 units for Sept 1 - Sept 5)
        order1 = create_order(
            customer_id=customer.id,
            rental_start=start,
            rental_end=end,
            items_data=[{'product_id': product.id, 'quantity': 3}]
        )

        # Now 3 booked, 2 available for Sept 1 - Sept 5
        assert get_booked_quantity(product.id, start, end) == 3
        assert get_available_quantity(product.id, start, end) == 2

        # Non-overlapping range (Sept 10 - Sept 15) should have 0 booked, 5 available
        assert get_booked_quantity(product.id, date(2026, 9, 10), date(2026, 9, 15)) == 0
        assert get_available_quantity(product.id, date(2026, 9, 10), date(2026, 9, 15)) == 5

        # Partial overlap range (Sept 4 - Sept 8) should overlap with order1
        assert get_booked_quantity(product.id, date(2026, 9, 4), date(2026, 9, 8)) == 3
        assert get_available_quantity(product.id, date(2026, 9, 4), date(2026, 9, 8)) == 2

        # Test exclude_order_id (Order 1 should be excluded)
        assert get_booked_quantity(product.id, start, end, exclude_order_id=order1.id) == 0
        assert get_available_quantity(product.id, start, end, exclude_order_id=order1.id) == 5

        # Cancel order1 -> should free up stock
        order1.status = 'cancelled'
        db.session.commit()

        assert get_booked_quantity(product.id, start, end) == 0
        assert get_available_quantity(product.id, start, end) == 5


def test_check_availability_validation(app):
    """Test check_availability error reporting logic."""
    with app.app_context():
        product = Product(
            name="Studio Light",
            slug="studio-light",
            daily_rate=Decimal('25.00'),
            total_stock=2,
            is_active=True
        )
        db.session.add(product)
        db.session.commit()

        start = date(2026, 9, 1)
        end = date(2026, 9, 3)

        # 2 requested <= 2 available -> No errors
        errors = check_availability([{'product_id': product.id, 'quantity': 2}], start, end)
        assert len(errors) == 0

        # 3 requested > 2 available -> Should report error
        errors_exceeded = check_availability([{'product_id': product.id, 'quantity': 3}], start, end)
        assert len(errors_exceeded) == 1
        assert "Cannot book 3 units of 'Studio Light'" in errors_exceeded[0]

        # Invalid date range
        errors_invalid_dates = check_availability([{'product_id': product.id, 'quantity': 1}], end, start)
        assert len(errors_invalid_dates) == 1
        assert "must be on or after" in errors_invalid_dates[0]


def test_create_order_overbooking_blocked(client, app):
    """Integration test: attempting to create an order exceeding stock is blocked."""
    with app.app_context():
        user = User(username="admin_avail", email="admin_avail@example.com")
        user.set_password("password123")
        product = Product(name="Limited Lens", slug="limited-lens", daily_rate=Decimal('50.00'), total_stock=1, is_active=True)
        customer = Customer(first_name="Bob", last_name="Smith", email="bob_avail@example.com")
        db.session.add_all([user, product, customer])
        db.session.commit()

        user_id = user.id
        product_id = product.id
        customer_id = customer.id

    # Log in
    client.post('/auth/login', data={'username': 'admin_avail', 'password': 'password123'})

    # Attempt to book 2 units when total_stock = 1
    res = client.post('/orders/create', data={
        'customer_id': customer_id,
        'rental_start': '2026-10-01',
        'rental_end': '2026-10-05',
        'items-0-product_id': product_id,
        'items-0-quantity': 2,
        'discount': '0.00',
        'tax_rate': '0.00'
    }, follow_redirects=True)

    assert res.status_code == 200
    assert b"Cannot book 2 units" in res.data or b"Only 1 available" in res.data

    # Verify no order was saved to database
    with app.app_context():
        assert Order.query.count() == 0


def test_api_availability_endpoint(client, app):
    """Integration test: GET /api/availability endpoint returns accurate JSON data."""
    with app.app_context():
        user = User(username="api_user", email="api_user@example.com")
        user.set_password("password123")
        product = Product(name="Drone HD", slug="drone-hd", daily_rate=Decimal('100.00'), total_stock=3, is_active=True)
        customer = Customer(first_name="Alice", last_name="Wong", email="alice_api@example.com")
        db.session.add_all([user, product, customer])
        db.session.commit()

        product_id = product.id
        customer_id = customer.id

        # Book 1 unit for Sept 1 - Sept 5
        create_order(
            customer_id=customer_id,
            rental_start=date(2026, 9, 1),
            rental_end=date(2026, 9, 5),
            items_data=[{'product_id': product_id, 'quantity': 1}]
        )

    # Log in
    client.post('/auth/login', data={'username': 'api_user', 'password': 'password123'})

    # Query API endpoint
    res = client.get(f'/api/availability?product_id={product_id}&start=2026-09-01&end=2026-09-05')
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data['total_stock'] == 3
    assert json_data['booked'] == 1
    assert json_data['available'] == 2

    # Query missing params
    res_err = client.get('/api/availability?product_id=1')
    assert res_err.status_code == 400
