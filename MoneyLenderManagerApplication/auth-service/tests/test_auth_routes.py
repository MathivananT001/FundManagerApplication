"""Tests for auth routes."""
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@patch("app.routes.auth.cognito_service")
@patch("app.routes.auth.get_db")
def test_register_success(mock_db, mock_cognito):
    mock_cognito.register.return_value = "cognito-sub-123"
    mock_session = MagicMock()
    mock_db.return_value = iter([mock_session])

    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "SecurePass123!",
        "full_name": "Test User",
    })
    assert response.status_code == 201
    assert "Registration successful" in response.json()["message"]


@patch("app.routes.auth.cognito_service")
@patch("app.routes.auth.get_db")
def test_login_email_success(mock_db, mock_cognito):
    mock_cognito.login_email.return_value = {
        "access_token": "access-123",
        "refresh_token": "refresh-123",
        "expires_in": 3600,
    }
    mock_session = MagicMock()
    mock_user = MagicMock()
    mock_user.id = "user-123"
    mock_session.query.return_value.filter.return_value.first.return_value = mock_user
    mock_db.return_value = iter([mock_session])

    response = client.post("/auth/login/email", json={
        "email": "test@example.com",
        "password": "SecurePass123!",
    })
    assert response.status_code == 200
    assert response.json()["access_token"] == "access-123"


@patch("app.routes.auth.cognito_service")
def test_login_email_invalid_credentials(mock_cognito):
    mock_cognito.login_email.side_effect = Exception("Incorrect username or password")

    response = client.post("/auth/login/email", json={
        "email": "test@example.com",
        "password": "wrong",
    })
    assert response.status_code == 401


@patch("app.routes.auth.cognito_service")
def test_login_phone_otp_initiated(mock_cognito):
    mock_cognito.initiate_phone_otp.return_value = {"session": "session-abc"}

    response = client.post("/auth/login/phone", json={
        "phone_number": "+919876543210",
    })
    assert response.status_code == 200
    assert response.json()["session"] == "session-abc"


@patch("app.routes.auth.cognito_service")
def test_refresh_token_success(mock_cognito):
    mock_cognito.refresh_token.return_value = {
        "access_token": "new-access-123",
        "expires_in": 3600,
    }

    response = client.post("/auth/refresh", json={
        "refresh_token": "refresh-123",
    })
    assert response.status_code == 200
    assert response.json()["access_token"] == "new-access-123"
