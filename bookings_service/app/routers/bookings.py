from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date, time
from shared.database import get_db
from bookings_service.app import models
from bookings_service.app.schemas import (
    BookingCreate,
    BookingUpdate,
    BookingResponse
)
from users_service.app.deps import get_current_user, require_admin, require_regular_user_or_above
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
    sanitized = re.sub(r'[;\'"\\]', '', input_str)
    return sanitized.strip()

@router.post("/create", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    data: BookingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_regular_user_or_above)
):
    """
    Create a new booking for a meeting room.
    
    - **username**: Username of the person making the booking (must match current user unless admin)
    - **room_id**: ID of the room to book
    - **date**: Date of the booking (YYYY-MM-DD)
    - **start_time**: Start time (HH:MM:SS)
    - **end_time**: End time (HH:MM:SS)
    
    Regular users can only book for themselves. Admins can book for any user.
    """
    # Validate that user exists and room exists
    user = db.query(user_models.User).filter(user_models.User.username == data.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    room = db.query(room_models.Room).filter(room_models.Room.id == data.room_id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    
    if not room.is_available:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Room is not available")
    
    # Authorization: Regular users can only book for themselves
    if current_user.role != "admin" and current_user.username != data.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create bookings for yourself"
        )
    
    # Validate time range
    if data.start_time >= data.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time"
        )
    
    # Check for overlapping bookings
    overlap = db.query(models.Booking).filter(
        and_(
            models.Booking.room_id == data.room_id,
            models.Booking.date == data.date,
            models.Booking.start_time < data.end_time,
            models.Booking.end_time > data.start_time
        )
    ).first()

    if overlap:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room already booked for this time slot"
        )

    booking = models.Booking(
        username=sanitize_string(data.username),
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
def get_all_bookings(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    """
    Get all bookings in the system.
    
    Requires admin role.
    """
    return db.query(models.Booking).all()

@router.get("/user/{username}", response_model=list[BookingResponse])
def get_user_bookings(
    username: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Get all bookings for a specific user.
    
    Regular users can only view their own bookings. Admins can view any user's bookings.
    """
    # Sanitize username input
    username = sanitize_string(username)
    
    # Authorization check
    if current_user.role != "admin" and current_user.username != username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own bookings"
        )
    
    return db.query(models.Booking).filter(models.Booking.username == username).all()

@router.get("/check", response_model=dict)
def check_room_availability(
    room_id: int,
    date: date,
    start_time: time,
    end_time: time,
    db: Session = Depends(get_db),
    current_user=Depends(require_regular_user_or_above)
):
    """
    Check if a room is available for a specific time slot.
    
    - **room_id**: ID of the room to check
    - **date**: Date to check (YYYY-MM-DD)
    - **start_time**: Start time (HH:MM:SS)
    - **end_time**: End time (HH:MM:SS)
    
    Returns: {"available": true/false}
    """
    # Validate time range
    if start_time >= end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time"
        )
    
    # Check room exists and is available
    room = db.query(room_models.Room).filter(room_models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    
    if not room.is_available:
        return {"available": False}
    
    # Check for conflicts
    conflict = db.query(models.Booking).filter(
        and_(
            models.Booking.room_id == room_id,
            models.Booking.date == date,
            models.Booking.start_time < end_time,
            models.Booking.end_time > start_time
        )
    ).first()

    return {"available": conflict is None}

@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Get a specific booking by ID.
    
    Regular users can only view their own bookings. Admins can view any booking.
    """
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    # Authorization check
    if current_user.role != "admin" and current_user.username != booking.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own bookings"
        )
    
    return booking

@router.put("/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: int,
    data: BookingUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Update an existing booking.
    
    Regular users can only update their own bookings. Admins can update any booking.
    """
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    # Authorization check
    if current_user.role != "admin" and current_user.username != booking.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own bookings"
        )
    
    # Validate time range if updating times
    start_time = data.start_time if data.start_time is not None else booking.start_time
    end_time = data.end_time if data.end_time is not None else booking.end_time
    booking_date = data.date if data.date is not None else booking.date
    
    if start_time >= end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time"
        )
    
    # Check for conflicts if updating time/date
    if data.date is not None or data.start_time is not None or data.end_time is not None:
        overlap = db.query(models.Booking).filter(
            and_(
                models.Booking.id != booking_id,
                models.Booking.room_id == booking.room_id,
                models.Booking.date == booking_date,
                models.Booking.start_time < end_time,
                models.Booking.end_time > start_time
            )
        ).first()
        
        if overlap:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Room already booked for this time slot"
            )
    
    if data.date is not None:
        booking.date = data.date
    if data.start_time is not None:
        booking.start_time = data.start_time
    if data.end_time is not None:
        booking.end_time = data.end_time

    db.commit()
    db.refresh(booking)
    return booking

@router.delete("/{booking_id}", status_code=status.HTTP_200_OK)
def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Cancel/delete a booking.
    
    Regular users can only delete their own bookings. Admins can delete any booking.
    """
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()

    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    # Authorization check
    if current_user.role != "admin" and current_user.username != booking.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own bookings"
        )

    db.delete(booking)
    db.commit()
    return {"detail": "Booking deleted successfully"}
