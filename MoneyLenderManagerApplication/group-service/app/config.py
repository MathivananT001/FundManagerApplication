"""Environment-based configuration for group service."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "dev"
    database_url: str
    aws_region: str = "ap-south-1"
    s3_archives_bucket: str
    notification_service_url: str = "http://notification-service:8000"

    class Config:
        env_file = ".env"


settings = Settings()
