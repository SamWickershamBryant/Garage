from app import app
import pytest
from unittest.mock import patch

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

def test_access_protected_route(client):
    response = client.get('/protected', follow_redirects=True)
    assert response.status_code == 200
    assert b"Please log in to access this page." in response.data


def test_signup(client):
    response = client.post('/signup', data=dict(
        username='newuser',
        password='newpassword',
        confirm='newpassword',
        email='newuser@example.com'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b"Account created successfully" in response.data  # Assuming a message shows up on successful creation

def test_logout(client, auth):
    auth.login()  # Assuming you have a helper function in your fixture to log in users

    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data  # Check for login prompt to confirm logout


def test_login(client):
    response = client.post('/login', data=dict(
        username='correct_username',
        password='correct_password'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b"Logged in" in response.data  # Assuming a successful login shows "Logged in"

def test_protected(client):
    response = client.get('/protected', follow_redirects=True)
    assert b"Login" in response.data  # Assuming it redirects to login page


@patch('stripe.checkout.Session.create')
def test_create_checkout_session(mock_create_session, client):
    mock_create_session.return_value = {'id': 'fake_session_id', 'url': 'http://fakeurl.com'}
    response = client.post('/create_checkout_session', data={
        'product_id': '123',
        'price_id': 'price_123',
        'spot_id': '1',
        'spot_num': '101',
        'garage_name': 'Main St Garage',
        'vehicle_id': '1',
        'vehicle_model': 'Car Model',
        'vehicle_plate': 'XYZ123',
        'reservation_date': '2024-01-01'
    })
    assert response.status_code == 303
    assert response.location == 'http://fakeurl.com'

@pytest.fixture
def app():
    app = app
    yield app
