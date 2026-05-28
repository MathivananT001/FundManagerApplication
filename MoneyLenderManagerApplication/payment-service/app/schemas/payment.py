"""Pydantic schemas for payment service."""
from typing import Optional, List
from datetime import date
from pydantic import BaseModel


# Requests
class ConfirmPaymentRequest(BaseModel):
    manager_id: str


class RejectPaymentRequest(BaseModel):
    manager_id: str
    reason: str


class ProofUploadRequest(BaseModel):
    file_name: str
    content_type: str
    description: Optional[str] = None


# Responses
class ContributionResponse(BaseModel):
    id: str
    group_id: str
    member_id: str
    month_number: int
    amount_due: float
    deadline_date: Optional[date]
    payment_status: str

    class Config:
        from_attributes = True


class PaymentRecordResponse(BaseModel):
    id: str
    contribution_id: str
    member_id: str
    status: str
    confirmed_by: Optional[str]
    confirmed_at: Optional[str]
    rejection_reason: Optional[str]

    class Config:
        from_attributes = True


class UnpaidMemberResponse(BaseModel):
    member_id: str
    full_name: str
    phone_number: str
    amount_due: float
    month_number: int


class PresignedUrlResponse(BaseModel):
    upload_url: str
    s3_key: str


class AttachmentResponse(BaseModel):
    id: str
    file_name: Optional[str]
    content_type: Optional[str]
    description: Optional[str]
    download_url: str


class SuccessResponse(BaseModel):
    message: str
