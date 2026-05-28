"""Pydantic schemas for auth service requests and responses."""
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, EmailStr


class UserRole(str, Enum):
    FUND_MANAGER = "FUND_MANAGER"
    MEMBER = "MEMBER"
    BOT = "BOT"


class LanguageCode(str, Enum):
    EN = "en"
    TA = "ta"


# Requests
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone_number: Optional[str] = None
    language_preference: LanguageCode = LanguageCode.EN


class EmailLoginRequest(BaseModel):
    email: EmailStr
    password: str


class PhoneOTPRequest(BaseModel):
    phone_number: str


class VerifyOTPRequest(BaseModel):
    phone_number: str
    otp_code: str


class GoogleLoginRequest(BaseModel):
    google_oauth_token: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None


class SetLanguageRequest(BaseModel):
    language: LanguageCode


class AssignRoleRequest(BaseModel):
    user_id: str
    role: UserRole


# Responses
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int


class OTPInitiatedResponse(BaseModel):
    message: str
    session: str


class UserProfileResponse(BaseModel):
    id: str
    email: Optional[str]
    phone_number: Optional[str]
    full_name: str
    language_preference: str
    roles: List[str]

    class Config:
        from_attributes = True


class SuccessResponse(BaseModel):
    message: str
