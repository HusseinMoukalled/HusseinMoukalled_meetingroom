import pytest
from fastapi import status
from datetime import date, time

def test_create_booking(bookings_client, rooms_client, admin_token, regular_user_token):
    """Test creating a booking."""
    # Admin creates a room
    room_response = rooms_client.post(
        "/rooms/add",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Test Room",
            "capacity": 10
        }
    )
    room_id = room_response.json()["id"]
    
    # Regular user creates booking
    response = bookings_client.post(
        "/bookings/create",
        headers={"Authorization": f"Bearer {regular_user_token}"},
        json={
            "username": "user1",
            "room_id": room_id,
            "date": "2025-12-31",
            "start_time": "10:00:00",
            "end_time": "11:00:00"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["username"] == "user1"
    assert response.json()["room_id"] == room_id

def test_create_booking_overlap(bookings_client, rooms_client, admin_token, regular_user_token):
    """Test that overlapping bookings are prevented."""
    # Admin creates a room
    room_response = rooms_client.post(
        "/rooms/add",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Test Room",
            "capacity": 10
        }
    )
    room_id = room_response.json()["id"]
    
    # Create first booking
    bookings_client.post(
        "/bookings/create",
        headers={"Authorization": f"Bearer {regular_user_token}"},
        json={
            "username": "user1",
            "room_id": room_id,
            "date": "2025-12-31",
            "start_time": "10:00:00",
            "end_time": "11:00:00"
        }
    )
    
    # Try to create overlapping booking
    response = bookings_client.post(
        "/bookings/create",
        headers={"Authorization": f"Bearer {regular_user_token}"},
        json={
            "username": "user1",
            "room_id": room_id,
            "date": "2025-12-31",
            "start_time": "10:30:00",
            "end_time": "11:30:00"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_get_user_bookings(bookings_client, rooms_client, admin_token, regular_user_token):
    """Test getting user's bookings."""
    # Admin creates a room
    room_response = rooms_client.post(
        "/rooms/add",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Test Room",
            "capacity": 10
        }
    )
    room_id = room_response.json()["id"]
    
    # Create booking
    bookings_client.post(
        "/bookings/create",
        headers={"Authorization": f"Bearer {regular_user_token}"},
        json={
            "username": "user1",
            "room_id": room_id,
            "date": "2025-12-31",
            "start_time": "10:00:00",
            "end_time": "11:00:00"
        }
    )
    
    # Get user bookings
    response = bookings_client.get(
        "/bookings/user/user1",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 0

def test_check_room_availability(bookings_client, rooms_client, admin_token, regular_user_token):
    """Test checking room availability."""
    # Admin creates a room
    room_response = rooms_client.post(
        "/rooms/add",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Test Room",
            "capacity": 10
        }
    )
    room_id = room_response.json()["id"]
    
    # Check availability
    response = bookings_client.get(
        f"/bookings/check?room_id={room_id}&date=2025-12-31&start_time=10:00:00&end_time=11:00:00",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "available" in response.json()

def test_update_booking(bookings_client, rooms_client, admin_token, regular_user_token):
    """Test updating a booking."""
    # Admin creates a room
    room_response = rooms_client.post(
        "/rooms/add",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Test Room",
            "capacity": 10
        }
    )
    room_id = room_response.json()["id"]
    
    # Create booking
    booking_response = bookings_client.post(
        "/bookings/create",
        headers={"Authorization": f"Bearer {regular_user_token}"},
        json={
            "username": "user1",
            "room_id": room_id,
            "date": "2025-12-31",
            "start_time": "10:00:00",
            "end_time": "11:00:00"
        }
    )
    booking_id = booking_response.json()["id"]
    
    # Update booking
    response = bookings_client.put(
        f"/bookings/{booking_id}",
        headers={"Authorization": f"Bearer {regular_user_token}"},
        json={
            "start_time": "11:00:00",
            "end_time": "12:00:00"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["start_time"] == "11:00:00"

def test_delete_booking(bookings_client, rooms_client, admin_token, regular_user_token):
    """Test deleting a booking."""
    # Admin creates a room
    room_response = rooms_client.post(
        "/rooms/add",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Test Room",
            "capacity": 10
        }
    )
    room_id = room_response.json()["id"]
    
    # Create booking
    booking_response = bookings_client.post(
        "/bookings/create",
        headers={"Authorization": f"Bearer {regular_user_token}"},
        json={
            "username": "user1",
            "room_id": room_id,
            "date": "2025-12-31",
            "start_time": "10:00:00",
            "end_time": "11:00:00"
        }
    )
    booking_id = booking_response.json()["id"]
    
    # Delete booking
    response = bookings_client.delete(
        f"/bookings/{booking_id}",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK

def test_get_all_bookings_requires_admin(bookings_client, regular_user_token):
    """Test that getting all bookings requires admin."""
    response = bookings_client.get(
        "/bookings/",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

