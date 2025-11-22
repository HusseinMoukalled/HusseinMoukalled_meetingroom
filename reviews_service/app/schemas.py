from pydantic import BaseModel


class ReviewCreate(BaseModel):
    username: str
    room_id: int
    rating: int
    comment: str


class UpdateReview(BaseModel):
    rating: int | None = None
    comment: str | None = None


class FlagReview(BaseModel):
    reason: str


class ReviewResponse(BaseModel):
    id: int
    username: str
    room_id: int
    rating: int
    comment: str
    is_flagged: bool
    flag_reason: str | None

    class Config:
        from_attributes = True
