from pydantic import BaseModel, EmailStr
from typing import Optional, List

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None

class UserCreate(BaseModel):
    name: str
    username: str
    email: EmailStr
    password: str
    role: str = "regular_user"

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    name: str
    username: str
    email: EmailStr
    role: str

    model_config = {
        "from_attributes": True
    }

class BookingHistoryItem(BaseModel):
    room_id: int
    date: str
    start_time: str
    end_time: str

    model_config = {
        "from_attributes": True
    }

class UserBookingHistoryResponse(BaseModel):
    username: str
    bookings: List[BookingHistoryItem]

    model_config = {
        "from_attributes": True
    }
