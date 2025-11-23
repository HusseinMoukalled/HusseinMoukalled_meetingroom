from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from shared.database import get_db
from rooms_service.app import models
from rooms_service.app.schemas import RoomCreate, RoomUpdate, RoomResponse, RoomStatusResponse
from users_service.app.deps import get_current_user, require_admin, require_regular_user_or_above
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

@router.post("/add", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def add_room(
    data: RoomCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    """
    Add a new meeting room to the system.
    
    - **name**: Name of the room
    - **capacity**: Maximum capacity of the room
    - **equipment**: Available equipment (optional)
    - **location**: Location of the room (optional)
    
    Requires admin role.
    """
    # Validate capacity
    if data.capacity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Capacity must be greater than 0"
        )
    
    # Sanitize inputs
    name = sanitize_string(data.name)
    equipment = sanitize_string(data.equipment) if data.equipment else None
    location = sanitize_string(data.location) if data.location else None
    
    # Check if room with same name already exists
    existing = db.query(models.Room).filter(models.Room.name == name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room with this name already exists"
        )
    
    room = models.Room(
        name=name,
        capacity=data.capacity,
        equipment=equipment,
        location=location,
        is_available=True
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return room

@router.put("/update/{room_id}", response_model=RoomResponse)
def update_room(
    room_id: int,
    data: RoomUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    """
    Update room details.
    
    - **name**: New name (optional)
    - **capacity**: New capacity (optional)
    - **equipment**: New equipment list (optional)
    - **location**: New location (optional)
    - **is_available**: Availability status (optional)
    
    Requires admin role.
    """
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    if data.name is not None:
        name = sanitize_string(data.name)
        # Check if another room with this name exists
        existing = db.query(models.Room).filter(
            and_(models.Room.name == name, models.Room.id != room_id)
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Room with this name already exists"
            )
        room.name = name
    
    if data.capacity is not None:
        if data.capacity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Capacity must be greater than 0"
            )
        room.capacity = data.capacity
    
    if data.equipment is not None:
        room.equipment = sanitize_string(data.equipment)
    
    if data.location is not None:
        room.location = sanitize_string(data.location)
    
    if data.is_available is not None:
        room.is_available = data.is_available

    db.commit()
    db.refresh(room)
    return room

@router.delete("/delete/{room_id}", status_code=status.HTTP_200_OK)
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    """
    Delete a room from the system.
    
    Requires admin role.
    """
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    
    db.delete(room)
    db.commit()
    return {"detail": "Room deleted successfully"}

@router.get("/available", response_model=list[RoomResponse])
def get_available_rooms(
    capacity: int | None = None,
    location: str | None = None,
    equipment: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_regular_user_or_above)
):
    """
    Retrieve available rooms based on filters.
    
    - **capacity**: Minimum capacity required (optional)
    - **location**: Filter by location (optional)
    - **equipment**: Filter by equipment (optional)
    
    Regular users and above can access this endpoint.
    """
    query = db.query(models.Room).filter(models.Room.is_available == True)
    
    if capacity is not None:
        if capacity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Capacity must be greater than 0"
            )
        query = query.filter(models.Room.capacity >= capacity)
    
    if location is not None:
        location = sanitize_string(location)
        query = query.filter(models.Room.location.contains(location))
    
    if equipment is not None:
        equipment = sanitize_string(equipment)
        query = query.filter(models.Room.equipment.contains(equipment))
    
    return query.all()

@router.get("/status/{room_id}", response_model=RoomStatusResponse)
def get_room_status(
    room_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_regular_user_or_above)
):
    """
    Get the availability status of a specific room.
    
    Regular users and above can access this endpoint.
    """
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    return RoomStatusResponse(room_id=room.id, is_available=room.is_available)

@router.get("/{room_id}", response_model=RoomResponse)
def get_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_regular_user_or_above)
):
    """
    Get details of a specific room by ID.
    
    Regular users and above can access this endpoint.
    """
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    return room

@router.get("/", response_model=list[RoomResponse])
def get_all_rooms(
    db: Session = Depends(get_db),
    current_user=Depends(require_regular_user_or_above)
):
    """
    Get all rooms in the system.
    
    Regular users and above can access this endpoint.
    """
    return db.query(models.Room).all()
