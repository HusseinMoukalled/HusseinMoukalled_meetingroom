from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from typing import List
from shared.database import get_db
from app import models
from app.schemas import ReviewCreate,ReviewUpdate,ReviewResponse,FlagReview

router=APIRouter()

def to_response(r:models.Review)->ReviewResponse:
    return ReviewResponse(
        id=r.id,
        username=r.username,
        room_id=r.room_id,
        rating=r.rating,
        comment=r.comment,
        flagged=r.flagged
    )

@router.post("/add",response_model=ReviewResponse)
def submit_review(data:ReviewCreate,db:Session=Depends(get_db)):
    room=db.query(models.Room).filter(models.Room.id==data.room_id).first()
    if not room:
        raise HTTPException(status_code=404,detail="Room not found")
    review=models.Review(
        username=data.username,
        room_id=data.room_id,
        rating=data.rating,
        comment=data.comment
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return to_response(review)

@router.put("/{review_id}",response_model=ReviewResponse)
def update_review(review_id:int,data:ReviewUpdate,db:Session=Depends(get_db)):
    review=db.query(models.Review).filter(models.Review.id==review_id).first()
    if not review:
        raise HTTPException(status_code=404,detail="Review not found")
    if data.rating is not None:
        review.rating=data.rating
    if data.comment is not None:
        review.comment=data.comment
    db.commit()
    db.refresh(review)
    return to_response(review)

@router.delete("/{review_id}")
def delete_review(review_id:int,db:Session=Depends(get_db)):
    review=db.query(models.Review).filter(models.Review.id==review_id).first()
    if not review:
        raise HTTPException(status_code=404,detail="Review not found")
    db.delete(review)
    db.commit()
    return {"detail":"Review deleted"}

@router.get("/room/{room_id}",response_model=List[ReviewResponse])
def get_reviews(room_id:int,db:Session=Depends(get_db)):
    room=db.query(models.Room).filter(models.Room.id==room_id).first()
    if not room:
        raise HTTPException(status_code=404,detail="Room not found")
    reviews=db.query(models.Review).filter(models.Review.room_id==room_id).all()
    return [to_response(r) for r in reviews]

@router.post("/{review_id}/flag",response_model=ReviewResponse)
def flag_review(review_id:int,data:FlagReview,db:Session=Depends(get_db)):
    review=db.query(models.Review).filter(models.Review.id==review_id).first()
    if not review:
        raise HTTPException(status_code=404,detail="Review not found")
    review.flagged=data.reason
    db.commit()
    db.refresh(review)
    return to_response(review)
