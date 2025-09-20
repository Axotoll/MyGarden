from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6) # plain text password for creation


class UserInDb(BaseModel):
    id: str | None = None  # MongoDB ObjectId as string
    username: str
    email: EmailStr
    hashed_password: str # bcrypt/argon2 hash
    language: str = "en"
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6) # plain text password for login


class UserPublic(BaseModel):
    username: str
    email: EmailStr
    language: str
    is_active: bool
    is_admin: bool
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: EmailStr | None = None