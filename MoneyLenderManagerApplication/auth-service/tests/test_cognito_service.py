"""Tests for Cognito service."""
from unittest.mock import patch, MagicMock
import pytest


@patch("app.services.cognito.boto3")
@patch("app.services.cognito.settings")
def test_register_calls_cognito(mock_settings, mock_boto3):
    mock_settings.aws_region = "ap-south-1"
    mock_settings.cognito_user_pool_id = "pool-123"
    mock_settings.cognito_client_id = "client-123"
    mock_settings.cognito_client_secret = ""

    mock_client = MagicMock()
    mock_boto3.client.return_value = mock_client
    mock_client.sign_up.return_value = {"UserSub": "sub-abc"}

    from app.services.cognito import CognitoService
    svc = CognitoService()
    svc.client = mock_client

    result = svc.register("test@example.com", "Pass123!", "Test User")
    assert result == "sub-abc"
    mock_client.sign_up.assert_called_once()


@patch("app.services.cognito.boto3")
@patch("app.services.cognito.settings")
def test_login_email_returns_tokens(mock_settings, mock_boto3):
    mock_settings.aws_region = "ap-south-1"
    mock_settings.cognito_user_pool_id = "pool-123"
    mock_settings.cognito_client_id = "client-123"
    mock_settings.cognito_client_secret = ""

    mock_client = MagicMock()
    mock_boto3.client.return_value = mock_client
    mock_client.initiate_auth.return_value = {
        "AuthenticationResult": {
            "AccessToken": "access-xyz",
            "RefreshToken": "refresh-xyz",
            "ExpiresIn": 3600,
        }
    }

    from app.services.cognito import CognitoService
    svc = CognitoService()
    svc.client = mock_client

    result = svc.login_email("test@example.com", "Pass123!")
    assert result["access_token"] == "access-xyz"
    assert result["refresh_token"] == "refresh-xyz"


@patch("app.services.cognito.boto3")
@patch("app.services.cognito.settings")
def test_logout_calls_global_sign_out(mock_settings, mock_boto3):
    mock_settings.aws_region = "ap-south-1"
    mock_settings.cognito_user_pool_id = "pool-123"
    mock_settings.cognito_client_id = "client-123"
    mock_settings.cognito_client_secret = ""

    mock_client = MagicMock()
    mock_boto3.client.return_value = mock_client

    from app.services.cognito import CognitoService
    svc = CognitoService()
    svc.client = mock_client

    svc.logout("access-token-123")
    mock_client.global_sign_out.assert_called_once_with(AccessToken="access-token-123")
