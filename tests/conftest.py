import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared.database import Base, get_db
from users_service.app.main import app as users_app
from rooms_service.app.main import app as rooms_app
from bookings_service.app.main import app as bookings_app
from reviews_service.app.main import app as reviews_app
import os

# Use test database
TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/test_meetingroom_db"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def users_client():
    """Create a test client for users service."""
    users_app.dependency_overrides[get_db] = override_get_db
    with TestClient(users_app) as client:
        yield client
    users_app.dependency_overrides.clear()

@pytest.fixture
def rooms_client():
    """Create a test client for rooms service."""
    rooms_app.dependency_overrides[get_db] = override_get_db
    with TestClient(rooms_app) as client:
        yield client
    rooms_app.dependency_overrides.clear()

@pytest.fixture
def bookings_client():
    """Create a test client for bookings service."""
    bookings_app.dependency_overrides[get_db] = override_get_db
    with TestClient(bookings_app) as client:
        yield client
    bookings_app.dependency_overrides.clear()

@pytest.fixture
def reviews_client():
    """Create a test client for reviews service."""
    reviews_app.dependency_overrides[get_db] = override_get_db
    with TestClient(reviews_app) as client:
        yield client
    reviews_app.dependency_overrides.clear()

@pytest.fixture
def admin_token(users_client):
    """Create an admin user and return token."""
    # Register admin user
    response = users_client.post("/users/register", json={
        "name": "Admin User",
        "username": "admin",
        "email": "admin@test.com",
        "password": "admin123",
        "role": "admin"
    })
    # Login
    response = users_client.post("/users/login", json={
        "username": "admin",
        "password": "admin123"
    })
    return response.json()["access_token"]

@pytest.fixture
def regular_user_token(users_client):
    """Create a regular user and return token."""
    # Register regular user
    response = users_client.post("/users/register", json={
        "name": "Regular User",
        "username": "user1",
        "email": "user1@test.com",
        "password": "user123",
        "role": "regular_user"
    })
    # Login
    response = users_client.post("/users/login", json={
        "username": "user1",
        "password": "user123"
    })
    return response.json()["access_token"]

@pytest.fixture
def moderator_token(users_client):
    """Create a moderator user and return token."""
    # Register moderator user
    response = users_client.post("/users/register", json={
        "name": "Moderator User",
        "username": "moderator",
        "email": "moderator@test.com",
        "password": "mod123",
        "role": "moderator"
    })
    # Login
    response = users_client.post("/users/login", json={
        "username": "moderator",
        "password": "mod123"
    })
    return response.json()["access_token"]

