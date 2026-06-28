from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class UserTable(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name=Column(String, nullable=True)
    entries = relationship("JournalTable", back_populates="owner")


class JournalTable(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    mood = Column(String)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    owner = relationship("UserTable", back_populates="entries")

class HabitTable(Base):
    __tablename__="habits"

    id=Column(Integer,primary_key=True,index=True)
    name=Column(String,nullable=False)
    streak_count=Column(Integer,default=0)

    user_id=Column(Integer,ForeignKey("users.id"),nullable=False)