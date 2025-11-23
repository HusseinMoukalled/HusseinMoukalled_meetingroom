from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey
from shared.database import Base

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    room_id = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
