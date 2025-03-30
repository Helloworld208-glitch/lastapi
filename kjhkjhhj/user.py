from  database import Base
from sqlalchemy import Column, Integer ,String



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