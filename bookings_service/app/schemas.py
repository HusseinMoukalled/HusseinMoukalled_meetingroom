from pydantic import BaseModel
from datetime import date, time
from typing import Optional

class BookingCreate(BaseModel):
    username: str
    room_id: int
    date: date
    start_time: time
    end_time: time

class BookingUpdate(BaseModel):
    date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None

class BookingResponse(BaseModel):
    id: int
    username: str
    room_id: int
    date: date
    start_time: time
    end_time: time

    class Config:
        from_attributes = True
