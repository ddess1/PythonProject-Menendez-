from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional
from datetime import datetime

# Базовая схема для чтения данных
class UserBase(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True

# Схема для регистрации пользователя (без id)
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: Optional[str] = "client"  # По умолчанию "client"

# Схема для логина пользователя
class UserLogin(BaseModel):
    email: str
    password: str

# Схема для ответа о пользователе
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str

    class Config:
        orm_mode = True




# CARS
class CarBase(BaseModel):
    name: str
    brand: str
    price: float
    description: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None

    @validator("price")
    def validate_price(cls, value):
        if value <= 0:
            raise ValueError("Price must be a positive number")
        return value

class CarCreate(CarBase):
    pass


class CarUpdate(CarBase):
    pass

class CarResponse(CarBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True






