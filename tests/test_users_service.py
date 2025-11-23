import pytest
from fastapi import status

def test_register_user(users_client):
    """Test user registration."""
    response = users_client.post("/users/register", json={
        "name": "Test User",
        "username": "testuser",
        "email": "test@example.com",
        "password": "test123",
        "role": "regular_user"
    })
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["username"] == "testuser"
    assert response.json()["email"] == "test@example.com"
    assert response.json()["role"] == "regular_user"
    assert "hashed_password" not in response.json()

def test_register_duplicate_username(users_client):
    """Test registration with duplicate username."""
    users_client.post("/users/register", json={
        "name": "Test User",
        "username": "testuser",
        "email": "test@example.com",
        "password": "test123",
        "role": "regular_user"
    })
    response = users_client.post("/users/register", json={
        "name": "Another User",
        "username": "testuser",
        "email": "another@example.com",
        "password": "test123",
        "role": "regular_user"
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_login_success(users_client):
    """Test successful login."""
    users_client.post("/users/register", json={
        "name": "Test User",
        "username": "testuser",
        "email": "test@example.com",
        "password": "test123",
        "role": "regular_user"
    })
    response = users_client.post("/users/login", json={
        "username": "testuser",
        "password": "test123"
    })
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_invalid_credentials(users_client):
    """Test login with invalid credentials."""
    response = users_client.post("/users/login", json={
        "username": "nonexistent",
        "password": "wrongpass"
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_all_users_requires_admin(users_client, regular_user_token):
    """Test that getting all users requires admin role."""
    response = users_client.get(
        "/users/",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_get_all_users_admin(users_client, admin_token):
    """Test admin can get all users."""
    response = users_client.get(
        "/users/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_get_user_profile(users_client, regular_user_token):
    """Test getting own user profile."""
    response = users_client.get(
        "/users/user1",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "user1"

def test_update_user_profile(users_client, regular_user_token):
    """Test updating own profile."""
    response = users_client.put(
        "/users/user1",
        headers={"Authorization": f"Bearer {regular_user_token}"},
        json={
            "name": "Updated Name",
            "email": "updated@example.com"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Updated Name"
    assert response.json()["email"] == "updated@example.com"

def test_delete_user_requires_admin(users_client, regular_user_token):
    """Test that deleting users requires admin role."""
    response = users_client.delete(
        "/users/user1",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_delete_user_admin(users_client, admin_token):
    """Test admin can delete users."""
    # First create a user to delete
    users_client.post("/users/register", json={
        "name": "To Delete",
        "username": "todelete",
        "email": "delete@example.com",
        "password": "test123",
        "role": "regular_user"
    })
    response = users_client.delete(
        "/users/todelete",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK

