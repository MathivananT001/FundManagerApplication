"""Auth API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.auth import (
    RegisterRequest, EmailLoginRequest, PhoneOTPRequest, VerifyOTPRequest,
    GoogleLoginRequest, RefreshTokenRequest, UpdateProfileRequest,
    SetLanguageRequest, AssignRoleRequest, TokenResponse, OTPInitiatedResponse,
    UserProfileResponse, SuccessResponse,
)
from app.services.cognito import cognito_service
from app.services.session import session_service
from app.middleware.auth import get_current_user, require_role

router = APIRouter()


@router.post("/register", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user with email + password (US-001)."""
    cognito_sub = cognito_service.register(
        email=payload.email, password=payload.password,
        full_name=payload.full_name, phone_number=payload.phone_number,
    )
    user = User(
        cognito_sub=cognito_sub, email=payload.email,
        full_name=payload.full_name, phone_number=payload.phone_number,
        language_preference=payload.language_preference.value,
    )
    role = UserRole(user=user, role="MEMBER")
    db.add(user)
    db.add(role)
    db.commit()
    return SuccessResponse(message="Registration successful. Please verify your email.")


@router.post("/login/email", response_model=TokenResponse)
async def login_email(payload: EmailLoginRequest, db: Session = Depends(get_db)):
    """Login with email + password (US-001)."""
    try:
        tokens = cognito_service.login_email(payload.email, payload.password)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    user = db.query(User).filter(User.email == payload.email).first()
    if user:
        session_service.create_session(user.id)

    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        expires_in=tokens["expires_in"],
    )


@router.post("/login/phone", response_model=OTPInitiatedResponse)
async def login_phone(payload: PhoneOTPRequest):
    """Initiate phone OTP login (US-002)."""
    try:
        result = cognito_service.initiate_phone_otp(payload.phone_number)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return OTPInitiatedResponse(message="OTP sent", session=result["session"])


@router.post("/login/phone/verify", response_model=TokenResponse)
async def verify_phone_otp(payload: VerifyOTPRequest):
    """Verify phone OTP and return tokens (US-002)."""
    try:
        tokens = cognito_service.verify_phone_otp(
            payload.phone_number, payload.otp_code, payload.session if hasattr(payload, 'session') else ""
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        expires_in=tokens["expires_in"],
    )


@router.post("/login/google", response_model=TokenResponse)
async def login_google(payload: GoogleLoginRequest):
    """Google OAuth token exchange (US-003)."""
    # Google OAuth is handled via Cognito Hosted UI on the client side.
    # This endpoint validates the resulting Cognito tokens.
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Google login handled via Cognito Hosted UI redirect flow",
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshTokenRequest):
    """Refresh access token."""
    try:
        tokens = cognito_service.refresh_token(payload.refresh_token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=payload.refresh_token,
        expires_in=tokens["expires_in"],
    )


@router.post("/logout", response_model=SuccessResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """Logout and revoke session."""
    session_service.delete_all_sessions(current_user.id)
    return SuccessResponse(message="Logged out successfully")


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile (US-004)."""
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        phone_number=current_user.phone_number,
        full_name=current_user.full_name,
        language_preference=current_user.language_preference,
        roles=[r.role for r in current_user.roles],
    )


@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    payload: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user profile (US-004)."""
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    if payload.phone_number is not None:
        current_user.phone_number = payload.phone_number
    db.commit()
    db.refresh(current_user)
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        phone_number=current_user.phone_number,
        full_name=current_user.full_name,
        language_preference=current_user.language_preference,
        roles=[r.role for r in current_user.roles],
    )


@router.put("/profile/language", response_model=SuccessResponse)
async def set_language(
    payload: SetLanguageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Set language preference (US-004)."""
    current_user.language_preference = payload.language.value
    db.commit()
    return SuccessResponse(message=f"Language set to {payload.language.value}")


@router.post("/role", response_model=SuccessResponse)
async def assign_role(
    payload: AssignRoleRequest,
    current_user: User = Depends(require_role("FUND_MANAGER")),
    db: Session = Depends(get_db),
):
    """Assign role to user (admin only)."""
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    existing = db.query(UserRole).filter(
        UserRole.user_id == payload.user_id, UserRole.role == payload.role.value
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role already assigned")
    role = UserRole(user_id=payload.user_id, role=payload.role.value)
    db.add(role)
    db.commit()
    return SuccessResponse(message=f"Role {payload.role.value} assigned")
