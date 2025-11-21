from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from typing import List,Optional
from shared.database import get_db
from app import models
from app.schemas import RoomCreate,RoomUpdate,RoomResponse,RoomStatusResponse

router=APIRouter()

def to_response(room:models.Room)->RoomResponse:
    equipment_list=room.equipment.split(",") if room.equipment else []
    return RoomResponse(
        id=room.id,
        room_name=room.room_name,
        capacity=room.capacity,
        equipment=equipment_list,
        location=room.location,
        is_available=room.is_available
    )

@router.post("/add",response_model=RoomResponse)
def add_room(data:RoomCreate,db:Session=Depends(get_db)):
    existing=db.query(models.Room).filter(models.Room.room_name==data.room_name).first()
    if existing:
        raise HTTPException(status_code=400,detail="Room name already exists")
    equipment_str=",".join(data.equipment) if data.equipment else None
    room=models.Room(
        room_name=data.room_name,
        capacity=data.capacity,
        equipment=equipment_str,
        location=data.location
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return to_response(room)

@router.put("/{room_id}",response_model=RoomResponse)
def update_room(room_id:int,data:RoomUpdate,db:Session=Depends(get_db)):
    room=db.query(models.Room).filter(models.Room.id==room_id).first()
    if not room:
        raise HTTPException(status_code=404,detail="Room not found")
    if data.room_name is not None:
        room.room_name=data.room_name
    if data.capacity is not None:
        room.capacity=data.capacity
    if data.equipment is not None:
        room.equipment=",".join(data.equipment)
    if data.location is not None:
        room.location=data.location
    db.commit()
    db.refresh(room)
    return to_response(room)

@router.delete("/{room_id}")
def delete_room(room_id:int,db:Session=Depends(get_db)):
    room=db.query(models.Room).filter(models.Room.id==room_id).first()
    if not room:
        raise HTTPException(status_code=404,detail="Room not found")
    db.delete(room)
    db.commit()
    return {"detail":"Room deleted"}

@router.get("/available",response_model=List[RoomResponse])
def get_available_rooms(
    capacity:Optional[int]=None,
    location:Optional[str]=None,
    equipment:Optional[str]=None,
    db:Session=Depends(get_db)
):
    q=db.query(models.Room)
    if capacity is not None:
        q=q.filter(models.Room.capacity>=capacity)
    if location is not None:
        q=q.filter(models.Room.location.ilike(f"%{location}%"))
    if equipment is not None:
        q=q.filter(models.Room.equipment.ilike(f"%{equipment}%"))
    rooms=q.all()
    return [to_response(r) for r in rooms]

@router.get("/{room_id}/status",response_model=RoomStatusResponse)
def room_status(room_id:int,db:Session=Depends(get_db)):
    room=db.query(models.Room).filter(models.Room.id==room_id).first()
    if not room:
        raise HTTPException(status_code=404,detail="Room not found")
    status="available" if room.is_available else "booked"
    return RoomStatusResponse(room_id=room.id,status=status)
