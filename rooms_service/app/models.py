from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from shared.database import Base

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_name = Column(String, unique=True, nullable=False)
    capacity = Column(Integer, nullable=False)
    equipment = Column(String, nullable=True)  # will store JSON as string
    location = Column(String, nullable=False)
    is_available = Column(Boolean, default=True)

    # relationships
    bookings = relationship("Booking", back_populates="room", lazy="selectin")
    reviews = relationship("Review", back_populates="room", lazy="selectin")
