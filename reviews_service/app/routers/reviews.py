from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from shared.database import get_db
from reviews_service.app import models
from reviews_service.app.schemas import (
    ReviewCreate,
    UpdateReview,
    FlagReview,
    ReviewResponse
)
from users_service.app.deps import get_current_user, require_admin, require_moderator, require_regular_user_or_above
from users_service.app import models as user_models
from rooms_service.app import models as room_models
import re

router = APIRouter()

def sanitize_string(input_str: str) -> str:
    """
    Sanitize string input to prevent SQL injection and XSS attacks.
    
    Args:
        input_str: Input string to sanitize
        
    Returns:
        str: Sanitized string
    """
    if not input_str:
        return ""
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[;\'"\\<>]', '', input_str)
    return sanitized.strip()

def validate_rating(rating: int) -> bool:
    """
    Validate that rating is between 1 and 5.
    
    Args:
        rating: Rating value to validate
        
    Returns:
        bool: True if valid
    """
    return 1 <= rating <= 5

@router.post("/create", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_regular_user_or_above)
):
    """
    Submit a review for a meeting room.
    
    - **username**: Username of the reviewer (must match current user unless admin)
    - **room_id**: ID of the room being reviewed
    - **rating**: Rating from 1 to 5
    - **comment**: Review comment (optional)
    
    Regular users can only submit reviews for themselves. Admins can submit for any user.
    """
    # Validate rating
    if not validate_rating(data.rating):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5"
        )
    
    # Authorization: Regular users can only review for themselves
    if current_user.role != "admin" and current_user.username != data.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only submit reviews for yourself"
        )
    
    # Validate user exists
    user = db.query(user_models.User).filter(user_models.User.username == data.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Validate room exists
    room = db.query(room_models.Room).filter(room_models.Room.id == data.room_id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    
    # Sanitize comment
    comment = sanitize_string(data.comment) if data.comment else None
    
    # Check if user already reviewed this room
    existing = db.query(models.Review).filter(
        models.Review.username == data.username,
        models.Review.room_id == data.room_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this room. Please update your existing review."
        )

    review = models.Review(
        username=sanitize_string(data.username),
        room_id=data.room_id,
        rating=data.rating,
        comment=comment,
        is_flagged=False
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return review


@router.get("/{review_id}", response_model=ReviewResponse)
def get_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_regular_user_or_above)
):
    """
    Get a specific review by ID.
    
    Regular users and above can access this endpoint.
    """
    review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    return review


@router.get("/room/{room_id}", response_model=list[ReviewResponse])
def get_reviews_for_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_regular_user_or_above)
):
    """
    Get all reviews for a specific room.
    
    Regular users and above can access this endpoint.
    """
    # Validate room exists
    room = db.query(room_models.Room).filter(room_models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    
    return db.query(models.Review).filter(models.Review.room_id == room_id).all()


@router.get("/user/{username}", response_model=list[ReviewResponse])
def get_reviews_by_user(
    username: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Get all reviews by a specific user.
    
    Regular users can only view their own reviews. Admins can view any user's reviews.
    """
    # Sanitize username
    username = sanitize_string(username)
    
    # Authorization check
    if current_user.role != "admin" and current_user.username != username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own reviews"
        )
    
    return db.query(models.Review).filter(models.Review.username == username).all()


@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    data: UpdateReview,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Update an existing review.
    
    Regular users can only update their own reviews. Admins can update any review.
    """
    review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    
    # Authorization check
    if current_user.role != "admin" and current_user.username != review.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own reviews"
        )
    
    # Validate rating if provided
    if data.rating is not None:
        if not validate_rating(data.rating):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 1 and 5"
            )
        review.rating = data.rating

    if data.comment is not None:
        review.comment = sanitize_string(data.comment)

    db.commit()
    db.refresh(review)

    return review


@router.post("/{review_id}/flag", response_model=ReviewResponse)
def flag_review(
    review_id: int,
    data: FlagReview,
    db: Session = Depends(get_db),
    current_user=Depends(require_regular_user_or_above)
):
    """
    Flag a review as inappropriate.
    
    Regular users and above can flag reviews. This allows moderation by admins/moderators.
    """
    review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    
    # Sanitize reason
    reason = sanitize_string(data.reason)
    
    review.is_flagged = True
    review.flag_reason = reason

    db.commit()
    db.refresh(review)

    return review


@router.post("/{review_id}/unflag", response_model=ReviewResponse)
def unflag_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_moderator)
):
    """
    Unflag a review (clear the flag).
    
    Requires moderator or admin role.
    """
    review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    
    review.is_flagged = False
    review.flag_reason = None

    db.commit()
    db.refresh(review)

    return review


@router.get("/flagged/all", response_model=list[ReviewResponse])
def get_flagged_reviews(
    db: Session = Depends(get_db),
    current_user=Depends(require_moderator)
):
    """
    Get all flagged reviews for moderation.
    
    Requires moderator or admin role.
    """
    return db.query(models.Review).filter(models.Review.is_flagged == True).all()


@router.delete("/{review_id}", status_code=status.HTTP_200_OK)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Delete a review.
    
    Regular users can only delete their own reviews. Admins and moderators can delete any review.
    """
    review = db.query(models.Review).filter(models.Review.id == review_id).first()

    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    # Authorization: Users can delete their own reviews, admins/moderators can delete any
    if current_user.role not in ["admin", "moderator"] and current_user.username != review.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own reviews"
        )

    db.delete(review)
    db.commit()

    return {"detail": "Review deleted successfully"}


@router.get("/", response_model=list[ReviewResponse])
def get_all_reviews(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    """
    Get all reviews in the system.
    
    Requires admin role.
    """
    return db.query(models.Review).all()
