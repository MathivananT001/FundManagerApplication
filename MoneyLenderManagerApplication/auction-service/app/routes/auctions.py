"""Auction API routes."""
from typing import List
from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auction import (
    ScheduleAuctionRequest, PlaceBidRequest,
    AuctionResponse, AuctionDetailResponse, BidResponse,
    WinnerResponse, SuccessResponse,
)
from app.services.auction_service import auction_service
from app.services.websocket_manager import ws_manager

router = APIRouter()


def _get_user_id(x_user_id: str = Header(...)) -> str:
    return x_user_id


def _to_auction_response(a) -> AuctionResponse:
    return AuctionResponse(
        id=a.id, group_id=a.group_id, month_number=a.month_number,
        scheduled_at=str(a.scheduled_at) if a.scheduled_at else None,
        opened_at=str(a.opened_at) if a.opened_at else None,
        closed_at=str(a.closed_at) if a.closed_at else None,
        status=a.status, winner_id=a.winner_id,
        winning_bid_amount=float(a.winning_bid_amount) if a.winning_bid_amount else None,
        disbursement_amount=float(a.disbursement_amount) if a.disbursement_amount else None,
    )


@router.post("", response_model=AuctionResponse, status_code=status.HTTP_201_CREATED)
async def schedule_auction(payload: ScheduleAuctionRequest, user_id: str = Depends(_get_user_id), db: Session = Depends(get_db)):
    """Schedule a new auction (US-011)."""
    auction = auction_service.schedule(db, payload.group_id, payload.month_number, payload.scheduled_at, user_id)
    return _to_auction_response(auction)


@router.post("/{auction_id}/open", response_model=AuctionResponse)
async def open_auction(auction_id: str, user_id: str = Depends(_get_user_id), db: Session = Depends(get_db)):
    """Open auction for bidding (US-011)."""
    auction = auction_service.open_auction(db, auction_id, user_id)
    ws_manager.broadcast(auction_id, {"event": "AUCTION_OPENED", "auction_id": auction_id})
    return _to_auction_response(auction)


@router.post("/{auction_id}/bid", response_model=BidResponse)
async def place_bid(auction_id: str, payload: PlaceBidRequest, db: Session = Depends(get_db)):
    """Place a bid (US-012)."""
    bid = auction_service.place_bid(db, auction_id, payload.member_id, payload.bid_amount)
    ws_manager.broadcast(auction_id, {
        "event": "NEW_BID",
        "member_id": payload.member_id,
        "bid_amount": payload.bid_amount,
    })
    return BidResponse(
        id=bid.id, auction_id=bid.auction_id, member_id=bid.member_id,
        bid_amount=float(bid.bid_amount), placed_at=str(bid.placed_at),
    )


@router.post("/{auction_id}/close", response_model=WinnerResponse)
async def close_auction(
    auction_id: str, user_id: str = Depends(_get_user_id),
    group_member_count: int = 10, manager_fee_percent: float = 2.0,
    db: Session = Depends(get_db),
):
    """Close auction and determine winner (US-011, US-013, US-014, US-015)."""
    result = auction_service.close_auction(db, auction_id, user_id, group_member_count, manager_fee_percent)
    ws_manager.broadcast(auction_id, {"event": "AUCTION_CLOSED", "winner_id": result["winner_id"]})
    return WinnerResponse(**result)


@router.get("/{auction_id}", response_model=AuctionDetailResponse)
async def get_auction(auction_id: str, db: Session = Depends(get_db)):
    """Get auction details with bid history."""
    auction = auction_service._get_auction_or_404(db, auction_id)
    bids = auction_service.get_bid_history(db, auction_id)
    resp = _to_auction_response(auction)
    return AuctionDetailResponse(
        **resp.model_dump(),
        bids=[BidResponse(id=b.id, auction_id=b.auction_id, member_id=b.member_id,
                          bid_amount=float(b.bid_amount), placed_at=str(b.placed_at)) for b in bids],
    )


@router.get("/group/{group_id}", response_model=List[AuctionResponse])
async def list_auctions(group_id: str, db: Session = Depends(get_db)):
    """List all auctions for a group."""
    auctions = auction_service.list_by_group(db, group_id)
    return [_to_auction_response(a) for a in auctions]


@router.get("/{auction_id}/highest-bid", response_model=BidResponse)
async def get_highest_bid(auction_id: str, db: Session = Depends(get_db)):
    """Get current highest bid."""
    bid = auction_service.get_highest_bid(db, auction_id)
    if not bid:
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No bids yet")
    return BidResponse(
        id=bid.id, auction_id=bid.auction_id, member_id=bid.member_id,
        bid_amount=float(bid.bid_amount), placed_at=str(bid.placed_at),
    )


@router.get("/upcoming")
async def get_upcoming(db: Session = Depends(get_db)):
    """Get upcoming scheduled auctions (Bot Agent)."""
    auctions = auction_service.get_upcoming(db)
    return {"auctions": [_to_auction_response(a).model_dump() for a in auctions]}


# WebSocket Lambda handlers (invoked by API Gateway WebSocket)
@router.post("/ws/connect")
async def ws_connect(auction_id: str, connection_id: str, member_id: str):
    """Register WebSocket connection (US-016)."""
    ws_manager.connect(auction_id, connection_id, member_id)
    return SuccessResponse(message="Connected")


@router.post("/ws/disconnect")
async def ws_disconnect(auction_id: str, connection_id: str):
    """Remove WebSocket connection."""
    ws_manager.disconnect(auction_id, connection_id)
    return SuccessResponse(message="Disconnected")
