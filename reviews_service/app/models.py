from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from shared.database import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, ForeignKey("users.username"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(String, nullable=True)
    flagged = Column(String, nullable=True)  # stores reason if flagged

    # relationships
    user = relationship("User", back_populates="reviews", lazy="selectin")
    room = relationship("Room", back_populates="reviews", lazy="selectin")
