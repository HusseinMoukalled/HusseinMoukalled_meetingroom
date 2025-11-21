from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from typing import List
from shared.database import get_db
from app import models
from app.schemas import BookingCreate,BookingUpdate,BookingResponse,AvailabilityResponse

router=APIRouter()

def to_response(b:models.Booking)->BookingResponse:
    return BookingResponse(
        id=b.id,
        username=b.username,
        room_id=b.room_id,
        date=str(b.date),
        start_time=str(b.start_time),
        end_time=str(b.end_time)
    )

def overlap(b,start,end):
    return not (end<=b.start_time or start>=b.end_time)

@router.get("/",response_model=List[BookingResponse])
def view_all(db:Session=Depends(get_db)):
    bookings=db.query(models.Booking).all()
    return [to_response(b) for b in bookings]

@router.post("/add",response_model=BookingResponse)
def make_booking(data:BookingCreate,db:Session=Depends(get_db)):
    room=db.query(models.Room).filter(models.Room.id==data.room_id).first()
    if not room:
        raise HTTPException(status_code=404,detail="Room not found")
    existing=db.query(models.Booking).filter(
        models.Booking.room_id==data.room_id,
        models.Booking.date==data.date
    ).all()
    for b in existing:
        if overlap(b,data.start_time,data.end_time):
            raise HTTPException(status_code=400,detail="Room is already booked at that time")
    booking=models.Booking(
        username=data.username,
        room_id=data.room_id,
        date=data.date,
        start_time=data.start_time,
        end_time=data.end_time
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return to_response(booking)

@router.put("/{booking_id}",response_model=BookingResponse)
def update_booking(booking_id:int,data:BookingUpdate,db:Session=Depends(get_db)):
    booking=db.query(models.Booking).filter(models.Booking.id==booking_id).first()
    if not booking:
        raise HTTPException(status_code=404,detail="Booking not found")
    if data.room_id is not None:
        booking.room_id=data.room_id
    if data.date is not None:
        booking.date=data.date
    if data.start_time is not None:
        booking.start_time=data.start_time
    if data.end_time is not None:
        booking.end_time=data.end_time
    conflict=db.query(models.Booking).filter(
        models.Booking.room_id==booking.room_id,
        models.Booking.date==booking.date,
        models.Booking.id!=booking_id
    ).all()
    for b in conflict:
        if overlap(b,booking.start_time,booking.end_time):
            raise HTTPException(status_code=400,detail="Room is already booked at that time")
    db.commit()
    db.refresh(booking)
    return to_response(booking)

@router.delete("/{booking_id}")
def cancel_booking(booking_id:int,db:Session=Depends(get_db)):
    booking=db.query(models.Booking).filter(models.Booking.id==booking_id).first()
    if not booking:
        raise HTTPException(status_code=404,detail="Booking not found")
    db.delete(booking)
    db.commit()
    return {"detail":"Booking canceled"}

@router.get("/available/{room_id}",response_model=AvailabilityResponse)
def check_availability(room_id:int,date:str,start_time:str,end_time:str,db:Session=Depends(get_db)):
    room=db.query(models.Room).filter(models.Room.id==room_id).first()
    if not room:
        raise HTTPException(status_code=404,detail="Room not found")
    existing=db.query(models.Booking).filter(
        models.Booking.room_id==room_id,
        models.Booking.date==date
    ).all()
    for b in existing:
        if overlap(b,start_time,end_time):
            return AvailabilityResponse(room_id=room_id,available=False)
    return AvailabilityResponse(room_id=room_id,available=True)

@router.get("/history/{username}",response_model=List[BookingResponse])
def booking_history(username:str,db:Session=Depends(get_db)):
    bookings=db.query(models.Booking).filter(models.Booking.username==username).all()
    return [to_response(b) for b in bookings]
