from pydantic import BaseModel
from typing import Optional

class BookingBase(BaseModel):
    username:str
    room_id:int
    date:str
    start_time:str
    end_time:str

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    room_id:Optional[int]=None
    date:Optional[str]=None
    start_time:Optional[str]=None
    end_time:Optional[str]=None

class BookingResponse(BookingBase):
    id:int

    class Config:
        orm_mode=True

class AvailabilityResponse(BaseModel):
    room_id:int
    available:bool

    class Config:
        orm_mode=True
