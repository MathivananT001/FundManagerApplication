"""Pydantic schemas for group service."""
from typing import Optional, List
from datetime import date
from enum import Enum
from pydantic import BaseModel


class GroupStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class MemberRole(str, Enum):
    MANAGER = "MANAGER"
    MEMBER = "MEMBER"
    BOT = "BOT"


# Requests
class CreateGroupRequest(BaseModel):
    name: str
    description: Optional[str] = None
    member_slots: int  # 8-15
    amount_per_person: float
    manager_fee_percent: float = 0.0


class UpdateGroupRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    manager_fee_percent: Optional[float] = None


class AddMemberRequest(BaseModel):
    user_id: str


class SetPaymentDeadlineRequest(BaseModel):
    month: int
    deadline_date: date


# Responses
class GroupMemberResponse(BaseModel):
    id: str
    user_id: str
    role: str
    has_won: bool
    won_month: Optional[int]
    status: str

    class Config:
        from_attributes = True


class GroupResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    manager_id: str
    member_slots: int
    amount_per_person: float
    targeting_amount: float
    monthly_auction_amount: float
    manager_fee_percent: float
    currency: str
    status: str
    member_count: int

    class Config:
        from_attributes = True


class GroupDetailResponse(GroupResponse):
    members: List[GroupMemberResponse]


class ArchiveResponse(BaseModel):
    message: str
    s3_key: str


class SuccessResponse(BaseModel):
    message: str
