"""Tests for notification service."""
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


@patch("app.routes.notifications.sns_service")
@patch("app.routes.notifications.localization_service")
@patch("app.routes.notifications.notification_log_service")
def test_send_sms(mock_log, mock_l10n, mock_sns):
    mock_l10n.translate.return_value = "Your payment is due"
    mock_sns.send_sms.return_value = "msg-123"

    response = client.post("/notifications/send-sms", json={
        "phone_number": "+919876543210",
        "template_key": "payment_reminder",
        "language": "en",
    })
    assert response.status_code == 200
    assert response.json()["message_id"] == "msg-123"


@patch("app.routes.notifications.device_token_service")
@patch("app.routes.notifications.sns_service")
@patch("app.routes.notifications.notification_log_service")
def test_send_push(mock_log, mock_sns, mock_device):
    mock_device.get_tokens.return_value = [{"token": "fcm-token-1", "platform": "android"}]
    mock_sns.send_push.return_value = "msg-456"

    response = client.post("/notifications/send-push", json={
        "user_id": "user-123",
        "title": "Auction Starting",
        "body": "Join now!",
    })
    assert response.status_code == 200


@patch("app.routes.notifications.device_token_service")
def test_send_push_no_tokens(mock_device):
    mock_device.get_tokens.return_value = []

    response = client.post("/notifications/send-push", json={
        "user_id": "user-no-device",
        "title": "Test",
        "body": "Test",
    })
    assert response.status_code == 404


@patch("app.routes.notifications.device_token_service")
def test_register_device_token(mock_device):
    response = client.post("/notifications/device-token", json={
        "user_id": "user-123",
        "fcm_token": "token-abc",
        "platform": "android",
    })
    assert response.status_code == 200
    mock_device.register_token.assert_called_once()


@patch("app.routes.notifications.localization_service")
def test_get_language_bundle(mock_l10n):
    mock_l10n.get_bundle.return_value = {"greeting": "Hello", "farewell": "Goodbye"}

    response = client.get("/notifications/localization/en")
    assert response.status_code == 200
    assert response.json()["greeting"] == "Hello"
