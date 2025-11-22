from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from shared.database import get_db
from reviews_service.app import models
from reviews_service.app.schemas import (
    ReviewCreate,
    UpdateReview,
    FlagReview,
    ReviewResponse
)

router = APIRouter()


@router.post("/create", response_model=ReviewResponse)
def create_review(data: ReviewCreate, db: Session = Depends(get_db)):

    review = models.Review(
        username=data.username,
        room_id=data.room_id,
        rating=data.rating,
        comment=data.comment
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return review


@router.get("/{review_id}", response_model=ReviewResponse)
def get_review(review_id: int, db: Session = Depends(get_db)):
    review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.get("/room/{room_id}", response_model=list[ReviewResponse])
def get_reviews_for_room(room_id: int, db: Session = Depends(get_db)):
    return db.query(models.Review).filter(models.Review.room_id == room_id).all()


@router.get("/user/{username}", response_model=list[ReviewResponse])
def get_reviews_by_user(username: str, db: Session = Depends(get_db)):
    return db.query(models.Review).filter(models.Review.username == username).all()


@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(review_id: int, data: UpdateReview, db: Session = Depends(get_db)):
    review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if data.rating is not None:
        review.rating = data.rating

    if data.comment is not None:
        review.comment = data.comment

    db.commit()
    db.refresh(review)

    return review


@router.post("/{review_id}/flag", response_model=ReviewResponse)
def flag_review(review_id: int, data: FlagReview, db: Session = Depends(get_db)):
    review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    review.is_flagged = True
    review.flag_reason = data.reason

    db.commit()
    db.refresh(review)

    return review


@router.delete("/{review_id}")
def delete_review(review_id: int, username: str, db: Session = Depends(get_db)):
    review = db.query(models.Review).filter(models.Review.id == review_id).first()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.username != username:
        raise HTTPException(status_code=403, detail="You can only delete your own review")

    db.delete(review)
    db.commit()

    return {"detail": "Review deleted"}
