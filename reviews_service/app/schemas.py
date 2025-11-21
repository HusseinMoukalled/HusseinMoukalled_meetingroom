from pydantic import BaseModel
from typing import Optional

class ReviewBase(BaseModel):
    username:str
    room_id:int
    rating:int
    comment:Optional[str]=None

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    rating:Optional[int]=None
    comment:Optional[str]=None

class ReviewResponse(ReviewBase):
    id:int
    flagged:Optional[str]=None

    class Config:
        orm_mode=True

class FlagReview(BaseModel):
    reason:Optional[str]=None
