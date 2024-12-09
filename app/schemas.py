# schemas.py
from pydantic import BaseModel
from datetime import datetime

class PostBase(BaseModel):
    title: str
    slug: str
    content: str

class PostCreate(PostBase):
    pass

class PostRead(PostBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
