"""DynamoDB services for device tokens and notification logs."""
import time
import boto3
from app.config import settings


class DeviceTokenService:
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb", region_name=settings.aws_region)
        self.table = self.dynamodb.Table(settings.dynamodb_device_tokens_table)

    def register_token(self, user_id: str, fcm_token: str, platform: str):
        self.table.put_item(Item={
            "user_id": user_id,
            "token": fcm_token,
            "platform": platform,
            "registered_at": int(time.time()),
        })

    def deregister_token(self, user_id: str, fcm_token: str):
        self.table.delete_item(Key={"user_id": user_id, "token": fcm_token})

    def get_tokens(self, user_id: str) -> list[dict]:
        response = self.table.query(
            KeyConditionExpression="user_id = :uid",
            ExpressionAttributeValues={":uid": user_id},
        )
        return response.get("Items", [])


class NotificationLogService:
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb", region_name=settings.aws_region)
        self.table = self.dynamodb.Table(settings.dynamodb_notification_logs_table)

    def log_notification(self, user_id: str, channel: str, template_key: str, status: str):
        self.table.put_item(Item={
            "user_id": user_id,
            "timestamp": str(int(time.time() * 1000)),
            "channel": channel,
            "template_key": template_key,
            "status": status,
            "ttl": int(time.time()) + (90 * 24 * 60 * 60),  # 90 days
        })

    def get_history(self, user_id: str, limit: int = 50) -> list[dict]:
        response = self.table.query(
            KeyConditionExpression="user_id = :uid",
            ExpressionAttributeValues={":uid": user_id},
            ScanIndexForward=False,
            Limit=limit,
        )
        return response.get("Items", [])


device_token_service = DeviceTokenService()
notification_log_service = NotificationLogService()
