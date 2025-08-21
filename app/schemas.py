from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: Optional[datetime]

    class Config:
        orm_mode = True 

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TodoBase(BaseModel):
    title: str
    description: Optional[str] = ""

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class TodoRead(TodoBase):
    id: int
    completed: bool = False

    class Config:
        orm_mode = True 
