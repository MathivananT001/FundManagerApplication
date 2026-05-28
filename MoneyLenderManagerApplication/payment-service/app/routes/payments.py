"""Payment API routes."""
from typing import List
from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.payment import (
    ConfirmPaymentRequest, RejectPaymentRequest, ProofUploadRequest,
    ContributionResponse, PaymentRecordResponse, UnpaidMemberResponse,
    PresignedUrlResponse, AttachmentResponse, SuccessResponse,
)
from app.services.payment_service import payment_service

router = APIRouter()


def _get_user_id(x_user_id: str = Header(...)) -> str:
    return x_user_id


@router.get("/{group_id}/{month}", response_model=List[ContributionResponse])
async def get_ledger(group_id: str, month: int, db: Session = Depends(get_db)):
    """Get contribution ledger for a group/month (US-017)."""
    contributions = payment_service.get_ledger(db, group_id, month)
    return [
        ContributionResponse(
            id=c.id, group_id=c.group_id, member_id=c.member_id,
            month_number=c.month_number, amount_due=float(c.amount_due),
            deadline_date=c.deadline_date,
            payment_status=c.payment.status if c.payment else "PENDING",
        )
        for c in contributions
    ]


@router.post("/{payment_id}/confirm", response_model=PaymentRecordResponse)
async def confirm_payment(payment_id: str, payload: ConfirmPaymentRequest, db: Session = Depends(get_db)):
    """Fund manager confirms payment (US-018)."""
    record = payment_service.confirm_payment(db, payment_id, payload.manager_id)
    return PaymentRecordResponse(
        id=record.id, contribution_id=record.contribution_id,
        member_id=record.member_id, status=record.status,
        confirmed_by=record.confirmed_by,
        confirmed_at=str(record.confirmed_at) if record.confirmed_at else None,
        rejection_reason=record.rejection_reason,
    )


@router.post("/{payment_id}/reject", response_model=PaymentRecordResponse)
async def reject_payment(payment_id: str, payload: RejectPaymentRequest, db: Session = Depends(get_db)):
    """Fund manager rejects payment."""
    record = payment_service.reject_payment(db, payment_id, payload.manager_id, payload.reason)
    return PaymentRecordResponse(
        id=record.id, contribution_id=record.contribution_id,
        member_id=record.member_id, status=record.status,
        confirmed_by=record.confirmed_by, confirmed_at=None,
        rejection_reason=record.rejection_reason,
    )


@router.post("/{payment_id}/proof/upload-url", response_model=PresignedUrlResponse)
async def get_upload_url(payment_id: str, payload: ProofUploadRequest, user_id: str = Depends(_get_user_id)):
    """Generate presigned URL for proof upload (US-019, US-020)."""
    url, s3_key = payment_service.generate_upload_url(
        group_id="from-payment", member_id=user_id,
        file_name=payload.file_name, content_type=payload.content_type,
    )
    return PresignedUrlResponse(upload_url=url, s3_key=s3_key)


@router.get("/{payment_id}/attachments", response_model=List[AttachmentResponse])
async def get_attachments(payment_id: str, db: Session = Depends(get_db)):
    """Get payment proof attachments with download URLs."""
    return payment_service.get_attachments(db, payment_id)


@router.get("/{group_id}/unpaid/{month}", response_model=List[UnpaidMemberResponse])
async def get_unpaid(group_id: str, month: int, db: Session = Depends(get_db)):
    """Get unpaid members for a group/month (US-021)."""
    unpaid = payment_service.get_unpaid_members(db, group_id, month)
    # In production, join with users table for name/phone
    return [
        UnpaidMemberResponse(
            member_id=u["member_id"], full_name="", phone_number="",
            amount_due=u["amount_due"], month_number=u["month_number"],
        )
        for u in unpaid
    ]


@router.get("/overdue")
async def get_overdue(db: Session = Depends(get_db)):
    """Get all overdue payments (used by Bot Agent)."""
    return {"overdue_members": payment_service.get_overdue(db)}
