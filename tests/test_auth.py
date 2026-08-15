from app.models.user import User


def test_login_page_renders(client):
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Sign in to your account' in response.data


def test_register_page_renders(client):
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'Create an Admin Account' in response.data


def test_protected_dashboard_redirects_anonymous(client):
    response = client.get('/', follow_redirects=False)
    assert response.status_code == 302
    assert '/auth/login' in response.location


def test_user_registration(client, app):
    response = client.post('/auth/register', data={
        'username': 'newadmin',
        'email': 'newadmin@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Your account has been successfully created' in response.data

    with app.app_context():
        user = User.query.filter_by(username='newadmin').first()
        assert user is not None
        assert user.email == 'newadmin@example.com'
        assert user.check_password('password123') is True


def test_user_login_and_logout(client, test_user):
    # Login with valid credentials
    response = client.post('/auth/login', data={
        'username': 'testadmin',
        'password': 'password123',
        'remember_me': False
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Welcome,' in response.data
    assert b'testadmin' in response.data

    # Access protected dashboard
    dash_response = client.get('/')
    assert dash_response.status_code == 200
    assert b'Phase 7 Live: Analytics & Reports' in dash_response.data

    # Verify all sidebar navigation links are present
    assert b'Dashboard' in dash_response.data
    assert b'Products' in dash_response.data
    assert b'Customers' in dash_response.data
    assert b'Orders' in dash_response.data
    assert b'Invoices' in dash_response.data
    assert b'Settings' in dash_response.data

    # Logout
    logout_response = client.get('/auth/logout', follow_redirects=True)
    assert logout_response.status_code == 200
    assert b'You have been logged out successfully.' in logout_response.data

    # Verify protected route redirects again
    after_logout = client.get('/', follow_redirects=False)
    assert after_logout.status_code == 302


def test_login_invalid_credentials(client, test_user):
    response = client.post('/auth/login', data={
        'username': 'testadmin',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid username/email or password.' in response.data


def test_settings_route_protected(client, test_user):
    # Anonymous redirect
    anon_response = client.get('/settings/', follow_redirects=False)
    assert anon_response.status_code == 302
    assert '/auth/login' in anon_response.location

    # Authenticated access
    client.post('/auth/login', data={
        'username': 'testadmin',
        'password': 'password123'
    })
    auth_response = client.get('/settings/')
    assert auth_response.status_code == 200
    assert b'Business Settings' in auth_response.data
