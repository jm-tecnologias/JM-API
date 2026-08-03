from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, EmailStr, ConfigDict

from models.user_history_model import UserHistoryResponse


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=10)
    name: str = Field(min_length=5, max_length=20)
    last_name: str = Field(min_length=3, max_length=20)
    email:EmailStr = Field(min_length=10, max_length=50)
    phone: str | None = Field(min_length=9, max_length=30)


class UserCreate(UserModel):
    password: str = Field(min_length=8, max_length=255)

class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=5, max_length=10)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    name: str | None = Field(default=None, min_length=5, max_length=20)
    last_name: str | None = Field(default=None,min_length=5, max_length=20)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=9, max_length=30)
    profile_pic_url: str | None
    status: bool | None = None
    user_type: str = Field(default="client", min_length=5, max_length=20)



class UserResponse(UserModel):
    id: int
    status: bool
    profile_pic_url: str | None = None
    user_type: str
    restaurant_id: int | None = None
    created_at: datetime
    updated_at: datetime
    histories:list[UserHistoryResponse] = Field(default_factory=list)
    token: str | None = None

    model_config = ConfigDict(
        from_attributes=True
    )

class UserLogin(BaseModel):
    username: str = Field(min_length=5, max_length=10)
    password: str = Field(min_length=8, max_length=255)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"


class RefreshSessionResponse(BaseModel):
    id: str
    issued_at: datetime
    expires_at: datetime
    last_used_at: datetime | None
    user_agent: str | None
    ip_address: str | None
    current: bool = False


class StaffRoleUpdate(BaseModel):
    user_type: Literal["client", "waiter", "kitchen", "cashier", "manager", "admin"]
    restaurant_id: int | None = Field(default=None, gt=0)


class BootstrapAdminRequest(BaseModel):
    username: str = Field(min_length=5, max_length=10)


