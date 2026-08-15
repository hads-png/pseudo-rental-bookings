import pytest
from app.models.settings import Settings


def test_settings_default_creation(app, db):
    """Test that default settings are auto-created if none exist."""
    with app.app_context():
        settings = Settings.get_settings()
        assert settings is not None
        assert settings.business_name == 'Pseudo Booqable Rentals'
        assert float(settings.default_tax_rate) == 0.10


def test_settings_page_access_control(client):
    """Test unauthenticated access to settings redirects to login."""
    response = client.get('/settings/', follow_redirects=False)
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']


def test_settings_update(client, app, db):
    """Test authenticated admin user updating settings."""
    # Login user
    client.post('/auth/register', data={
        'username': 'admin_settings',
        'email': 'admin_settings@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    client.post('/auth/login', data={
        'username': 'admin_settings',
        'password': 'password123'
    })

    response = client.post('/settings/', data={
        'business_name': 'Acme Camera Rentals',
        'business_address': '456 Studio Way, Hollywood, CA',
        'default_tax_rate': '0.0850'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Settings updated successfully' in response.data

    with app.app_context():
        settings = Settings.get_settings()
        assert settings.business_name == 'Acme Camera Rentals'
        assert settings.business_address == '456 Studio Way, Hollywood, CA'
        assert float(settings.default_tax_rate) == 0.0850
