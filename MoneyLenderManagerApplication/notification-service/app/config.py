"""Environment-based configuration for notification service."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "dev"
    aws_region: str = "ap-south-1"
    sns_sms_sender_id: str = "MLMFund"
    sqs_notification_queue_url: str
    dynamodb_notification_logs_table: str
    dynamodb_device_tokens_table: str
    localization_bucket: str
    fcm_server_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
