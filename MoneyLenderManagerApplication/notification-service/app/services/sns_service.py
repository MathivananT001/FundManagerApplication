"""AWS SNS service for SMS and push notifications."""
import boto3
from app.config import settings


class SNSService:
    def __init__(self):
        self.client = boto3.client("sns", region_name=settings.aws_region)

    def send_sms(self, phone_number: str, message: str) -> str:
        """Send SMS via SNS (US-023, US-024, US-025, US-026)."""
        response = self.client.publish(
            PhoneNumber=phone_number,
            Message=message,
            MessageAttributes={
                "AWS.SNS.SMS.SenderID": {
                    "DataType": "String",
                    "StringValue": settings.sns_sms_sender_id,
                },
                "AWS.SNS.SMS.SMSType": {
                    "DataType": "String",
                    "StringValue": "Transactional",
                },
            },
        )
        return response["MessageId"]

    def send_push(self, device_token: str, title: str, body: str, data: dict = None) -> str:
        """Send push notification via SNS → FCM."""
        import json
        message = {
            "GCM": json.dumps({
                "notification": {"title": title, "body": body},
                "data": data or {},
            })
        }
        response = self.client.publish(
            TargetArn=device_token,
            Message=json.dumps(message),
            MessageStructure="json",
        )
        return response["MessageId"]

    def send_bulk_sms(self, phone_numbers: list[str], message: str) -> list[str]:
        """Send SMS to multiple recipients."""
        return [self.send_sms(phone, message) for phone in phone_numbers]


sns_service = SNSService()
