from pydantic import BaseModel
from typing import Optional

class RoomBase(BaseModel):
    name:str
    capacity:int
    equipment:Optional[str]=None
    location:Optional[str]=None

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    name:Optional[str]=None
    capacity:Optional[int]=None
    equipment:Optional[str]=None
    location:Optional[str]=None
    is_available:Optional[bool]=None

class RoomResponse(RoomBase):
    id:int
    is_available:bool

    class Config:
        from_attributes=True

class RoomStatusResponse(BaseModel):
    room_id:int
    is_available:bool
