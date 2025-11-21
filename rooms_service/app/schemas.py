from pydantic import BaseModel
from typing import Optional,List

class RoomBase(BaseModel):
    room_name:str
    capacity:int
    equipment:Optional[List[str]]=None
    location:str

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    room_name:Optional[str]=None
    capacity:Optional[int]=None
    equipment:Optional[List[str]]=None
    location:Optional[str]=None

class RoomResponse(RoomBase):
    id:int
    is_available:bool

    class Config:
        orm_mode=True

class RoomStatusResponse(BaseModel):
    room_id:int
    status:str

    class Config:
        orm_mode=True
