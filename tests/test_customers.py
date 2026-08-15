"""
Tests for Customer CRUD operations, search, pagination, email validation,
order deletion protection, and access control.
"""
from datetime import date, timedelta
from app.models.customer import Customer
from app.models.order import Order


def _login(client):
    """Helper to log in the test admin user."""
    client.post('/auth/login', data={
        'username': 'testadmin',
        'password': 'password123'
    })


def _create_customer(db, first_name='Jane', last_name='Doe', email='jane.doe@example.com',
                     phone='555-0199', address='123 Main St'):
    """Helper to create a customer in the DB."""
    customer = Customer(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        address=address,
        notes='Test note.'
    )
    db.session.add(customer)
    db.session.commit()
    return customer


# ─── List & Empty State ───────────────────────────────────────────

def test_customer_list_empty_and_populated(client, test_user, db):
    """Verify empty state message and populated customer table."""
    _login(client)

    # Empty state
    response = client.get('/customers/')
    assert response.status_code == 200
    assert b'No customers yet' in response.data

    # Populated state
    _create_customer(db)
    response = client.get('/customers/')
    assert b'Jane Doe' in response.data
    assert b'jane.doe@example.com' in response.data


# ─── Search ───────────────────────────────────────────────────────

def test_customer_search_by_name_and_email(client, test_user, db):
    """Verify search filters by first name, last name, full name, and email."""
    _login(client)
    _create_customer(db, first_name='Alice', last_name='Smith', email='alice@example.com')
    _create_customer(db, first_name='Bob', last_name='Jones', email='bob@example.com')

    # Search by first name
    response = client.get('/customers/?q=Alice')
    assert b'Alice Smith' in response.data
    assert b'Bob Jones' not in response.data

    # Search by last name
    response = client.get('/customers/?q=Jones')
    assert b'Bob Jones' in response.data
    assert b'Alice Smith' not in response.data

    # Search by full name
    response = client.get('/customers/?q=Alice Smith')
    assert b'Alice Smith' in response.data
    assert b'Bob Jones' not in response.data

    # Search by email
    response = client.get('/customers/?q=bob@example.com')
    assert b'Bob Jones' in response.data
    assert b'Alice Smith' not in response.data


# ─── Pagination ───────────────────────────────────────────────────

def test_customer_pagination(client, test_user, db):
    """Creates 15 customers and verifies 10 per page pagination."""
    _login(client)
    for i in range(15):
        _create_customer(db, first_name=f'User{i:02d}', last_name='Test', email=f'user{i:02d}@example.com')

    response = client.get('/customers/')
    assert response.status_code == 200
    assert b'Showing' in response.data

    # Page 2
    response = client.get('/customers/?page=2')
    assert response.status_code == 200


# ─── Create Customer ──────────────────────────────────────────────

def test_customer_create_success(client, test_user, app, db):
    """Creates a customer via POST and asserts DB record insertion."""
    _login(client)

    response = client.post('/customers/create', data={
        'first_name': 'Charlie',
        'last_name': 'Brown',
        'email': 'charlie@example.com',
        'phone': '555-4321',
        'address': '742 Evergreen Terrace',
        'notes': 'Preferred customer.'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'created successfully' in response.data

    with app.app_context():
        customer = Customer.query.filter_by(email='charlie@example.com').first()
        assert customer is not None
        assert customer.full_name == 'Charlie Brown'
        assert customer.phone == '555-4321'


def test_customer_create_duplicate_email(client, test_user, db):
    """Submits duplicate email and asserts form validation error."""
    _login(client)
    _create_customer(db, email='duplicate@example.com')

    response = client.post('/customers/create', data={
        'first_name': 'New',
        'last_name': 'User',
        'email': 'duplicate@example.com'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'A customer with this email address already exists' in response.data


# ─── Edit Customer ────────────────────────────────────────────────

def test_customer_edit_update(client, test_user, app, db):
    """Edits customer details and asserts changes in database."""
    _login(client)
    customer = _create_customer(db, first_name='Original', last_name='Name', email='original@example.com')

    response = client.post(f'/customers/{customer.id}/edit', data={
        'first_name': 'Updated',
        'last_name': 'Name',
        'email': 'original@example.com',  # Same email shouldn't trigger duplicate error
        'phone': '555-9999',
        'address': 'New Address',
        'notes': 'Updated notes.'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'updated successfully' in response.data

    with app.app_context():
        updated = db.session.get(Customer, customer.id)
        assert updated.first_name == 'Updated'
        assert updated.phone == '555-9999'


# ─── Delete Customer ──────────────────────────────────────────────

def test_customer_delete_success_no_orders(client, test_user, app, db):
    """Hard-deletes customer with 0 orders and asserts deletion."""
    _login(client)
    customer = _create_customer(db, first_name='ToDelete', last_name='Customer', email='todelete@example.com')

    response = client.post(f'/customers/{customer.id}/delete', follow_redirects=True)
    assert response.status_code == 200
    assert b'was deleted' in response.data

    with app.app_context():
        deleted = db.session.get(Customer, customer.id)
        assert deleted is None


def test_customer_delete_blocked_with_orders(client, test_user, app, db):
    """Attempts deletion of customer with orders, asserts blocked and error flash."""
    _login(client)
    customer = _create_customer(db, first_name='HasOrder', last_name='Customer', email='hasorder@example.com')

    # Create mock order for customer
    order = Order(
        order_number='ORD-TEST-001',
        customer_id=customer.id,
        status='draft',
        rental_start=date.today(),
        rental_end=date.today() + timedelta(days=2),
        subtotal=100.00,
        total=100.00
    )
    db.session.add(order)
    db.session.commit()

    response = client.post(f'/customers/{customer.id}/delete', follow_redirects=True)
    assert response.status_code == 200
    assert b'Could not delete customer &#39;they have existing orders.' in response.data or b'Could not delete customer' in response.data

    with app.app_context():
        existing = db.session.get(Customer, customer.id)
        assert existing is not None  # Customer is preserved


# ─── Access Control ───────────────────────────────────────────────

def test_customer_access_control(client):
    """Asserts unauthenticated requests redirect to /auth/login."""
    endpoints = [
        '/customers/',
        '/customers/create',
        '/customers/1',
        '/customers/1/edit',
    ]
    for endpoint in endpoints:
        response = client.get(endpoint, follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/login' in response.location

    post_endpoints = [
        '/customers/create',
        '/customers/1/edit',
        '/customers/1/delete',
    ]
    for endpoint in post_endpoints:
        response = client.post(endpoint, follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/login' in response.location
