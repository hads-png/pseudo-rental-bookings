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


def test_order_access_control(client):
    res = client.get('/orders/')
    assert res.status_code == 302
    assert '/auth/login' in res.location


def test_order_list_empty_and_filters(logged_in_client, app, db):
    res = logged_in_client.get('/orders/')
    assert res.status_code == 200
    assert b"No orders found" in res.data

    with app.app_context():
        c = Customer(first_name="Alice", last_name="Wonderland", email="alice@example.com")
        p = Product(name="Projector", slug="projector", daily_rate=Decimal('100.00'), total_stock=10)
        db.session.add_all([c, p])
        db.session.commit()

        o = create_order(
            customer_id=c.id,
            rental_start=date(2026, 8, 15),
            rental_end=date(2026, 8, 17),
            items_data=[{'product_id': p.id, 'quantity': 1}]
        )
        order_num = o.order_number

    # View order list
    res = logged_in_client.get('/orders/')
    assert res.status_code == 200
    assert order_num.encode() in res.data
    assert b"Alice Wonderland" in res.data

    # Filter by search keyword
    res = logged_in_client.get(f'/orders/?q={order_num}')
    assert res.status_code == 200
    assert order_num.encode() in res.data

    # Filter by non-existent status
    res = logged_in_client.get('/orders/?status=returned')
    assert res.status_code == 200
    assert b"No orders found" in res.data


def test_order_create_success(logged_in_client, app, db):
    with app.app_context():
        c = Customer(first_name="Bob", last_name="Builder", email="bob@example.com")
        p = Product(name="Hammer", slug="hammer", daily_rate=Decimal('25.00'), total_stock=10)
        db.session.add_all([c, p])
        db.session.commit()
        c_id, p_id = c.id, p.id

    # Submit create order form
    res = logged_in_client.post('/orders/create', data={
        'customer_id': c_id,
        'rental_start': '2026-08-20',
        'rental_end': '2026-08-22',  # 3 days
        'discount': '5.00',
        'tax_rate': '0.05',
        'notes': 'Deliver to site A',
        'items-0-product_id': p_id,
        'items-0-quantity': 2
    }, follow_redirects=True)

    assert res.status_code == 200
    assert b"created successfully" in res.data
    assert b"Bob Builder" in res.data
    assert b"Deliver to site A" in res.data


def test_order_detail_view(logged_in_client, app, db):
    with app.app_context():
        c = Customer(first_name="Charlie", last_name="Brown", email="charlie@example.com")
        p = Product(name="Speaker", slug="speaker", daily_rate=Decimal('40.00'), total_stock=10)
        db.session.add_all([c, p])
        db.session.commit()

        o = create_order(
            customer_id=c.id,
            rental_start=date(2026, 8, 20),
            rental_end=date(2026, 8, 20),
            items_data=[{'product_id': p.id, 'quantity': 1}]
        )
        o_id = o.id

    res = logged_in_client.get(f'/orders/{o_id}')
    assert res.status_code == 200
    assert b"Charlie Brown" in res.data
    assert b"Confirm Order" in res.data


def test_order_status_transitions_and_edit_guards(logged_in_client, app, db):
    with app.app_context():
        c = Customer(first_name="David", last_name="Goliath", email="david@example.com")
        p = Product(name="Mic", slug="mic", daily_rate=Decimal('15.00'), total_stock=10)
        db.session.add_all([c, p])
        db.session.commit()

        o = create_order(
            customer_id=c.id,
            rental_start=date(2026, 8, 20),
            rental_end=date(2026, 8, 20),
            items_data=[{'product_id': p.id, 'quantity': 1}]
        )
        o_id = o.id
        c_id = c.id
        p_id = p.id

    # Confirm order
    res = logged_in_client.post(f'/orders/{o_id}/status', data={'status': 'confirmed'}, follow_redirects=True)
    assert res.status_code == 200
    assert b"Order status updated" in res.data
    assert b"confirmed" in res.data

    # Edit order while confirmed
    res = logged_in_client.post(f'/orders/{o_id}/edit', data={
        'customer_id': c_id,
        'rental_start': '2026-08-20',
        'rental_end': '2026-08-21',
        'discount': '0.00',
        'tax_rate': '0.00',
        'items-0-product_id': p_id,
        'items-0-quantity': 2
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"updated successfully" in res.data

    # Mark Picked Up
    res = logged_in_client.post(f'/orders/{o_id}/status', data={'status': 'picked_up'}, follow_redirects=True)
    assert res.status_code == 200
    assert b"Order status updated" in res.data
    assert b"picked_up" in res.data

    # Edit attempt while picked_up -> blocked
    res = logged_in_client.get(f'/orders/{o_id}/edit', follow_redirects=True)
    assert res.status_code == 200
    assert b"Cannot edit order" in res.data

    # Mark Returned
    res = logged_in_client.post(f'/orders/{o_id}/status', data={'status': 'returned'}, follow_redirects=True)
    assert res.status_code == 200
    assert b"Order status updated" in res.data
    assert b"returned" in res.data


def test_customer_detail_displays_order_history(logged_in_client, app, db):
    with app.app_context():
        c = Customer(first_name="Emma", last_name="Watson", email="emma@example.com")
        p = Product(name="Lighting Rig", slug="lighting-rig", daily_rate=Decimal('150.00'))
        db.session.add_all([c, p])
        db.session.commit()

        o = create_order(
            customer_id=c.id,
            rental_start=date(2026, 8, 25),
            rental_end=date(2026, 8, 26),
            items_data=[{'product_id': p.id, 'quantity': 1}]
        )
        c_id = c.id
        o_num = o.order_number

    res = logged_in_client.get(f'/customers/{c_id}')
    assert res.status_code == 200
    assert o_num.encode() in res.data
    assert b"1 order" in res.data
