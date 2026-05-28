"""Environment-based configuration for payment service."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "dev"
    database_url: str
    aws_region: str = "ap-south-1"
    s3_payment_proofs_bucket: str
    presigned_url_expiry: int = 3600
    notification_service_url: str = "http://notification-service:8000"

    class Config:
        env_file = ".env"


settings = Settings()
