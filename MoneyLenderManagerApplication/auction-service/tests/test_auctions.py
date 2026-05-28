"""Tests for auction service."""
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
HEADER = {"X-User-Id": "manager-001"}


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


@patch("app.routes.auctions.get_db")
@patch("app.routes.auctions.auction_service")
def test_schedule_auction(mock_svc, mock_db):
    mock_auction = MagicMock()
    mock_auction.id = "auc-001"
    mock_auction.group_id = "grp-001"
    mock_auction.month_number = 1
    mock_auction.scheduled_at = "2026-06-01T10:00:00"
    mock_auction.opened_at = None
    mock_auction.closed_at = None
    mock_auction.status = "SCHEDULED"
    mock_auction.winner_id = None
    mock_auction.winning_bid_amount = None
    mock_auction.disbursement_amount = None
    mock_svc.schedule.return_value = mock_auction

    response = client.post("/auctions", json={
        "group_id": "grp-001",
        "month_number": 1,
        "scheduled_at": "2026-06-01T10:00:00",
    }, headers=HEADER)
    assert response.status_code == 201
    assert response.json()["status"] == "SCHEDULED"


@patch("app.routes.auctions.ws_manager")
@patch("app.routes.auctions.get_db")
@patch("app.routes.auctions.auction_service")
def test_place_bid(mock_svc, mock_db, mock_ws):
    mock_bid = MagicMock()
    mock_bid.id = "bid-001"
    mock_bid.auction_id = "auc-001"
    mock_bid.member_id = "user-002"
    mock_bid.bid_amount = 1500.0
    mock_bid.placed_at = "2026-06-01T10:05:00"
    mock_svc.place_bid.return_value = mock_bid

    response = client.post("/auctions/auc-001/bid", json={
        "member_id": "user-002",
        "bid_amount": 1500.0,
    })
    assert response.status_code == 200
    assert response.json()["bid_amount"] == 1500.0
    mock_ws.broadcast.assert_called_once()


@patch("app.routes.auctions.ws_manager")
@patch("app.routes.auctions.get_db")
@patch("app.routes.auctions.auction_service")
def test_close_auction_with_winner(mock_svc, mock_db, mock_ws):
    mock_svc.close_auction.return_value = {
        "winner_id": "user-002",
        "winning_bid_amount": 1500.0,
        "disbursement_amount": 3400.0,
        "contribution_per_member": 166.67,
    }

    response = client.post("/auctions/auc-001/close", headers=HEADER)
    assert response.status_code == 200
    assert response.json()["winner_id"] == "user-002"
    assert response.json()["disbursement_amount"] == 3400.0
