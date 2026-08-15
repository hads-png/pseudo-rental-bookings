"""
Seed script to populate initial development database with:
- Admin user: admin / admin123
- 10 sample products
- 5 sample customers
- 3 sample orders with order items
- Default business settings
"""
from datetime import date, timedelta
from decimal import Decimal
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.product import Product
from app.models.customer import Customer
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.settings import Settings
from app.services.order_service import generate_order_number, calculate_rental_days

app = create_app()

with app.app_context():
    print("[-] Seeding database...")

    # 0. Default Settings
    settings = Settings.get_settings()
    print(f"  [*] Business Settings: {settings.business_name}")

    # 1. Admin User
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@booqable.local',
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        print("  [+] Created admin user: admin / admin123")
    else:
        print("  [*] Admin user already exists")

    # 2. Sample Products (10 products)
    if Product.query.count() == 0:
        products = [
            Product(name='Sony FX3 Cinema Camera', slug='sony-fx3-cinema-camera', category='Cameras', daily_rate=Decimal('120.00'), total_stock=4, description='Full-frame Cinema Line camera with 4K 120p.'),
            Product(name='Canon EOS R5', slug='canon-eos-r5', category='Cameras', daily_rate=Decimal('95.00'), total_stock=6, description='45MP full-frame mirrorless camera.'),
            Product(name='Sony 24-70mm f/2.8 GM II', slug='sony-24-70mm-f2-8-gm-ii', category='Lenses', daily_rate=Decimal('45.00'), total_stock=5, description='Standard zoom lens for full-frame Sony E-mount.'),
            Product(name='Aputure 300d II LED Light', slug='aputure-300d-ii-led-light', category='Lighting', daily_rate=Decimal('50.00'), total_stock=8, description='Daylight point-source LED light fixture.'),
            Product(name='DJI RS 3 Pro Gimbal', slug='dji-rs-3-pro-gimbal', category='Gimbals', daily_rate=Decimal('40.00'), total_stock=5, description='Automated axis locks and carbon fiber arms.'),
            Product(name='Rode Wireless GO II', slug='rode-wireless-go-ii', category='Audio', daily_rate=Decimal('25.00'), total_stock=10, description='Dual channel wireless microphone system.'),
            Product(name='Sennheiser MKH 416 Shotgun Mic', slug='sennheiser-mkh-416', category='Audio', daily_rate=Decimal('35.00'), total_stock=4, description='Industry standard moisture-resistant shotgun microphone.'),
            Product(name='RED V-Raptor 8K VV', slug='red-v-raptor-8k', category='Cameras', daily_rate=Decimal('350.00'), total_stock=2, description='Flagship multi-format 8K sensor camera.'),
            Product(name='Aputure Nova P300c RGBWW Panel', slug='aputure-nova-p300c', category='Lighting', daily_rate=Decimal('85.00'), total_stock=4, description='300W RGBWW soft light panel.'),
            Product(name='Teradek Bolt 4K LT 750', slug='teradek-bolt-4k-lt-750', category='Video Transmission', daily_rate=Decimal('75.00'), total_stock=3, description='Zero-delay wireless video transmitter and receiver set.'),
        ]
        db.session.add_all(products)
        db.session.commit()
        print(f"  [+] Added {len(products)} sample products")
    else:
        print(f"  [*] Products table already has {Product.query.count()} records")

    # 3. Sample Customers (5 customers)
    if Customer.query.count() == 0:
        customers = [
            Customer(first_name='Alex', last_name='Rivera', email='alex@productionstudio.com', phone='+1 555-0192', address='120 Film St, Los Angeles, CA'),
            Customer(first_name='Sarah', last_name='Connor', email='sarah@skynetmedia.io', phone='+1 555-0143', address='404 Resistance Blvd, Austin, TX'),
            Customer(first_name='Marcus', last_name='Vance', email='marcus@indiefilms.net', phone='+1 555-0188', address='77 Sunset Ave, Seattle, WA'),
            Customer(first_name='Elena', last_name='Rostova', email='elena@cinemaworks.com', phone='+1 555-0167', address='12 Art District Way, New York, NY'),
            Customer(first_name='David', last_name='Kim', email='dkim@apexvisuals.org', phone='+1 555-0112', address='500 Tech Hub Dr, San Francisco, CA'),
        ]
        db.session.add_all(customers)
        db.session.commit()
        print(f"  [+] Added {len(customers)} sample customers")
    else:
        print(f"  [*] Customers table already has {Customer.query.count()} records")

    # 4. Sample Orders (3 orders)
    if Order.query.count() == 0:
        c1 = Customer.query.first()
        c2 = Customer.query.offset(1).first()
        c3 = Customer.query.offset(2).first()

        p1 = Product.query.filter_by(slug='sony-fx3-cinema-camera').first()
        p2 = Product.query.filter_by(slug='sony-24-70mm-f2-8-gm-ii').first()
        p3 = Product.query.filter_by(slug='aputure-300d-ii-led-light').first()

        today = date.today()

        # Order 1: Confirmed
        start1 = today + timedelta(days=2)
        end1 = start1 + timedelta(days=3)
        days1 = calculate_rental_days(start1, end1)
        item1_total = p1.daily_rate * 1 * days1
        subtotal1 = item1_total
        tax1 = subtotal1 * Decimal('0.10')
        total1 = subtotal1 + tax1

        o1 = Order(
            order_number=generate_order_number(),
            customer_id=c1.id,
            status='confirmed',
            rental_start=start1,
            rental_end=end1,
            subtotal=subtotal1,
            discount=Decimal('0.00'),
            tax_rate=Decimal('0.1000'),
            total=total1,
            payment_status='paid',
            amount_paid=total1,
            notes='Commercial shoot in studio B.'
        )
        db.session.add(o1)
        db.session.flush()

        oi1 = OrderItem(
            order_id=o1.id,
            product_id=p1.id,
            quantity=1,
            daily_rate=p1.daily_rate,
            line_total=item1_total
        )
        db.session.add(oi1)

        # Order 2: Picked Up
        start2 = today - timedelta(days=1)
        end2 = today + timedelta(days=2)
        days2 = calculate_rental_days(start2, end2)
        line1 = p2.daily_rate * 2 * days2
        line2 = p3.daily_rate * 1 * days2
        subtotal2 = line1 + line2
        total2 = subtotal2

        o2 = Order(
            order_number=generate_order_number(),
            customer_id=c2.id,
            status='picked_up',
            rental_start=start2,
            rental_end=end2,
            subtotal=subtotal2,
            discount=Decimal('0.00'),
            tax_rate=Decimal('0.0000'),
            total=total2,
            payment_status='partially_paid',
            amount_paid=Decimal('100.00'),
            notes='Weekend event setup.'
        )
        db.session.add(o2)
        db.session.flush()

        oi2_1 = OrderItem(
            order_id=o2.id,
            product_id=p2.id,
            quantity=2,
            daily_rate=p2.daily_rate,
            line_total=line1
        )
        oi2_2 = OrderItem(
            order_id=o2.id,
            product_id=p3.id,
            quantity=1,
            daily_rate=p3.daily_rate,
            line_total=line2
        )
        db.session.add_all([oi2_1, oi2_2])

        # Order 3: Returned
        start3 = today - timedelta(days=10)
        end3 = today - timedelta(days=7)
        days3 = calculate_rental_days(start3, end3)
        line3 = p1.daily_rate * 1 * days3
        subtotal3 = line3
        total3 = subtotal3

        o3 = Order(
            order_number=generate_order_number(),
            customer_id=c3.id,
            status='returned',
            rental_start=start3,
            rental_end=end3,
            subtotal=subtotal3,
            discount=Decimal('0.00'),
            tax_rate=Decimal('0.0000'),
            total=total3,
            payment_status='paid',
            amount_paid=total3,
            notes='Documentary interview.'
        )
        db.session.add(o3)
        db.session.flush()

        oi3 = OrderItem(
            order_id=o3.id,
            product_id=p1.id,
            quantity=1,
            daily_rate=p1.daily_rate,
            line_total=line3
        )
        db.session.add(oi3)

        db.session.commit()
        print("  [+] Added 3 sample orders with order items")
    else:
        print(f"  [*] Orders table already has {Order.query.count()} records")

    db.session.commit()
    print("[OK] Database seeding completed successfully!")
