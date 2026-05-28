"""Auction service business logic — bidding, winner determination, contribution calculation."""
import random
import boto3
import httpx
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.config import settings
from app.models.auction import Auction, Bid


class AuctionService:
    def schedule(self, db: Session, group_id: str, month_number: int, scheduled_at: datetime, manager_id: str) -> Auction:
        """Schedule a new auction (US-011)."""
        existing = db.query(Auction).filter(
            Auction.group_id == group_id, Auction.month_number == month_number
        ).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Auction already exists for this month")

        auction = Auction(group_id=group_id, month_number=month_number, scheduled_at=scheduled_at)
        db.add(auction)
        db.commit()
        db.refresh(auction)
        return auction

    def open_auction(self, db: Session, auction_id: str, manager_id: str) -> Auction:
        """Open auction for bidding (US-011)."""
        auction = self._get_auction_or_404(db, auction_id)
        if auction.status != "SCHEDULED":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Auction must be SCHEDULED to open")
        auction.status = "OPEN"
        auction.opened_at = datetime.utcnow()
        db.commit()
        db.refresh(auction)
        return auction

    def place_bid(self, db: Session, auction_id: str, member_id: str, bid_amount: float) -> Bid:
        """Place a bid during an open auction (US-012)."""
        auction = self._get_auction_or_404(db, auction_id)
        if auction.status != "OPEN":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Auction is not open")
        if bid_amount <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bid must be positive")

        bid = Bid(auction_id=auction_id, member_id=member_id, bid_amount=bid_amount)
        db.add(bid)
        db.commit()
        db.refresh(bid)
        return bid

    def close_auction(self, db: Session, auction_id: str, manager_id: str, group_member_count: int, manager_fee_percent: float) -> dict:
        """Close auction, determine winner, calculate disbursement (US-011, US-013, US-014, US-015)."""
        auction = self._get_auction_or_404(db, auction_id)
        if auction.status != "OPEN":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Auction must be OPEN to close")

        auction.status = "CLOSED"
        auction.closed_at = datetime.utcnow()

        # Determine winner
        bids = db.query(Bid).filter(Bid.auction_id == auction_id).order_by(Bid.bid_amount.desc()).all()

        if bids:
            # Highest bidder wins (US-013)
            winner_bid = bids[0]
            auction.winner_id = winner_bid.member_id
            auction.winning_bid_amount = winner_bid.bid_amount
        else:
            # No bids — random selection from non-winners (US-014)
            non_winners = self._fetch_non_winners(auction.group_id)
            if not non_winners:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No eligible non-winners")
            winner = random.choice(non_winners)
            auction.winner_id = winner["user_id"]
            auction.winning_bid_amount = 0

        # Calculate disbursement (US-015)
        # monthly_auction_amount = amount_per_person (since targeting/members = amount_per_person)
        # disbursement = monthly_auction_amount - winning_bid - manager_fee
        monthly_auction_amount = self._get_monthly_auction_amount(auction.group_id)
        manager_fee = monthly_auction_amount * (manager_fee_percent / 100)
        disbursement = monthly_auction_amount - float(auction.winning_bid_amount) - manager_fee
        auction.disbursement_amount = max(disbursement, 0)

        # Contribution per member = winning_bid_amount / (members excluding bot)
        contribution_per_member = float(auction.winning_bid_amount) / max(group_member_count - 1, 1) if auction.winning_bid_amount else 0

        db.commit()
        db.refresh(auction)

        return {
            "winner_id": auction.winner_id,
            "winning_bid_amount": float(auction.winning_bid_amount),
            "disbursement_amount": float(auction.disbursement_amount),
            "contribution_per_member": contribution_per_member,
        }

    def get_highest_bid(self, db: Session, auction_id: str) -> Bid | None:
        """Get current highest bid."""
        return db.query(Bid).filter(Bid.auction_id == auction_id).order_by(Bid.bid_amount.desc()).first()

    def get_bid_history(self, db: Session, auction_id: str) -> list[Bid]:
        """Get all bids for an auction."""
        return db.query(Bid).filter(Bid.auction_id == auction_id).order_by(Bid.placed_at.desc()).all()

    def list_by_group(self, db: Session, group_id: str) -> list[Auction]:
        """List all auctions for a group."""
        return db.query(Auction).filter(Auction.group_id == group_id).order_by(Auction.month_number).all()

    def get_upcoming(self, db: Session) -> list[Auction]:
        """Get upcoming scheduled auctions (used by Bot Agent)."""
        return db.query(Auction).filter(Auction.status == "SCHEDULED").all()

    def _get_auction_or_404(self, db: Session, auction_id: str) -> Auction:
        auction = db.query(Auction).filter(Auction.id == auction_id).first()
        if not auction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auction not found")
        return auction

    def _fetch_non_winners(self, group_id: str) -> list[dict]:
        """Fetch non-winners from group service."""
        try:
            resp = httpx.get(f"{settings.group_service_url}/groups/{group_id}/non-winners", timeout=5)
            return resp.json() if resp.status_code == 200 else []
        except Exception:
            return []

    def _get_monthly_auction_amount(self, group_id: str) -> float:
        """Fetch monthly auction amount from group service."""
        try:
            resp = httpx.get(f"{settings.group_service_url}/groups/{group_id}", timeout=5)
            if resp.status_code == 200:
                return resp.json().get("monthly_auction_amount", 0)
        except Exception:
            pass
        return 0


auction_service = AuctionService()
