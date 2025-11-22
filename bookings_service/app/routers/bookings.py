from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from shared.database import get_db
from bookings_service.app import models
from bookings_service.app.schemas import (
    BookingCreate,
    BookingUpdate,
    BookingResponse
)
from users_service.app.deps import get_current_user

router = APIRouter()

@router.post("/create", response_model=BookingResponse)
def create_booking(data: BookingCreate, db: Session = Depends(get_db)):
    overlap = db.query(models.Booking).filter(
        models.Booking.room_id == data.room_id,
        models.Booking.date == data.date,
        models.Booking.start_time < data.end_time,
        models.Booking.end_time > data.start_time
    ).first()

    if overlap:
        raise HTTPException(status_code=400, detail="Room already booked for this time")

    booking = models.Booking(
        username=data.username,
        room_id=data.room_id,
        date=data.date,
        start_time=data.start_time,
        end_time=data.end_time
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

@router.get("/", response_model=list[BookingResponse])
def get_all_bookings(db: Session = Depends(get_db)):
    return db.query(models.Booking).all()

@router.get("/user/{username}", response_model=list[BookingResponse])
def get_user_bookings(username: str, db: Session = Depends(get_db)):
    return db.query(models.Booking).filter(models.Booking.username == username).all()

@router.get("/check", response_model=dict)
def check_room(room_id: int, date: str, start_time: str, end_time: str, db: Session = Depends(get_db)):
    conflict = db.query(models.Booking).filter(
        models.Booking.room_id == room_id,
        models.Booking.date == date,
        models.Booking.start_time < end_time,
        models.Booking.end_time > start_time
    ).first()

    return {"available": conflict is None}

@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@router.put("/{booking_id}", response_model=BookingResponse)
def update_booking(booking_id: int, data: BookingUpdate, db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if data.date is not None:
        booking.date = data.date
    if data.start_time is not None:
        booking.start_time = data.start_time
    if data.end_time is not None:
        booking.end_time = data.end_time

    db.commit()
    db.refresh(booking)
    return booking

@router.delete("/{booking_id}")
def delete_booking(booking_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.username != current_user["sub"]:
        raise HTTPException(status_code=403, detail="You can only delete your own bookings")

    db.delete(booking)
    db.commit()
    return {"detail": "Booking deleted"}
