from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr,Field

from app.enums.user_roles import UserRole

class UserCreate(BaseModel):

    email: EmailStr

    password: str = Field(
        min_length=6,
        max_length=72
    )

    full_name: str

class UserLogin(BaseModel):

    email: EmailStr

    password: str


class UserUpdate(BaseModel):

    email: EmailStr | None = None

    full_name: str | None = None

    password: str | None = None


class UserResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    email: EmailStr

    full_name: str

    role: UserRole

    is_active: bool

    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str