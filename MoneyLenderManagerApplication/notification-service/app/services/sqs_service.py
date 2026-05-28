"""SQS consumer for async notification dispatch."""
import json
import boto3
from app.config import settings
from app.services.sns_service import sns_service


class SQSConsumer:
    def __init__(self):
        self.client = boto3.client("sqs", region_name=settings.aws_region)
        self.queue_url = settings.sqs_notification_queue_url

    def send_to_queue(self, notification_type: str, payload: dict):
        """Enqueue a notification for async processing."""
        self.client.send_message(
            QueueUrl=self.queue_url,
            MessageBody=json.dumps({"type": notification_type, "payload": payload}),
        )

    def process_messages(self, max_messages: int = 10):
        """Poll and process messages from the queue."""
        response = self.client.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=max_messages,
            WaitTimeSeconds=5,
        )
        for msg in response.get("Messages", []):
            body = json.loads(msg["Body"])
            self._handle_message(body)
            self.client.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=msg["ReceiptHandle"],
            )

    def _handle_message(self, body: dict):
        """Route message to appropriate handler."""
        msg_type = body.get("type")
        payload = body.get("payload", {})

        if msg_type == "sms":
            sns_service.send_sms(payload["phone_number"], payload["message"])
        elif msg_type == "push":
            sns_service.send_push(payload["device_token"], payload["title"], payload["body"], payload.get("data"))
        elif msg_type == "bulk_sms":
            sns_service.send_bulk_sms(payload["phone_numbers"], payload["message"])


sqs_consumer = SQSConsumer()
