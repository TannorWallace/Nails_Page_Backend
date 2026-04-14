from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float, DateTime, Table,Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Integer, default=1)
    is_admin = Column(Boolean, default=False)

    # Relationship for comments
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")


class ArtImage(Base):
    __tablename__ = "art_images"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    image_url = Column(String, nullable=False)  # path or cloud URL
    artist = Column(String, default="Wife's Nail Art")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationship for comments
    comments = relationship("Comment", back_populates="image", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    image_id = Column(Integer, ForeignKey("art_images.id"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="comments")
    image = relationship("ArtImage", back_populates="comments")