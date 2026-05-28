"""Group API routes."""
from typing import List
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.group import ChitGroup, GroupMember
from app.schemas.group import (
    CreateGroupRequest, UpdateGroupRequest, AddMemberRequest,
    SetPaymentDeadlineRequest, GroupResponse, GroupDetailResponse,
    GroupMemberResponse, ArchiveResponse, SuccessResponse,
)
from app.services.group_service import group_service

router = APIRouter()


def _get_manager_id(x_user_id: str = Header(...)) -> str:
    """Extract user ID from header (in production, from JWT middleware)."""
    return x_user_id


def _to_group_response(group: ChitGroup) -> GroupResponse:
    active_members = [m for m in group.members if m.status == "ACTIVE"]
    return GroupResponse(
        id=group.id, name=group.name, description=group.description,
        manager_id=group.manager_id, member_slots=group.member_slots,
        amount_per_person=float(group.amount_per_person),
        targeting_amount=group.targeting_amount,
        monthly_auction_amount=group.monthly_auction_amount,
        manager_fee_percent=float(group.manager_fee_percent),
        currency=group.currency, status=group.status,
        member_count=len(active_members),
    )


@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(payload: CreateGroupRequest, manager_id: str = Depends(_get_manager_id), db: Session = Depends(get_db)):
    """Create a new chit fund group (US-005)."""
    group = group_service.create_group(
        db, manager_id=manager_id, name=payload.name, description=payload.description,
        member_slots=payload.member_slots, amount_per_person=payload.amount_per_person,
        manager_fee_percent=payload.manager_fee_percent,
    )
    return _to_group_response(group)


@router.get("/{group_id}", response_model=GroupDetailResponse)
async def get_group(group_id: str, db: Session = Depends(get_db)):
    """Get group details with members."""
    group = db.query(ChitGroup).filter(ChitGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    active_members = [m for m in group.members if m.status == "ACTIVE"]
    return GroupDetailResponse(
        id=group.id, name=group.name, description=group.description,
        manager_id=group.manager_id, member_slots=group.member_slots,
        amount_per_person=float(group.amount_per_person),
        targeting_amount=group.targeting_amount,
        monthly_auction_amount=group.monthly_auction_amount,
        manager_fee_percent=float(group.manager_fee_percent),
        currency=group.currency, status=group.status,
        member_count=len(active_members),
        members=[GroupMemberResponse.model_validate(m) for m in active_members],
    )


@router.get("", response_model=List[GroupResponse])
async def list_groups(manager_id: str = Depends(_get_manager_id), db: Session = Depends(get_db)):
    """List groups managed by the current user."""
    groups = db.query(ChitGroup).filter(ChitGroup.manager_id == manager_id).all()
    return [_to_group_response(g) for g in groups]


@router.put("/{group_id}", response_model=GroupResponse)
async def update_group(group_id: str, payload: UpdateGroupRequest, manager_id: str = Depends(_get_manager_id), db: Session = Depends(get_db)):
    """Update group settings."""
    group = group_service._get_group_or_404(db, group_id)
    group_service._assert_manager(group, manager_id)
    if payload.name is not None:
        group.name = payload.name
    if payload.description is not None:
        group.description = payload.description
    if payload.manager_fee_percent is not None:
        group.manager_fee_percent = payload.manager_fee_percent
    db.commit()
    db.refresh(group)
    return _to_group_response(group)


@router.post("/{group_id}/activate", response_model=GroupResponse)
async def activate_group(group_id: str, manager_id: str = Depends(_get_manager_id), db: Session = Depends(get_db)):
    """Activate a group."""
    group = group_service.activate_group(db, group_id, manager_id)
    return _to_group_response(group)


@router.post("/{group_id}/members", response_model=GroupMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_member(group_id: str, payload: AddMemberRequest, manager_id: str = Depends(_get_manager_id), db: Session = Depends(get_db)):
    """Add a member to the group (US-006)."""
    member = group_service.add_member(db, group_id, payload.user_id, manager_id)
    return GroupMemberResponse.model_validate(member)


@router.delete("/{group_id}/members/{user_id}", response_model=SuccessResponse)
async def remove_member(group_id: str, user_id: str, manager_id: str = Depends(_get_manager_id), db: Session = Depends(get_db)):
    """Remove a member from the group."""
    group_service.remove_member(db, group_id, user_id, manager_id)
    return SuccessResponse(message="Member removed")


@router.get("/{group_id}/non-winners", response_model=List[GroupMemberResponse])
async def get_non_winners(group_id: str, db: Session = Depends(get_db)):
    """Get members who haven't won yet (US-007, US-008)."""
    members = group_service.get_non_winners(db, group_id)
    return [GroupMemberResponse.model_validate(m) for m in members]


@router.post("/{group_id}/deadline", response_model=SuccessResponse)
async def set_deadline(group_id: str, payload: SetPaymentDeadlineRequest, manager_id: str = Depends(_get_manager_id), db: Session = Depends(get_db)):
    """Set payment deadline for a month (US-009)."""
    group_service._assert_manager(group_service._get_group_or_404(db, group_id), manager_id)
    group_service.set_payment_deadline(db, group_id, payload.month, payload.deadline_date)
    return SuccessResponse(message=f"Deadline set for month {payload.month}")


@router.post("/{group_id}/archive", response_model=ArchiveResponse)
async def archive_group(group_id: str, manager_id: str = Depends(_get_manager_id), db: Session = Depends(get_db)):
    """Archive a completed group (US-010)."""
    s3_key = group_service.archive_group(db, group_id, manager_id)
    return ArchiveResponse(message="Group archived successfully", s3_key=s3_key)
