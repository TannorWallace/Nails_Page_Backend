from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    # is_admin: bool = False

class AdminUserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_admin: bool = False

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: int
    is_admin: bool

    model_config = {"from_attributes": True}

    # class Config:
    #     from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str


# IMAGE SCHEMAS
class ArtImageCreate(BaseModel):
    title: str
    artist: Optional[str] = "Nails by Mykala"

class ArtImageOut(BaseModel):
    id: int
    title: str
    image_url: str
    artist: str
    created_at: datetime
    
    model_config = {"from_attributes": True}

    # class Config:
    #     from_attributes = True

#COMMENTS
class CommentCreate(BaseModel):
    text:str
    image_id: int

class UpdateComment(BaseModel):
    text: str

class CommentOut(BaseModel):
    id: int
    text: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    username: str          #show who commented

    model_config = {"from_attributes": True}
    # class Config:
    #     from_attributes = True

class AdminCommentOut(BaseModel):
    id: int
    text: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    username: str
    image_id: int
    image_title: str          # helpful for moderation

    model_config = {"from_attributes": True}

    # class Config:
    #     from_attributes = True