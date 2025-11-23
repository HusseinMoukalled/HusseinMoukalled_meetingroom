import pytest
from fastapi import status

def test_create_review(reviews_client, rooms_client, admin_token, regular_user_token):
    """Test creating a review."""
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
    
    # Regular user creates review
    response = reviews_client.post(
        "/reviews/create",
        headers={"Authorization": f"Bearer {regular_user_token}"},
        json={
            "username": "user1",
            "room_id": room_id,
            "rating": 5,
            "comment": "Great room!"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["rating"] == 5
    assert response.json()["username"] == "user1"

def test_create_review_invalid_rating(reviews_client, rooms_client, admin_token, regular_user_token):
    """Test creating review with invalid rating."""
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
    
    # Try to create review with invalid rating
    response = reviews_client.post(
        "/reviews/create",
        headers={"Authorization": f"Bearer {regular_user_token}"},
        json={
            "username": "user1",
            "room_id": room_id,
            "rating": 10,  # Invalid rating
            "comment": "Test"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_get_reviews_for_room(reviews_client, rooms_client, admin_token, regular_user_token):
    """Test getting reviews for a room."""
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
    
    # Create review
    reviews_client.post(
        "/reviews/create",
        headers={"Authorization": f"Bearer {regular_user_token}"},
        json={
            "username": "user1",
            "room_id": room_id,
            "rating": 5,
            "comment": "Great room!"
        }
    )
    
    # Get reviews for room
    response = reviews_client.get(
        f"/reviews/room/{room_id}",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 0

def test_update_review(reviews_client, rooms_client, admin_token, regular_user_token):
    """Test updating a review."""
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
    
    # Create review
    review_response = reviews_client.post(
        "/reviews/create",
        headers={"Authorization": f"Bearer {regular_user_token}"},
        json={
            "username": "user1",
            "room_id": room_id,
            "rating": 3,
            "comment": "Okay room"
        }
    )
    review_id = review_response.json()["id"]
    
    # Update review
    response = reviews_client.put(
        f"/reviews/{review_id}",
        headers={"Authorization": f"Bearer {regular_user_token}"},
        json={
            "rating": 5,
            "comment": "Actually great room!"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["rating"] == 5

def test_flag_review(reviews_client, rooms_client, admin_token, regular_user_token):
    """Test flagging a review."""
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
    
    # Create review
    review_response = reviews_client.post(
        "/reviews/create",
        headers={"Authorization": f"Bearer {regular_user_token}"},
        json={
            "username": "user1",
            "room_id": room_id,
            "rating": 5,
            "comment": "Test review"
        }
    )
    review_id = review_response.json()["id"]
    
    # Flag review
    response = reviews_client.post(
        f"/reviews/{review_id}/flag",
        headers={"Authorization": f"Bearer {regular_user_token}"},
        json={
            "reason": "Inappropriate content"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["is_flagged"] == True

def test_get_flagged_reviews_requires_moderator(reviews_client, regular_user_token):
    """Test that getting flagged reviews requires moderator role."""
    response = reviews_client.get(
        "/reviews/flagged/all",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_get_flagged_reviews_moderator(reviews_client, rooms_client, admin_token, moderator_token, regular_user_token):
    """Test moderator can get flagged reviews."""
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
    
    # Create and flag review
    review_response = reviews_client.post(
        "/reviews/create",
        headers={"Authorization": f"Bearer {regular_user_token}"},
        json={
            "username": "user1",
            "room_id": room_id,
            "rating": 5,
            "comment": "Test"
        }
    )
    review_id = review_response.json()["id"]
    
    reviews_client.post(
        f"/reviews/{review_id}/flag",
        headers={"Authorization": f"Bearer {regular_user_token}"},
        json={"reason": "Test flag"}
    )
    
    # Moderator gets flagged reviews
    response = reviews_client.get(
        "/reviews/flagged/all",
        headers={"Authorization": f"Bearer {moderator_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 0

def test_delete_review(reviews_client, rooms_client, admin_token, regular_user_token):
    """Test deleting a review."""
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
    
    # Create review
    review_response = reviews_client.post(
        "/reviews/create",
        headers={"Authorization": f"Bearer {regular_user_token}"},
        json={
            "username": "user1",
            "room_id": room_id,
            "rating": 5,
            "comment": "Test review"
        }
    )
    review_id = review_response.json()["id"]
    
    # Delete review
    response = reviews_client.delete(
        f"/reviews/{review_id}",
        headers={"Authorization": f"Bearer {regular_user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK

