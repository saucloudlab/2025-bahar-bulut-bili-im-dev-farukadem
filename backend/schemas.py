from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CommentBase(BaseModel):
    text: str

class Comment(CommentBase):
    id: int
    user_id: int
    created_at: datetime
    class Config: from_attributes = True

class MaterialBase(BaseModel):
    name: str
    description: Optional[str] = "Açıklama girilmedi."
    dimensions: Optional[str] = "Bilinmiyor"
    usage_area: Optional[str] = "Genel"

class Material(MaterialBase):
    id: int
    file_url: str
    owner_id: int
    comments: List[Comment] = []
    class Config: from_attributes = True

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    class Config: from_attributes = True

class Notification(BaseModel):
    id: int
    message: str
    is_read: bool
    class Config: from_attributes = True
