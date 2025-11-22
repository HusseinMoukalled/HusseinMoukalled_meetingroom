from sqlalchemy import Column,Integer,String,Boolean
from shared.database import Base

class Room(Base):
    __tablename__="rooms"

    id=Column(Integer,primary_key=True,index=True)
    name=Column(String,nullable=False)
    capacity=Column(Integer,nullable=False)
    equipment=Column(String,nullable=True)
    location=Column(String,nullable=True)
    is_available=Column(Boolean,default=True)
