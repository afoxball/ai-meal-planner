import pytest
from app import create_app, db
from app.models import User, MealPreference, MealPlan
from config import Config


class TestConfig(Config):
    """Test configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'


@pytest.fixture
def app():
    """Create and configure a test application instance."""
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def auth_client(client, app):
    """Create an authenticated test client."""
    with app.app_context():
        # Create a test user
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()

    # Log in the user
    client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'testpassword'
    })
    return client


class TestMainRoutes:
    """Test main routes."""

    def test_index_page(self, client):
        """Test home page loads."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'AI Meal Planner' in response.data

    def test_dashboard_requires_login(self, client):
        """Test dashboard requires authentication."""
        response = client.get('/dashboard', follow_redirects=True)
        assert response.status_code == 200
        assert b'Login' in response.data

    def test_dashboard_authenticated(self, auth_client):
        """Test dashboard accessible when authenticated."""
        response = auth_client.get('/dashboard')
        assert response.status_code == 200
        assert b'Welcome' in response.data


class TestAuthRoutes:
    """Test authentication routes."""

    def test_register_page(self, client):
        """Test registration page loads."""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Register' in response.data

    def test_login_page(self, client):
        """Test login page loads."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data

    def test_register_user(self, client, app):
        """Test user registration."""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Registration successful' in response.data

        with app.app_context():
            user = User.query.filter_by(email='new@example.com').first()
            assert user is not None
            assert user.username == 'newuser'

    def test_login_user(self, client, app):
        """Test user login."""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('testpassword')
            db.session.add(user)
            db.session.commit()

        response = client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'testpassword'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Login successful' in response.data

    def test_logout(self, auth_client):
        """Test user logout."""
        response = auth_client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'logged out' in response.data


class TestMealRoutes:
    """Test meal planning routes."""

    def test_preferences_requires_login(self, client):
        """Test preferences requires authentication."""
        response = client.get('/meals/preferences', follow_redirects=True)
        assert response.status_code == 200
        assert b'Login' in response.data

    def test_preferences_page(self, auth_client):
        """Test preferences page loads."""
        response = auth_client.get('/meals/preferences')
        assert response.status_code == 200
        assert b'Meal Preferences' in response.data

    def test_generate_requires_preferences(self, auth_client):
        """Test generate redirects to preferences if none set."""
        response = auth_client.get('/meals/generate', follow_redirects=True)
        assert response.status_code == 200
        assert b'Please set your meal preferences first' in response.data

    def test_history_page(self, auth_client):
        """Test history page loads."""
        response = auth_client.get('/meals/history')
        assert response.status_code == 200
        assert b'History' in response.data


class TestModels:
    """Test database models."""

    def test_user_password_hashing(self, app):
        """Test password hashing works correctly."""
        with app.app_context():
            user = User(username='test', email='test@test.com')
            user.set_password('testpassword')
            assert user.check_password('testpassword')
            assert not user.check_password('wrongpassword')

    def test_user_creation(self, app):
        """Test user model creation."""
        with app.app_context():
            user = User(username='test', email='test@test.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()

            retrieved = User.query.filter_by(username='test').first()
            assert retrieved is not None
            assert retrieved.email == 'test@test.com'

    def test_meal_preference_creation(self, app):
        """Test meal preference model creation."""
        with app.app_context():
            user = User(username='test', email='test@test.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()

            pref = MealPreference(
                user_id=user.id,
                primary_goal='fitness',
                meals_per_day=3
            )
            db.session.add(pref)
            db.session.commit()

            retrieved = MealPreference.query.filter_by(user_id=user.id).first()
            assert retrieved is not None
            assert retrieved.primary_goal == 'fitness'
