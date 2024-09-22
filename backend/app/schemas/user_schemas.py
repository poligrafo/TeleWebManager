from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    nickname: str
    telegram_uid: str
    coins: Optional[int] = 0
    rating: Optional[int] = 0

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    coins: Optional[int] = None
    rating: Optional[int] = None

class UserInDBBase(UserBase):
    id: int
    last_login: datetime
    last_logout: datetime

    class Config:
        orm_mode = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    pass