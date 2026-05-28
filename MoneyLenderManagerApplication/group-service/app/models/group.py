"""SQLAlchemy models for chit_groups and group_members."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey, Boolean, Numeric, Date
from sqlalchemy.orm import relationship
from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class ChitGroup(Base):
    __tablename__ = "chit_groups"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    manager_id = Column(String(36), nullable=False)
    member_slots = Column(Integer, nullable=False)
    amount_per_person = Column(Numeric(12, 2), nullable=False)
    manager_fee_percent = Column(Numeric(5, 2), default=0.00)
    currency = Column(String(3), default="INR")
    status = Column(Enum("DRAFT", "ACTIVE", "COMPLETED", "ARCHIVED"), default="DRAFT")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")

    @property
    def targeting_amount(self) -> float:
        return float(self.member_slots * self.amount_per_person)

    @property
    def monthly_auction_amount(self) -> float:
        return float(self.targeting_amount / self.member_slots)


class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    group_id = Column(String(36), ForeignKey("chit_groups.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), nullable=False)
    role = Column(Enum("MANAGER", "MEMBER", "BOT"), nullable=False)
    has_won = Column(Boolean, default=False)
    won_month = Column(Integer)
    status = Column(Enum("ACTIVE", "REMOVED"), default="ACTIVE")
    joined_at = Column(DateTime, default=datetime.utcnow)

    group = relationship("ChitGroup", back_populates="members")


class PaymentDeadline(Base):
    __tablename__ = "payment_deadlines"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    group_id = Column(String(36), ForeignKey("chit_groups.id"), nullable=False)
    month_number = Column(Integer, nullable=False)
    deadline_date = Column(Date, nullable=False)
