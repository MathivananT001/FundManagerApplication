"""Pydantic schemas for auction service."""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


# Requests
class ScheduleAuctionRequest(BaseModel):
    group_id: str
    month_number: int
    scheduled_at: datetime


class PlaceBidRequest(BaseModel):
    member_id: str
    bid_amount: float


# Responses
class BidResponse(BaseModel):
    id: str
    auction_id: str
    member_id: str
    bid_amount: float
    placed_at: str

    class Config:
        from_attributes = True


class AuctionResponse(BaseModel):
    id: str
    group_id: str
    month_number: int
    scheduled_at: Optional[str]
    opened_at: Optional[str]
    closed_at: Optional[str]
    status: str
    winner_id: Optional[str]
    winning_bid_amount: Optional[float]
    disbursement_amount: Optional[float]

    class Config:
        from_attributes = True


class AuctionDetailResponse(AuctionResponse):
    bids: List[BidResponse]


class WinnerResponse(BaseModel):
    winner_id: str
    winning_bid_amount: float
    disbursement_amount: float
    contribution_per_member: float


class ContributionRecord(BaseModel):
    member_id: str
    amount_due: float


class SuccessResponse(BaseModel):
    message: str
