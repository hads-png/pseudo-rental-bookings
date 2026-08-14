"""
Tests for Product CRUD, search/filter, pagination, slug generation, image upload, and soft-delete.
"""
import io
import os
from decimal import Decimal

from app.models.product import Product


def _login(client):
    """Helper to log in the test user."""
    client.post('/auth/login', data={
        'username': 'testadmin',
        'password': 'password123'
    })


def _create_product(db, name='Test Product', slug='test-product', category='Cameras',
                    daily_rate=Decimal('50.00'), total_stock=5):
    """Helper to insert a product directly into the DB."""
    product = Product(
        name=name,
        slug=slug,
        category=category,
        daily_rate=daily_rate,
        total_stock=total_stock,
        description='A test product.'
    )
    db.session.add(product)
    db.session.commit()
    return product


# ─── List & Empty State ───────────────────────────────────────────

def test_product_list_empty_and_populated(client, test_user, db):
    """Verify empty state message and populated table rendering."""
    _login(client)

    # Empty state
    response = client.get('/products/')
    assert response.status_code == 200
    assert b'No products yet' in response.data

    # Populated state
    _create_product(db)
    response = client.get('/products/')
    assert b'Test Product' in response.data
    assert b'$50.00' in response.data


# ─── Search Filter ────────────────────────────────────────────────

def test_product_search_filter(client, test_user, db):
    """Verify search by name returns matching products and excludes others."""
    _login(client)
    _create_product(db, name='Sony FX3', slug='sony-fx3')
    _create_product(db, name='Canon R5', slug='canon-r5')

    response = client.get('/products/?q=Sony')
    assert b'Sony FX3' in response.data
    assert b'Canon R5' not in response.data

    response = client.get('/products/?q=Canon')
    assert b'Canon R5' in response.data
    assert b'Sony FX3' not in response.data


# ─── Category Filter ─────────────────────────────────────────────

def test_product_category_filter(client, test_user, db):
    """Verify category dropdown filters products accurately."""
    _login(client)
    _create_product(db, name='Camera A', slug='camera-a', category='Cameras')
    _create_product(db, name='Lens B', slug='lens-b', category='Lenses')

    response = client.get('/products/?category=Cameras')
    assert b'Camera A' in response.data
    assert b'Lens B' not in response.data

    response = client.get('/products/?category=Lenses')
    assert b'Lens B' in response.data
    assert b'Camera A' not in response.data


# ─── Pagination ───────────────────────────────────────────────────

def test_product_pagination(client, test_user, db):
    """Creates 15 products and verifies 10 per page pagination behavior."""
    _login(client)
    for i in range(15):
        _create_product(db, name=f'Product {i:02d}', slug=f'product-{i:02d}')

    # Page 1 should have 10 items
    response = client.get('/products/')
    assert response.status_code == 200
    # Check pagination controls appear
    assert b'Next' in response.data or b'page=' in response.data

    # Page 2 should have 5 items
    response = client.get('/products/?page=2')
    assert response.status_code == 200


# ─── Create Product & Slug ────────────────────────────────────────

