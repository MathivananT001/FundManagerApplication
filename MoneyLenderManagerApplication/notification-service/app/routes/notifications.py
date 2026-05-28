"""Notification API routes."""
from typing import List
from fastapi import APIRouter, HTTPException, status

from app.schemas.notifications import (
    SendSMSRequest, SendPushRequest, BulkSMSRequest, BulkPushRequest,
    RegisterDeviceRequest, DeregisterDeviceRequest,
    NotificationLogResponse, SuccessResponse,
)
from app.services.sns_service import sns_service
from app.services.dynamodb_service import device_token_service, notification_log_service
from app.services.localization import localization_service

router = APIRouter()


@router.post("/send-sms", response_model=SuccessResponse)
async def send_sms(payload: SendSMSRequest):
    """Send localized SMS to a phone number (US-025, US-026)."""
    message = localization_service.translate(payload.template_key, payload.language, **payload.params)
    message_id = sns_service.send_sms(payload.phone_number, message)
    notification_log_service.log_notification(
        user_id=payload.phone_number, channel="sms",
        template_key=payload.template_key, status="sent",
    )
    return SuccessResponse(message="SMS sent", message_id=message_id)


@router.post("/send-push", response_model=SuccessResponse)
async def send_push(payload: SendPushRequest):
    """Send push notification to a user's devices."""
    tokens = device_token_service.get_tokens(payload.user_id)
    if not tokens:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No device tokens found")

    for token_record in tokens:
        sns_service.send_push(token_record["token"], payload.title, payload.body, payload.data)

    notification_log_service.log_notification(
        user_id=payload.user_id, channel="push",
        template_key=payload.title, status="sent",
    )
    return SuccessResponse(message=f"Push sent to {len(tokens)} device(s)")


@router.post("/send-bulk-sms", response_model=SuccessResponse)
async def send_bulk_sms(payload: BulkSMSRequest):
    """Send SMS to multiple phone numbers (US-023, US-024)."""
    message = localization_service.translate(payload.template_key, payload.language, **payload.params)
    sns_service.send_bulk_sms(payload.phone_numbers, message)
    return SuccessResponse(message=f"Bulk SMS sent to {len(payload.phone_numbers)} recipients")


@router.post("/send-bulk-push", response_model=SuccessResponse)
async def send_bulk_push(payload: BulkPushRequest):
    """Send push notification to multiple users."""
    count = 0
    for user_id in payload.user_ids:
        tokens = device_token_service.get_tokens(user_id)
        for token_record in tokens:
            sns_service.send_push(token_record["token"], payload.title, payload.body, payload.data)
            count += 1
    return SuccessResponse(message=f"Push sent to {count} device(s)")


@router.post("/device-token", response_model=SuccessResponse)
async def register_device(payload: RegisterDeviceRequest):
    """Register FCM device token."""
    device_token_service.register_token(payload.user_id, payload.fcm_token, payload.platform)
    return SuccessResponse(message="Device token registered")


@router.delete("/device-token", response_model=SuccessResponse)
async def deregister_device(payload: DeregisterDeviceRequest):
    """Deregister FCM device token."""
    device_token_service.deregister_token(payload.user_id, payload.fcm_token)
    return SuccessResponse(message="Device token removed")


@router.get("/history/{user_id}", response_model=List[NotificationLogResponse])
async def get_history(user_id: str, limit: int = 50):
    """Get notification history for a user."""
    items = notification_log_service.get_history(user_id, limit)
    return [NotificationLogResponse(**item) for item in items]


@router.get("/localization/{language_code}")
async def get_language_bundle(language_code: str):
    """Fetch language bundle (US-027)."""
    try:
        bundle = localization_service.get_bundle(language_code)
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Bundle not found: {language_code}")
    return bundle
