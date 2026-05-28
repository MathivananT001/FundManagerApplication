"""Tests for group service."""
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
MANAGER_HEADER = {"X-User-Id": "manager-001"}


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


@patch("app.routes.groups.get_db")
@patch("app.routes.groups.group_service")
def test_create_group(mock_svc, mock_db):
    mock_group = MagicMock()
    mock_group.id = "grp-001"
    mock_group.name = "Test Fund"
    mock_group.description = None
    mock_group.manager_id = "manager-001"
    mock_group.member_slots = 10
    mock_group.amount_per_person = 5000.0
    mock_group.targeting_amount = 50000.0
    mock_group.monthly_auction_amount = 5000.0
    mock_group.manager_fee_percent = 2.0
    mock_group.currency = "INR"
    mock_group.status = "DRAFT"
    mock_group.members = []
    mock_svc.create_group.return_value = mock_group

    response = client.post("/groups", json={
        "name": "Test Fund",
        "member_slots": 10,
        "amount_per_person": 5000.0,
    }, headers=MANAGER_HEADER)
    assert response.status_code == 201
    assert response.json()["targeting_amount"] == 50000.0


@patch("app.routes.groups.get_db")
@patch("app.routes.groups.group_service")
def test_create_group_invalid_slots(mock_svc, mock_db):
    from fastapi import HTTPException
    mock_svc.create_group.side_effect = HTTPException(status_code=400, detail="member_slots must be 8-15")

    response = client.post("/groups", json={
        "name": "Bad Fund",
        "member_slots": 3,
        "amount_per_person": 1000.0,
    }, headers=MANAGER_HEADER)
    assert response.status_code == 400


@patch("app.routes.groups.get_db")
@patch("app.routes.groups.group_service")
def test_add_member(mock_svc, mock_db):
    mock_member = MagicMock()
    mock_member.id = "gm-001"
    mock_member.user_id = "user-002"
    mock_member.role = "MEMBER"
    mock_member.has_won = False
    mock_member.won_month = None
    mock_member.status = "ACTIVE"
    mock_svc.add_member.return_value = mock_member

    response = client.post("/groups/grp-001/members", json={
        "user_id": "user-002",
    }, headers=MANAGER_HEADER)
    assert response.status_code == 201
    assert response.json()["user_id"] == "user-002"


@patch("app.routes.groups.get_db")
@patch("app.routes.groups.group_service")
def test_archive_group(mock_svc, mock_db):
    mock_svc.archive_group.return_value = "archives/grp-001/20260528.json"

    response = client.post("/groups/grp-001/archive", headers=MANAGER_HEADER)
    assert response.status_code == 200
    assert "s3_key" in response.json()