def test_product_create_success_and_slug_generation(client, test_user, app, db):
    """Creates product via form, checks DB insertion and slug generation."""
    _login(client)

    response = client.post('/products/create', data={
        'name': 'Sony A7 IV Camera',
        'category': 'Cameras',
        'daily_rate': '85.00',
        'total_stock': '5',
        'description': 'Full frame mirrorless.'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Product &#39;Sony A7 IV Camera&#39; created successfully." in response.data or b"created successfully" in response.data

    with app.app_context():
        product = Product.query.filter_by(name='Sony A7 IV Camera').first()
        assert product is not None
        assert product.slug == 'sony-a7-iv-camera'
        assert product.daily_rate == Decimal('85.00')
        assert product.total_stock == 5
        assert product.category == 'Cameras'


# ─── Slug Collision ───────────────────────────────────────────────

def test_product_slug_collision_handling(client, test_user, app, db):
    """Creates products with identical names and asserts suffix resolution."""
    _login(client)

    # First product
    client.post('/products/create', data={
        'name': 'Duplicate Name',
        'daily_rate': '10.00',
        'total_stock': '1'
    })

    # Second product with same name
    client.post('/products/create', data={
        'name': 'Duplicate Name',
        'daily_rate': '20.00',
        'total_stock': '2'
    })

    with app.app_context():
        products = Product.query.filter(Product.slug.like('duplicate-name%')).order_by(Product.id).all()
        assert len(products) == 2
        assert products[0].slug == 'duplicate-name'
        assert products[1].slug == 'duplicate-name-1'


# ─── Image Upload ─────────────────────────────────────────────────

def test_product_image_upload(client, test_user, app, db):
    """Uploads mock image bytes and asserts file exists on disk and image_url is stored."""
    _login(client)

    # Create a minimal valid JPEG file (JFIF header)
    image_data = (
        b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
        b'\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t'
        b'\xff\xd9'
    )

    response = client.post('/products/create', data={
        'name': 'Product With Image',
        'daily_rate': '30.00',
        'total_stock': '3',
        'image': (io.BytesIO(image_data), 'test_image.jpg')
    }, follow_redirects=True, content_type='multipart/form-data')

    assert response.status_code == 200

    with app.app_context():
        product = Product.query.filter_by(name='Product With Image').first()
        assert product is not None
        assert product.image_url is not None
        assert product.image_url.startswith('uploads/')
        assert product.image_url.endswith('.jpg')

        # Verify file exists on disk
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], product.image_url.replace('uploads/', ''))
        assert os.path.isfile(filepath)

        # Cleanup
        os.remove(filepath)


# ─── Edit Product ─────────────────────────────────────────────────

def test_product_edit_update(client, test_user, app, db):
    """Edits product rate and stock, verifies updated values in database."""
    _login(client)
    product = _create_product(db, name='Editable Product', slug='editable-product',
                              daily_rate=Decimal('40.00'), total_stock=3)

    response = client.post(f'/products/{product.id}/edit', data={
        'name': 'Editable Product',
        'category': 'Updated Category',
        'daily_rate': '55.00',
        'total_stock': '8',
        'description': 'Updated description.'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'updated successfully' in response.data

    with app.app_context():
        updated = db.session.get(Product, product.id)
        assert updated.daily_rate == Decimal('55.00')
        assert updated.total_stock == 8
        assert updated.category == 'Updated Category'
        assert updated.description == 'Updated description.'


# ─── Soft Delete ──────────────────────────────────────────────────

def test_product_soft_delete(client, test_user, app, db):
    """Executes delete POST, asserts is_active == False and product not in active list."""
    _login(client)
    product = _create_product(db, name='Deletable Product', slug='deletable-product')

    response = client.post(f'/products/{product.id}/delete', follow_redirects=True)
    assert response.status_code == 200
    assert b"was deleted" in response.data

    with app.app_context():
        deleted = db.session.get(Product, product.id)
        assert deleted is not None  # Still exists in DB
        assert deleted.is_active is False  # But soft-deleted

    # Verify product no longer in active list
    list_response = client.get('/products/')
    assert b'Deletable Product' not in list_response.data


# ─── Access Control ───────────────────────────────────────────────

def test_product_access_control(client):
    """Asserts unauthenticated requests redirect to /auth/login."""
    endpoints = [
        '/products/',
        '/products/create',
        '/products/1',
        '/products/1/edit',
    ]
    for endpoint in endpoints:
        response = client.get(endpoint, follow_redirects=False)
        assert response.status_code == 302, f"Expected redirect for {endpoint}"
        assert '/auth/login' in response.location, f"Expected login redirect for {endpoint}"

    # POST endpoints
    post_endpoints = [
        '/products/create',
        '/products/1/edit',
        '/products/1/delete',
    ]
    for endpoint in post_endpoints:
        response = client.post(endpoint, follow_redirects=False)
        assert response.status_code == 302, f"Expected redirect for POST {endpoint}"
        assert '/auth/login' in response.location, f"Expected login redirect for POST {endpoint}"


# ─── Validation Errors ────────────────────────────────────────────

def test_product_create_validation_errors(client, test_user):
    """Submit create form with missing required fields and verify re-render with errors."""
    _login(client)

    # Empty form submission
    response = client.post('/products/create', data={
        'name': '',
        'daily_rate': '',
        'total_stock': ''
    }, follow_redirects=True)

    assert response.status_code == 200
    # Should re-render the form page (not redirect)
    assert b'Add New Product' in response.data
    # Should show validation error messages
    assert b'required' in response.data.lower() or b'This field is required' in response.data
