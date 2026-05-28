"""JWT validation and role-based authorization middleware."""
import json
import urllib.request
from functools import lru_cache
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User

security = HTTPBearer()


@lru_cache()
def _get_cognito_jwks() -> dict:
    """Fetch Cognito JWKS for token verification."""
    url = (
        f"https://cognito-idp.{settings.aws_region}.amazonaws.com/"
        f"{settings.cognito_user_pool_id}/.well-known/jwks.json"
    )
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read())


def _decode_token(token: str) -> dict:
    """Decode and verify a Cognito JWT."""
    jwks = _get_cognito_jwks()
    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")

    key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
    if not key:
        raise JWTError("Key not found")

    payload = jwt.decode(
        token, key, algorithms=["RS256"],
        audience=settings.cognito_client_id,
        issuer=f"https://cognito-idp.{settings.aws_region}.amazonaws.com/{settings.cognito_user_pool_id}",
    )
    return payload


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Extract and validate JWT, return the current user."""
    try:
        payload = _decode_token(credentials.credentials)
    except (JWTError, Exception):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    cognito_sub = payload.get("sub")
    if not cognito_sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user = db.query(User).filter(User.cognito_sub == cognito_sub).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def require_role(role: str):
    """Factory that returns a dependency requiring a specific role."""
    async def _check(current_user: User = Depends(get_current_user)) -> User:
        user_roles = [r.role for r in current_user.roles]
        if role not in user_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user
    return _check
