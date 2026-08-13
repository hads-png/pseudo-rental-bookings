"""
Seed script to populate initial development database with:
- Admin user: admin / admin123
- Sample products
- Sample customers
"""
from decimal import Decimal
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.product import Product
from app.models.customer import Customer

app = create_app()

with app.app_context():
    print("[-] Seeding database...")
    
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

    # 2. Sample Products
    if Product.query.count() == 0:
        products = [
            Product(name='Sony FX3 Cinema Camera', slug='sony-fx3-cinema-camera', category='Cameras', daily_rate=Decimal('120.00'), total_stock=4, description='Full-frame Cinema Line camera with 4K 120p.'),
            Product(name='Canon EOS R5', slug='canon-eos-r5', category='Cameras', daily_rate=Decimal('95.00'), total_stock=6, description='45MP full-frame mirrorless camera.'),
            Product(name='Sony 24-70mm f/2.8 GM II', slug='sony-24-70mm-f2-8-gm-ii', category='Lenses', daily_rate=Decimal('45.00'), total_stock=5, description='Standard zoom lens for full-frame Sony E-mount.'),
            Product(name='Aputure 300d II LED Light', slug='aputure-300d-ii-led-light', category='Lighting', daily_rate=Decimal('50.00'), total_stock=8, description='Daylight point-source LED light fixture.'),
            Product(name='DJI RS 3 Pro Gimbal', slug='dji-rs-3-pro-gimbal', category='Gimbals', daily_rate=Decimal('40.00'), total_stock=5, description='Automated axis locks and carbon fiber arms.'),
            Product(name='Rode Wireless GO II', slug='rode-wireless-go-ii', category='Audio', daily_rate=Decimal('25.00'), total_stock=10, description='Dual channel wireless microphone system.'),
        ]
        db.session.add_all(products)
        print(f"  [+] Added {len(products)} sample products")
    else:
        print(f"  [*] Products table already has {Product.query.count()} records")

    # 3. Sample Customers
    if Customer.query.count() == 0:
        customers = [
            Customer(first_name='Alex', last_name='Rivera', email='alex@productionstudio.com', phone='+1 555-0192', address='120 Film St, Los Angeles, CA'),
            Customer(first_name='Sarah', last_name='Connor', email='sarah@skynetmedia.io', phone='+1 555-0143', address='404 Resistance Blvd, Austin, TX'),
            Customer(first_name='Marcus', last_name='Vance', email='marcus@indiefilms.net', phone='+1 555-0188', address='77 Sunset Ave, Seattle, WA'),
        ]
        db.session.add_all(customers)
        print(f"  [+] Added {len(customers)} sample customers")
    else:
        print(f"  [*] Customers table already has {Customer.query.count()} records")

    db.session.commit()
    print("[OK] Database seeding completed successfully!")
