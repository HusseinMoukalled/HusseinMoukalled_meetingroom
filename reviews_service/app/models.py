from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from shared.database import Base

import users_service.app.models
import rooms_service.app.models


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, ForeignKey("users.username"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(String, nullable=True)

    is_flagged = Column(Boolean, default=False)
    flag_reason = Column(String, nullable=True)

    user = relationship("User")
    room = relationship("Room")
