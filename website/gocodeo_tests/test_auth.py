import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_login import LoginManager
from website.auth import auth, login, sign_up, logout
from website.models import User
from werkzeug.security import generate_password_hash

@pytest.fixture
def client():
    app = Flask(__name__)
    app.secret_key = 'test_secret'
    app.register_blueprint(auth)
    
    # Set up Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)

    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_user():
    user = MagicMock(spec=User)
    user.email = 'test@example.com'
    user.password = generate_password_hash('securepassword', method='pbkdf2:sha256')
    user.first_name = 'Test'
    return user

@pytest.fixture
def mock_db_session():
    with patch('website.auth.db.session') as mock_session:
        yield mock_session

@pytest.fixture
def mock_user_query(mock_user):
    with patch('website.auth.User.query.filter_by') as mock_filter:
        mock_filter.return_value.first.return_value = mock_user
        yield mock_filter

@pytest.fixture
def mock_flash():
    with patch('website.auth.flash') as mock_flash:
        yield mock_flash

@pytest.fixture
def mock_login_user():
    with patch('website.auth.login_user') as mock_login:
        yield mock_login

@pytest.fixture
def mock_logout_user():
    with patch('website.auth.logout_user') as mock_logout:
        yield mock_logout

@pytest.fixture
def mock_render_template():
    with patch('website.auth.render_template') as mock_render:
        yield mock_render

@pytest.fixture
def mock_redirect():
    with patch('website.auth.redirect') as mock_redirect:
        yield mock_redirect

@pytest.fixture
def mock_url_for():
    with patch('website.auth.url_for') as mock_url:
        yield mock_url

# happy_path - test_signup_success - Test that a user can successfully sign up with valid details.
def test_signup_success(client, mock_user_query, mock_db_session, mock_flash, mock_login_user, mock_redirect, mock_url_for):
    mock_user_query.return_value.first.return_value = None
    mock_url_for.return_value = '/views/home'
    response = client.post('/signup', data={
        'email': 'newuser@example.com',
        'firstName': 'John',
        'password1': 'securepassword',
        'password2': 'securepassword'
    })
    assert mock_flash.called_once_with('Successfully Signed up. Welcome!', category='success')
    assert mock_login_user.called_once
    assert mock_redirect.called_once_with('/views/home')
    assert response.status_code == 302

# happy_path - test_login_page_render - Test that login page renders correctly for GET request.
def test_login_page_render(client, mock_render_template):
    response = client.get('/login')
    mock_render_template.assert_called_once_with('login.html', user=None)
    assert response.status_code == 200

# happy_path - test_signup_page_render - Test that signup page renders correctly for GET request.
def test_signup_page_render(client, mock_render_template):
    response = client.get('/signup')
    mock_render_template.assert_called_once_with('signup.html', user=None)
    assert response.status_code == 200

# edge_case - test_login_incorrect_password - Test that login fails with incorrect password.
def test_login_incorrect_password(client, mock_user_query, mock_flash):
    mock_user_query.return_value.first.return_value = mock_user
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'wrong_password'
    })
    mock_flash.assert_called_once_with('Incorrect password', category='error')
    assert response.status_code == 200

# edge_case - test_login_nonexistent_user - Test that login fails with non-existent user.
def test_login_nonexistent_user(client, mock_user_query, mock_flash):
    mock_user_query.return_value.first.return_value = None
    response = client.post('/login', data={
        'email': 'nonexistent@example.com',
        'password': 'any_password'
    })
    mock_flash.assert_called_once_with('No such user. Please sign up', category='error')
    assert response.status_code == 200

# edge_case - test_signup_existing_email - Test that signup fails with existing email.
def test_signup_existing_email(client, mock_user_query, mock_flash):
    response = client.post('/signup', data={
        'email': 'existing@example.com',
        'firstName': 'John',
        'password1': 'securepassword',
        'password2': 'securepassword'
    })
    mock_flash.assert_called_once_with('Account already exists. Please log in.', category='error')
    assert response.status_code == 200

# edge_case - test_signup_password_mismatch - Test that signup fails with mismatched passwords.
def test_signup_password_mismatch(client, mock_user_query, mock_flash):
    mock_user_query.return_value.first.return_value = None
    response = client.post('/signup', data={
        'email': 'newuser@example.com',
        'firstName': 'John',
        'password1': 'password1',
        'password2': 'password2'
    })
    mock_flash.assert_called_once_with('Passwords do not match.', category='error')
    assert response.status_code == 200

# edge_case - test_signup_short_password - Test that signup fails with short password.
def test_signup_short_password(client, mock_user_query, mock_flash):
    mock_user_query.return_value.first.return_value = None
    response = client.post('/signup', data={
        'email': 'newuser@example.com',
        'firstName': 'John',
        'password1': 'short',
        'password2': 'short'
    })
    mock_flash.assert_called_once_with('Passwords must be at least 8 characters.', category='error')
    assert response.status_code == 200

# edge_case - test_signup_short_email - Test that signup fails with short email.
def test_signup_short_email(client, mock_user_query, mock_flash):
    mock_user_query.return_value.first.return_value = None
    response = client.post('/signup', data={
        'email': 'a@b',
        'firstName': 'John',
        'password1': 'securepassword',
        'password2': 'securepassword'
    })
    mock_flash.assert_called_once_with('Email must be more than 4 characters.', category='error')
    assert response.status_code == 200

