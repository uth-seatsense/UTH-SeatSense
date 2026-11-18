from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class OtpRequest(BaseModel):
    email: EmailStr


class OtpLoginRequest(OtpRequest):
    otp: str = Field(pattern=r"^\d{6}$")


class OtpRequestResponse(BaseModel):
    status: Literal["otp_sent"] = "otp_sent"


class AuthUser(BaseModel):
    id: int
    email: EmailStr
    display_name: str
    role: Literal["student", "librarian", "admin"]


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_at: datetime
    user: AuthUser
