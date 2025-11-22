from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from shared.database import get_db
from rooms_service.app import models
from rooms_service.app.schemas import RoomCreate, RoomUpdate, RoomResponse, RoomStatusResponse

router = APIRouter()

@router.post("/add", response_model=RoomResponse)
def add_room(data: RoomCreate, db: Session = Depends(get_db)):
    room = models.Room(
        name=data.name,
        capacity=data.capacity,
        equipment=data.equipment,
        location=data.location
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return room

@router.put("/update/{room_id}", response_model=RoomResponse)
def update_room(room_id: int, data: RoomUpdate, db: Session = Depends(get_db)):
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if data.name is not None:
        room.name = data.name
    if data.capacity is not None:
        room.capacity = data.capacity
    if data.equipment is not None:
        room.equipment = data.equipment
    if data.location is not None:
        room.location = data.location
    if data.is_available is not None:
        room.is_available = data.is_available

    db.commit()
    db.refresh(room)
    return room

@router.delete("/delete/{room_id}")
def delete_room(room_id: int, db: Session = Depends(get_db)):
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    db.delete(room)
    db.commit()
    return {"detail": "Room deleted"}

@router.get("/available", response_model=list[RoomResponse])
def get_available_rooms(capacity: int | None = None, location: str | None = None, equipment: str | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Room).filter(models.Room.is_available == True)
    if capacity is not None:
        query = query.filter(models.Room.capacity >= capacity)
    if location is not None:
        query = query.filter(models.Room.location == location)
    if equipment is not None:
        query = query.filter(models.Room.equipment.contains(equipment))
    return query.all()

@router.get("/status/{room_id}", response_model=RoomStatusResponse)
def get_room_status(room_id: int, db: Session = Depends(get_db)):
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return RoomStatusResponse(room_id=room.id, is_available=room.is_available)
