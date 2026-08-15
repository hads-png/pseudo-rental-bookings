from datetime import date
from decimal import Decimal
import pytest
from app.models.customer import Customer
from app.models.product import Product
from app.models.order import Order
from app.services.order_service import create_order, update_order_status


@pytest.fixture
def logged_in_client(client, test_user):
    client.post('/auth/login', data={
        'username': 'testadmin',
        'password': 'password123'
    }, follow_redirects=True)
    return client


def test_dashboard_access_control(client):
    res = client.get('/')
    assert res.status_code == 302
    assert '/auth/login' in res.location


def test_dashboard_rendering_with_data(logged_in_client, app, db):
    with app.app_context():
        c = Customer(first_name="Alice", last_name="Dashboard", email="alice.dash@example.com")
        p = Product(name="Studio Light", slug="studio-light", daily_rate=Decimal('25.00'), total_stock=10, category="Lighting")
        db.session.add_all([c, p])
        db.session.commit()

        # Create order in current month
        today = date.today()
        o = create_order(
            customer_id=c.id,
            rental_start=today,
            rental_end=today,
            items_data=[{'product_id': p.id, 'quantity': 2}]
        )
        update_order_status(o, 'confirmed')

    res = logged_in_client.get('/')
    assert res.status_code == 200
    assert b"Welcome," in res.data

    assert b"Active Bookings" in res.data
    assert b"Monthly Revenue" in res.data
    assert b"Studio Light" in res.data
    assert b"Alice Dashboard" in res.data


def test_dashboard_revenue_api_endpoint(logged_in_client):
    res = logged_in_client.get('/api/dashboard/revenue')
    assert res.status_code == 200
    json_data = res.get_json()
    assert 'labels' in json_data
    assert 'data' in json_data
    assert len(json_data['labels']) == 6
    assert len(json_data['data']) == 6
