from pydantic import BaseModel, constr
from datetime import datetime

class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=5)

class UserLogin(BaseModel):
    username: str
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    created_at: datetime

    class Config:
        orm_mode = True
