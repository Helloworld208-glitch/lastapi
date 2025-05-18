from  database import Base
from sqlalchemy import Column, Integer ,String
from sqlalchemy import DateTime
from sqlalchemy.sql import func


class Userr(Base):
    __tablename__="User"
    id=Column(Integer,primary_key=True)
    firstname =Column(String(50))
    lasttname =Column(String(50))
    email =Column(String(50))
    password =Column(String(200))
import enum
from sqlalchemy import Column, Integer, Date, Enum, TIMESTAMP, func, ForeignKey
from database import Base

class AppointmentStatus(enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class Appointment(Base):
    __tablename__ = "appointments"
    
    appointment_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("User.id"), nullable=False)
    appointment_date = Column(Date, nullable=False)
    status = Column(Enum(AppointmentStatus), nullable=False, default=AppointmentStatus.pending)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("User.id"), nullable=False, unique=True)
    role = Column(String(50), default="admin")  

class UserPremium(Base):
    __tablename__ = "user_premium"
    
    user_id = Column(Integer, ForeignKey("User.id"), primary_key=True)





class ChatMessage(Base):
    __tablename__ = "simple_chat_messages"  # New table name
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    from_id = Column(Integer, index=True)
    to_id = Column(Integer, index=True)
    message = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
