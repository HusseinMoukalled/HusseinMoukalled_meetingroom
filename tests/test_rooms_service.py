import pytest
from fastapi import status

def test_add_room_requires_admin(rooms_client, regular_user_token):
    """Test that adding rooms requires admin role."""
    response = rooms_client.post(
        "/rooms/add",
        headers={"Authorization": f"Bearer {regular_user_token}"},
        json={
            "name": "Test Room",
            "capacity": 10,
            "equipment": "Projector, Whiteboard",
            "location": "Building A"
        }
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_add_room_admin(rooms_client, admin_token):
    """Test admin can add rooms."""
    response = rooms_client.post(
        "/rooms/add",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Test Room",
            "capacity": 10,
            "equipment": "Projector, Whiteboard",
            "location": "Building A"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == "Test Room"
    assert response.json()["capacity"] == 10
    assert response.json()["is_available"] == True

def test_get_available_rooms(rooms_client, admin_token, regular_user_token):
    """Test getting available rooms."""
    # Admin adds a room
    rooms_client.post(
        "/rooms/add",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Room 1",
            "capacity": 5,
            "location": "Building A"
        }
    )
    # Regular user can view available rooms
    response = rooms_client.get(
        "/rooms/available",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 0

def test_get_available_rooms_with_filters(rooms_client, admin_token, regular_user_token):
    """Test getting available rooms with filters."""
    # Add rooms
    rooms_client.post(
        "/rooms/add",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Small Room",
            "capacity": 5,
            "location": "Building A"
        }
    )
    rooms_client.post(
        "/rooms/add",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Large Room",
            "capacity": 20,
            "location": "Building B"
        }
    )
    # Filter by capacity
    response = rooms_client.get(
        "/rooms/available?capacity=10",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert all(room["capacity"] >= 10 for room in response.json())

def test_update_room_requires_admin(rooms_client, admin_token, regular_user_token):
    """Test that updating rooms requires admin role."""
    # Admin creates room
    response = rooms_client.post(
        "/rooms/add",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Test Room",
            "capacity": 10
        }
    )
    room_id = response.json()["id"]
    
    # Regular user tries to update
    response = rooms_client.put(
        f"/rooms/update/{room_id}",
        headers={"Authorization": f"Bearer {regular_user_token}"},
        json={"capacity": 15}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_update_room_admin(rooms_client, admin_token):
    """Test admin can update rooms."""
    # Create room
    response = rooms_client.post(
        "/rooms/add",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Test Room",
            "capacity": 10
        }
    )
    room_id = response.json()["id"]
    
    # Update room
    response = rooms_client.put(
        f"/rooms/update/{room_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"capacity": 15, "is_available": False}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["capacity"] == 15
    assert response.json()["is_available"] == False

def test_delete_room_requires_admin(rooms_client, admin_token, regular_user_token):
    """Test that deleting rooms requires admin role."""
    # Admin creates room
    response = rooms_client.post(
        "/rooms/add",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Test Room",
            "capacity": 10
        }
    )
    room_id = response.json()["id"]
    
    # Regular user tries to delete
    response = rooms_client.delete(
        f"/rooms/delete/{room_id}",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_get_room_status(rooms_client, admin_token, regular_user_token):
    """Test getting room status."""
    # Admin creates room
    response = rooms_client.post(
        "/rooms/add",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Test Room",
            "capacity": 10
        }
    )
    room_id = response.json()["id"]
    
    # Regular user can check status
    response = rooms_client.get(
        f"/rooms/status/{room_id}",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "is_available" in response.json()

