from datetime import date
from decimal import Decimal
import pytest
from app.models.customer import Customer
from app.models.product import Product
from app.models.order import Order
from app.services.order_service import create_order


@pytest.fixture
def logged_in_client(client, test_user):
    client.post('/auth/login', data={
        'username': 'testadmin',
        'password': 'password123'
    }, follow_redirects=True)
    return client


@pytest.fixture
def sample_order(app, db):
    with app.app_context():
        c = Customer(first_name="Jane", last_name="Smith", email="jane.smith@example.com", phone="1234567890", address="123 Main St")
        p = Product(name="Camera Kit", slug="camera-kit", daily_rate=Decimal('50.00'), total_stock=5, category="Electronics")
        db.session.add_all([c, p])
        db.session.commit()

        # 3 day rental: 50.00 * 1 * 3 = 150.00 subtotal
        order = create_order(
            customer_id=c.id,
            rental_start=date(2026, 9, 1),
            rental_end=date(2026, 9, 3),
            items_data=[{'product_id': p.id, 'quantity': 1}],
            discount=10,
            tax_rate=0.10
        )
        # Subtotal: 150.00, Discount: 10.00, Taxable: 140.00, Tax: 14.00, Total: 154.00
        return order.id


def test_invoice_route_access_control(client, sample_order):
    # Unauthenticated access should redirect to login
    res = client.get(f'/orders/{sample_order}/invoice')
    assert res.status_code == 302
    assert '/auth/login' in res.location

    res = client.get(f'/invoices/{sample_order}')
    assert res.status_code == 302
    assert '/auth/login' in res.location


def test_invoice_view_rendering(logged_in_client, app, db, sample_order):
    res = logged_in_client.get(f'/orders/{sample_order}/invoice')
    assert res.status_code == 200
    assert b"Pseudo Booqable" in res.data
    assert b"Jane Smith" in res.data
    assert b"Camera Kit" in res.data
    assert b"UNPAID" in res.data
    assert b"window.print()" in res.data

    # Check blueprint route as well
    res_bp = logged_in_client.get(f'/invoices/{sample_order}')
    assert res_bp.status_code == 200
    assert b"INVOICE" in res_bp.data


def test_invoice_404_nonexistent(logged_in_client):
    res = logged_in_client.get('/orders/99999/invoice')
    assert res.status_code == 404


def test_record_payment_partial_and_full(logged_in_client, app, db, sample_order):
    # 1. Check initial payment status is unpaid
    with app.app_context():
        order = db.session.get(Order, sample_order)
        assert order.payment_status == 'unpaid'
        assert float(order.amount_paid) == 0.0

    # 2. Record partial payment of $50.00
    res = logged_in_client.post(
        f'/orders/{sample_order}/payment',
        data={'amount': '50.00'},
        follow_redirects=True
    )
    assert res.status_code == 200
    assert b"Payment of $50.00 recorded" in res.data

    with app.app_context():
        order = db.session.get(Order, sample_order)
        assert order.payment_status == 'partially_paid'
        assert float(order.amount_paid) == 50.0

    # 3. Record remaining payment of $104.00 (Total is 154.00)
    res = logged_in_client.post(
        f'/orders/{sample_order}/payment',
        data={'amount': '104.00'},
        follow_redirects=True
    )
    assert res.status_code == 200
    assert b"Payment of $104.00 recorded" in res.data

    with app.app_context():
        order = db.session.get(Order, sample_order)
        assert order.payment_status == 'paid'
        assert float(order.amount_paid) == 154.0
        assert b"This order is fully paid" in logged_in_client.get(f'/orders/{sample_order}').data


def test_record_payment_invalid_amount(logged_in_client, app, db, sample_order):
    # Zero or negative amount should fail
    res = logged_in_client.post(
        f'/orders/{sample_order}/payment',
        data={'amount': '0'},
        follow_redirects=True
    )
    assert res.status_code == 200
    assert b"Payment amount must be greater than zero" in res.data

    # Invalid text amount
    res = logged_in_client.post(
        f'/orders/{sample_order}/payment',
        data={'amount': 'abc'},
        follow_redirects=True
    )
    assert res.status_code == 200
    assert b"Invalid payment amount" in res.data
