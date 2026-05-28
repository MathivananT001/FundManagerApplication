"""Tests for payment service."""
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


@patch("app.routes.payments.get_db")
@patch("app.routes.payments.payment_service")
def test_confirm_payment(mock_svc, mock_db):
    mock_record = MagicMock()
    mock_record.id = "pay-001"
    mock_record.contribution_id = "contrib-001"
    mock_record.member_id = "user-002"
    mock_record.status = "CONFIRMED"
    mock_record.confirmed_by = "manager-001"
    mock_record.confirmed_at = "2026-05-28T10:00:00"
    mock_record.rejection_reason = None
    mock_svc.confirm_payment.return_value = mock_record

    response = client.post("/payments/pay-001/confirm", json={"manager_id": "manager-001"})
    assert response.status_code == 200
    assert response.json()["status"] == "CONFIRMED"


@patch("app.routes.payments.get_db")
@patch("app.routes.payments.payment_service")
def test_reject_payment(mock_svc, mock_db):
    mock_record = MagicMock()
    mock_record.id = "pay-001"
    mock_record.contribution_id = "contrib-001"
    mock_record.member_id = "user-002"
    mock_record.status = "REJECTED"
    mock_record.confirmed_by = "manager-001"
    mock_record.confirmed_at = None
    mock_record.rejection_reason = "Invalid proof"
    mock_svc.reject_payment.return_value = mock_record

    response = client.post("/payments/pay-001/reject", json={
        "manager_id": "manager-001",
        "reason": "Invalid proof",
    })
    assert response.status_code == 200
    assert response.json()["status"] == "REJECTED"


@patch("app.routes.payments.payment_service")
def test_get_upload_url(mock_svc):
    mock_svc.generate_upload_url.return_value = ("https://s3.presigned.url", "proofs/grp/usr/file.jpg")

    response = client.post("/payments/pay-001/proof/upload-url", json={
        "file_name": "receipt.jpg",
        "content_type": "image/jpeg",
    }, headers={"X-User-Id": "user-002"})
    assert response.status_code == 200
    assert "upload_url" in response.json()


@patch("app.routes.payments.get_db")
@patch("app.routes.payments.payment_service")
def test_get_overdue(mock_svc, mock_db):
    mock_svc.get_overdue.return_value = [
        {"group_id": "grp-001", "member_id": "user-002", "amount_due": 5000.0, "month_number": 3}
    ]

    response = client.get("/payments/overdue")
    assert response.status_code == 200
    assert len(response.json()["overdue_members"]) == 1
