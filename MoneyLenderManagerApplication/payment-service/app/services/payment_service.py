"""Payment service business logic."""
import boto3
from datetime import datetime, date
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.config import settings
from app.models.payment import Contribution, PaymentRecord, Attachment


class PaymentService:
    def __init__(self):
        self.s3 = boto3.client("s3", region_name=settings.aws_region)

    def get_ledger(self, db: Session, group_id: str, month: int) -> list[Contribution]:
        """Get contribution ledger for a group/month (US-017)."""
        return db.query(Contribution).filter(
            Contribution.group_id == group_id,
            Contribution.month_number == month,
        ).all()

    def confirm_payment(self, db: Session, payment_id: str, manager_id: str) -> PaymentRecord:
        """Fund manager confirms payment (US-018)."""
        record = self._get_payment_or_404(db, payment_id)
        if record.status != "PENDING":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment already processed")
        record.status = "CONFIRMED"
        record.confirmed_by = manager_id
        record.confirmed_at = datetime.utcnow()
        db.commit()
        db.refresh(record)
        return record

    def reject_payment(self, db: Session, payment_id: str, manager_id: str, reason: str) -> PaymentRecord:
        """Fund manager rejects payment."""
        record = self._get_payment_or_404(db, payment_id)
        if record.status != "PENDING":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment already processed")
        record.status = "REJECTED"
        record.confirmed_by = manager_id
        record.rejection_reason = reason
        db.commit()
        db.refresh(record)
        return record

    def generate_upload_url(self, group_id: str, member_id: str, file_name: str, content_type: str) -> tuple[str, str]:
        """Generate presigned PUT URL for proof upload (US-019, US-020)."""
        s3_key = f"proofs/{group_id}/{member_id}/{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file_name}"
        url = self.s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.s3_payment_proofs_bucket,
                "Key": s3_key,
                "ContentType": content_type,
            },
            ExpiresIn=settings.presigned_url_expiry,
        )
        return url, s3_key

    def add_attachment(self, db: Session, payment_id: str, s3_key: str,
                       file_name: str, content_type: str, description: str = None) -> Attachment:
        """Record an attachment after upload."""
        record = self._get_payment_or_404(db, payment_id)
        attachment = Attachment(
            payment_record_id=record.id, s3_key=s3_key,
            file_name=file_name, content_type=content_type, description=description,
        )
        db.add(attachment)
        db.commit()
        db.refresh(attachment)
        return attachment

    def get_attachments(self, db: Session, payment_id: str) -> list[dict]:
        """Get attachments with presigned download URLs."""
        attachments = db.query(Attachment).filter(Attachment.payment_record_id == payment_id).all()
        result = []
        for att in attachments:
            url = self.s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": settings.s3_payment_proofs_bucket, "Key": att.s3_key},
                ExpiresIn=settings.presigned_url_expiry,
            )
            result.append({
                "id": att.id, "file_name": att.file_name,
                "content_type": att.content_type, "description": att.description,
                "download_url": url,
            })
        return result

    def get_unpaid_members(self, db: Session, group_id: str, month: int) -> list[dict]:
        """Get members with unconfirmed payments (US-021)."""
        contributions = db.query(Contribution).filter(
            Contribution.group_id == group_id,
            Contribution.month_number == month,
        ).all()

        unpaid = []
        for c in contributions:
            if not c.payment or c.payment.status != "CONFIRMED":
                unpaid.append({
                    "member_id": c.member_id,
                    "amount_due": float(c.amount_due),
                    "month_number": c.month_number,
                })
        return unpaid

    def get_overdue(self, db: Session) -> list[dict]:
        """Get all overdue payments across groups (used by Bot Agent)."""
        today = date.today()
        contributions = db.query(Contribution).filter(
            Contribution.deadline_date < today,
        ).all()

        overdue = []
        for c in contributions:
            if not c.payment or c.payment.status == "PENDING":
                overdue.append({
                    "group_id": c.group_id,
                    "member_id": c.member_id,
                    "amount_due": float(c.amount_due),
                    "month_number": c.month_number,
                })
        return overdue

    def _get_payment_or_404(self, db: Session, payment_id: str) -> PaymentRecord:
        record = db.query(PaymentRecord).filter(PaymentRecord.id == payment_id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment record not found")
        return record


payment_service = PaymentService()
