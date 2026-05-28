"""Environment-based configuration for auction service."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "dev"
    database_url: str
    aws_region: str = "ap-south-1"
    dynamodb_auction_connections_table: str
    dynamodb_auction_state_table: str
    websocket_api_endpoint: str = ""
    group_service_url: str = "http://group-service:8000"
    payment_service_url: str = "http://payment-service:8000"
    notification_service_url: str = "http://notification-service:8000"

    class Config:
        env_file = ".env"


settings = Settings()
