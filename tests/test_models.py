from datetime import date
from decimal import Decimal
from app.models.user import User
from app.models.product import Product
from app.models.customer import Customer
from app.models.order import Order
from app.models.order_item import OrderItem


def test_user_password_hashing(app, db):
    user = User(username='johndoe', email='john@example.com')
    user.set_password('mysecretpass')
    db.session.add(user)
    db.session.commit()

    assert user.id is not None
    assert user.password_hash != 'mysecretpass'
    assert user.check_password('mysecretpass') is True
    assert user.check_password('wrongpass') is False


def test_product_model(app, db):
    product = Product(
        name='Sony FX3 Cinema Camera',
        slug='sony-fx3-cinema-camera',
        description='Full frame cinema line camera',
        daily_rate=Decimal('120.00'),
        total_stock=5,
        category='Cameras'
    )
    db.session.add(product)
    db.session.commit()

    saved = Product.query.filter_by(slug='sony-fx3-cinema-camera').first()
    assert saved is not None
    assert saved.name == 'Sony FX3 Cinema Camera'
    assert saved.daily_rate == Decimal('120.00')
    assert saved.total_stock == 5
    assert saved.is_active is True


def test_customer_model(app, db):
    customer = Customer(
        first_name='Alice',
        last_name='Smith',
        email='alice@example.com',
        phone='+1234567890'
    )
    db.session.add(customer)
    db.session.commit()

    saved = Customer.query.filter_by(email='alice@example.com').first()
    assert saved is not None
    assert saved.full_name == 'Alice Smith'


def test_order_and_order_item_relationship(app, db):
    customer = Customer(first_name='Bob', last_name='Marley', email='bob@example.com')
    product = Product(name='Tripod Pro', slug='tripod-pro', daily_rate=Decimal('25.00'), total_stock=10)
    db.session.add_all([customer, product])
    db.session.commit()

    order = Order(
        order_number='ORD-20260813-001',
        customer_id=customer.id,
        status='draft',
        rental_start=date(2026, 8, 15),
        rental_end=date(2026, 8, 18),
        subtotal=Decimal('75.00'),
        total=Decimal('75.00')
    )
    db.session.add(order)
    db.session.commit()

    item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        quantity=1,
        daily_rate=Decimal('25.00'),
        line_total=Decimal('75.00')
    )
    db.session.add(item)
    db.session.commit()

    assert len(order.order_items) == 1
    assert order.order_items[0].product.name == 'Tripod Pro'
    assert customer.orders.first().order_number == 'ORD-20260813-001'
