"""Pydantic schemas for notification service."""
from typing import Optional, List
from pydantic import BaseModel


class SendSMSRequest(BaseModel):
    phone_number: str
    template_key: str
    params: dict = {}
    language: str = "en"


class SendPushRequest(BaseModel):
    user_id: str
    title: str
    body: str
    data: dict = {}
    language: str = "en"


class BulkSMSRequest(BaseModel):
    phone_numbers: List[str]
    template_key: str
    params: dict = {}
    language: str = "en"


class BulkPushRequest(BaseModel):
    user_ids: List[str]
    title: str
    body: str
    data: dict = {}
    language: str = "en"


class RegisterDeviceRequest(BaseModel):
    user_id: str
    fcm_token: str
    platform: str  # "android" | "ios"


class DeregisterDeviceRequest(BaseModel):
    user_id: str
    fcm_token: str


class NotificationLogResponse(BaseModel):
    user_id: str
    timestamp: str
    channel: str
    template_key: str
    status: str


class SuccessResponse(BaseModel):
    message: str
    message_id: Optional[str] = None
