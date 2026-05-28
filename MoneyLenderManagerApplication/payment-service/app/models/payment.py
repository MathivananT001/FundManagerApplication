"""SQLAlchemy models for contributions, payment_records, and attachments."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey, Numeric, Date, Text
from sqlalchemy.orm import relationship
from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class Contribution(Base):
    __tablename__ = "contributions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    group_id = Column(String(36), nullable=False)
    auction_id = Column(String(36), nullable=False)
    member_id = Column(String(36), nullable=False)
    month_number = Column(Integer, nullable=False)
    amount_due = Column(Numeric(12, 2), nullable=False)
    deadline_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)

    payment = relationship("PaymentRecord", back_populates="contribution", uselist=False)


class PaymentRecord(Base):
    __tablename__ = "payment_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    contribution_id = Column(String(36), ForeignKey("contributions.id"), nullable=False)
    member_id = Column(String(36), nullable=False)
    confirmed_by = Column(String(36))
    status = Column(Enum("PENDING", "CONFIRMED", "REJECTED"), default="PENDING")
    confirmed_at = Column(DateTime)
    rejection_reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    contribution = relationship("Contribution", back_populates="payment")
    attachments = relationship("Attachment", back_populates="payment_record", cascade="all, delete-orphan")


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    payment_record_id = Column(String(36), ForeignKey("payment_records.id", ondelete="CASCADE"), nullable=False)
    s3_key = Column(String(512), nullable=False)
    file_name = Column(String(255))
    content_type = Column(String(100))
    description = Column(Text)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    payment_record = relationship("PaymentRecord", back_populates="attachments")
