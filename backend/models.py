from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    materials = relationship("Material", back_populates="owner")
    comments = relationship("Comment", back_populates="user")
    notifications = relationship("Notification", back_populates="user")

class Material(Base):
    __tablename__ = "materials"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    file_url = Column(String)
    
    # --- YENİ EKLENEN GERÇEK ÖZELLİKLER ---
    description = Column(String, default="Açıklama girilmedi.")
    dimensions = Column(String, default="Bilinmiyor")
    usage_area = Column(String, default="Genel")
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="materials")
    comments = relationship("Comment", back_populates="material")
    ratings = relationship("Rating", back_populates="material")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    material_id = Column(Integer, ForeignKey("materials.id"))
    
    user = relationship("User", back_populates="comments")
    material = relationship("Material", back_populates="comments")

class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True, index=True)
    stars = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))
    material_id = Column(Integer, ForeignKey("materials.id"))
    material = relationship("Material", back_populates="ratings")

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)
    is_read = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="notifications")
