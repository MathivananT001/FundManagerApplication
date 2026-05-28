"""DynamoDB session management."""
import uuid
import time
import boto3
from app.config import settings

SESSION_TTL_SECONDS = 30 * 24 * 60 * 60  # 30 days


class SessionService:
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb", region_name=settings.aws_region)
        self.table = self.dynamodb.Table(settings.dynamodb_sessions_table)

    def create_session(self, user_id: str) -> str:
        session_id = str(uuid.uuid4())
        self.table.put_item(Item={
            "user_id": user_id,
            "session_id": session_id,
            "created_at": int(time.time()),
            "ttl": int(time.time()) + SESSION_TTL_SECONDS,
        })
        return session_id

    def get_session(self, user_id: str, session_id: str) -> dict | None:
        response = self.table.get_item(Key={"user_id": user_id, "session_id": session_id})
        return response.get("Item")

    def delete_session(self, user_id: str, session_id: str):
        self.table.delete_item(Key={"user_id": user_id, "session_id": session_id})

    def delete_all_sessions(self, user_id: str):
        response = self.table.query(
            KeyConditionExpression="user_id = :uid",
            ExpressionAttributeValues={":uid": user_id},
        )
        for item in response.get("Items", []):
            self.table.delete_item(Key={"user_id": user_id, "session_id": item["session_id"]})


session_service = SessionService()
