"""AWS Cognito integration service."""
import hmac
import hashlib
import base64
import boto3
from botocore.exceptions import ClientError
from app.config import settings


class CognitoService:
    def __init__(self):
        self.client = boto3.client("cognito-idp", region_name=settings.aws_region)
        self.user_pool_id = settings.cognito_user_pool_id
        self.client_id = settings.cognito_client_id
        self.client_secret = settings.cognito_client_secret

    def _get_secret_hash(self, username: str) -> str:
        if not self.client_secret:
            return ""
        msg = username + self.client_id
        dig = hmac.new(
            self.client_secret.encode("utf-8"),
            msg.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        return base64.b64encode(dig).decode()

    def register(self, email: str, password: str, full_name: str, phone_number: str = None):
        attrs = [
            {"Name": "email", "Value": email},
            {"Name": "name", "Value": full_name},
        ]
        if phone_number:
            attrs.append({"Name": "phone_number", "Value": phone_number})

        params = {
            "ClientId": self.client_id,
            "Username": email,
            "Password": password,
            "UserAttributes": attrs,
        }
        secret_hash = self._get_secret_hash(email)
        if secret_hash:
            params["SecretHash"] = secret_hash

        response = self.client.sign_up(**params)
        return response["UserSub"]

    def login_email(self, email: str, password: str) -> dict:
        params = {
            "AuthFlow": "USER_PASSWORD_AUTH",
            "ClientId": self.client_id,
            "AuthParameters": {"USERNAME": email, "PASSWORD": password},
        }
        secret_hash = self._get_secret_hash(email)
        if secret_hash:
            params["AuthParameters"]["SECRET_HASH"] = secret_hash

        response = self.client.initiate_auth(**params)
        result = response["AuthenticationResult"]
        return {
            "access_token": result["AccessToken"],
            "refresh_token": result["RefreshToken"],
            "expires_in": result["ExpiresIn"],
        }

    def initiate_phone_otp(self, phone_number: str) -> dict:
        params = {
            "AuthFlow": "CUSTOM_AUTH",
            "ClientId": self.client_id,
            "AuthParameters": {"USERNAME": phone_number},
        }
        secret_hash = self._get_secret_hash(phone_number)
        if secret_hash:
            params["AuthParameters"]["SECRET_HASH"] = secret_hash

        response = self.client.initiate_auth(**params)
        return {"session": response["Session"]}

    def verify_phone_otp(self, phone_number: str, otp_code: str, session: str) -> dict:
        params = {
            "ClientId": self.client_id,
            "ChallengeName": "CUSTOM_CHALLENGE",
            "Session": session,
            "ChallengeResponses": {"USERNAME": phone_number, "ANSWER": otp_code},
        }
        secret_hash = self._get_secret_hash(phone_number)
        if secret_hash:
            params["ChallengeResponses"]["SECRET_HASH"] = secret_hash

        response = self.client.respond_to_auth_challenge(**params)
        result = response["AuthenticationResult"]
        return {
            "access_token": result["AccessToken"],
            "refresh_token": result["RefreshToken"],
            "expires_in": result["ExpiresIn"],
        }

    def login_google(self, google_token: str) -> dict:
        """Exchange Google OAuth token via Cognito hosted UI token endpoint."""
        # In production, this calls the Cognito token endpoint with the authorization code
        # For the service layer, we validate the Google token and create/get the Cognito user
        params = {
            "AuthFlow": "USER_PASSWORD_AUTH",
            "ClientId": self.client_id,
            "AuthParameters": {"USERNAME": google_token, "PASSWORD": google_token},
        }
        # Note: Actual Google OAuth flow is handled client-side via Cognito Hosted UI
        # This endpoint receives the tokens after the OAuth redirect
        raise NotImplementedError("Google OAuth handled via Cognito Hosted UI redirect")

    def refresh_token(self, refresh_token: str) -> dict:
        params = {
            "AuthFlow": "REFRESH_TOKEN_AUTH",
            "ClientId": self.client_id,
            "AuthParameters": {"REFRESH_TOKEN": refresh_token},
        }
        response = self.client.initiate_auth(**params)
        result = response["AuthenticationResult"]
        return {
            "access_token": result["AccessToken"],
            "expires_in": result["ExpiresIn"],
        }

    def logout(self, access_token: str):
        self.client.global_sign_out(AccessToken=access_token)

    def get_user(self, access_token: str) -> dict:
        response = self.client.get_user(AccessToken=access_token)
        attrs = {a["Name"]: a["Value"] for a in response["UserAttributes"]}
        return {"sub": attrs.get("sub"), "email": attrs.get("email"), "name": attrs.get("name")}


cognito_service = CognitoService()
