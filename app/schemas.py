from typing import Annotated
from pydantic import BaseModel, constr
from datetime import datetime


class UserCreate(BaseModel):
    username: Annotated[str, constr(min_length=3, max_length=50)]
    password: Annotated[str, constr(min_length=5)]


class UserLogin(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    id: int
    username: str
    created_at: datetime

    class Config:
        orm_mode = True
