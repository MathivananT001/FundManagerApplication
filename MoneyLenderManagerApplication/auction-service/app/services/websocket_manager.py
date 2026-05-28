"""WebSocket connection management via DynamoDB (for API Gateway WebSocket)."""
import time
import boto3
from app.config import settings


class WebSocketManager:
    """Manages WebSocket connections in DynamoDB for API Gateway WebSocket API."""

    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb", region_name=settings.aws_region)
        self.connections_table = self.dynamodb.Table(settings.dynamodb_auction_connections_table)

    def connect(self, auction_id: str, connection_id: str, member_id: str):
        """Register a WebSocket connection."""
        self.connections_table.put_item(Item={
            "auction_id": auction_id,
            "connection_id": connection_id,
            "member_id": member_id,
            "connected_at": int(time.time()),
            "ttl": int(time.time()) + (4 * 60 * 60),  # 4 hours
        })

    def disconnect(self, auction_id: str, connection_id: str):
        """Remove a WebSocket connection."""
        self.connections_table.delete_item(Key={
            "auction_id": auction_id,
            "connection_id": connection_id,
        })

    def get_connections(self, auction_id: str) -> list[dict]:
        """Get all active connections for an auction."""
        response = self.connections_table.query(
            KeyConditionExpression="auction_id = :aid",
            ExpressionAttributeValues={":aid": auction_id},
        )
        return response.get("Items", [])

    def broadcast(self, auction_id: str, message: dict):
        """Broadcast message to all connected clients via API Gateway."""
        if not settings.websocket_api_endpoint:
            return
        import json
        apigw = boto3.client(
            "apigatewaymanagementapi",
            endpoint_url=settings.websocket_api_endpoint,
            region_name=settings.aws_region,
        )
        connections = self.get_connections(auction_id)
        for conn in connections:
            try:
                apigw.post_to_connection(
                    ConnectionId=conn["connection_id"],
                    Data=json.dumps(message).encode(),
                )
            except Exception:
                # Connection stale, remove it
                self.disconnect(auction_id, conn["connection_id"])


ws_manager = WebSocketManager()
