from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    nickname: str
    telegram_uid: str
    coins: int
    rating: int


class UserUpdateRequest(BaseModel):
    coins: int
    rating: int