"""Group service business logic — lifecycle, calculations, archival."""
import json
import boto3
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.config import settings
from app.models.group import ChitGroup, GroupMember, PaymentDeadline


class GroupService:
    def __init__(self):
        self.s3 = boto3.client("s3", region_name=settings.aws_region)

    def create_group(self, db: Session, manager_id: str, name: str, description: str,
                     member_slots: int, amount_per_person: float, manager_fee_percent: float) -> ChitGroup:
        """Create a new chit fund group (US-005)."""
        if not 8 <= member_slots <= 15:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="member_slots must be 8-15")

        group = ChitGroup(
            name=name, description=description, manager_id=manager_id,
            member_slots=member_slots, amount_per_person=amount_per_person,
            manager_fee_percent=manager_fee_percent,
        )
        # Auto-add manager as member
        manager_member = GroupMember(group=group, user_id=manager_id, role="MANAGER")
        db.add(group)
        db.add(manager_member)
        db.commit()
        db.refresh(group)
        return group

    def activate_group(self, db: Session, group_id: str, manager_id: str) -> ChitGroup:
        """Activate a group (move from DRAFT to ACTIVE)."""
        group = self._get_group_or_404(db, group_id)
        self._assert_manager(group, manager_id)
        if group.status != "DRAFT":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only DRAFT groups can be activated")
        group.status = "ACTIVE"
        db.commit()
        db.refresh(group)
        return group

    def add_member(self, db: Session, group_id: str, user_id: str, manager_id: str) -> GroupMember:
        """Add a member to the group (US-006)."""
        group = self._get_group_or_404(db, group_id)
        self._assert_manager(group, manager_id)

        active_count = db.query(GroupMember).filter(
            GroupMember.group_id == group_id, GroupMember.status == "ACTIVE"
        ).count()
        if active_count >= group.member_slots:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Group is full")

        existing = db.query(GroupMember).filter(
            GroupMember.group_id == group_id, GroupMember.user_id == user_id
        ).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Member already in group")

        member = GroupMember(group_id=group_id, user_id=user_id, role="MEMBER")
        db.add(member)
        db.commit()
        db.refresh(member)
        return member

    def remove_member(self, db: Session, group_id: str, user_id: str, manager_id: str):
        """Remove a member from the group."""
        group = self._get_group_or_404(db, group_id)
        self._assert_manager(group, manager_id)

        member = db.query(GroupMember).filter(
            GroupMember.group_id == group_id, GroupMember.user_id == user_id
        ).first()
        if not member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
        member.status = "REMOVED"
        db.commit()

    def get_non_winners(self, db: Session, group_id: str) -> list[GroupMember]:
        """Get members who haven't won yet, excluding bot (US-007, US-008)."""
        return db.query(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.has_won == False,
            GroupMember.role != "BOT",
            GroupMember.status == "ACTIVE",
        ).all()

    def mark_member_as_winner(self, db: Session, group_id: str, member_id: str, month: int):
        """Mark a member as auction winner for a given month."""
        member = db.query(GroupMember).filter(
            GroupMember.group_id == group_id, GroupMember.user_id == member_id
        ).first()
        if not member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
        member.has_won = True
        member.won_month = month
        db.commit()

    def set_payment_deadline(self, db: Session, group_id: str, month: int, deadline_date) -> PaymentDeadline:
        """Set payment deadline for a month (US-009)."""
        existing = db.query(PaymentDeadline).filter(
            PaymentDeadline.group_id == group_id, PaymentDeadline.month_number == month
        ).first()
        if existing:
            existing.deadline_date = deadline_date
            db.commit()
            return existing

        deadline = PaymentDeadline(group_id=group_id, month_number=month, deadline_date=deadline_date)
        db.add(deadline)
        db.commit()
        db.refresh(deadline)
        return deadline

    def archive_group(self, db: Session, group_id: str, manager_id: str) -> str:
        """Archive a completed group — export to S3 and mark as ARCHIVED (US-010)."""
        group = self._get_group_or_404(db, group_id)
        self._assert_manager(group, manager_id)

        if group.status not in ("COMPLETED", "ACTIVE"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Group must be COMPLETED or ACTIVE to archive")

        # Serialize group data
        members = db.query(GroupMember).filter(GroupMember.group_id == group_id).all()
        archive_data = {
            "group": {
                "id": group.id, "name": group.name, "member_slots": group.member_slots,
                "amount_per_person": float(group.amount_per_person),
                "targeting_amount": group.targeting_amount,
                "manager_fee_percent": float(group.manager_fee_percent),
            },
            "members": [
                {"user_id": m.user_id, "role": m.role, "has_won": m.has_won, "won_month": m.won_month}
                for m in members
            ],
            "archived_at": datetime.utcnow().isoformat(),
        }

        # Upload to S3
        s3_key = f"archives/{group_id}/{datetime.utcnow().strftime('%Y%m%d')}.json"
        self.s3.put_object(
            Bucket=settings.s3_archives_bucket,
            Key=s3_key,
            Body=json.dumps(archive_data),
            ContentType="application/json",
        )

        # Mark as archived
        group.status = "ARCHIVED"
        db.commit()
        return s3_key

    def _get_group_or_404(self, db: Session, group_id: str) -> ChitGroup:
        group = db.query(ChitGroup).filter(ChitGroup.id == group_id).first()
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
        return group

    def _assert_manager(self, group: ChitGroup, manager_id: str):
        if group.manager_id != manager_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the fund manager can perform this action")


group_service = GroupService()
