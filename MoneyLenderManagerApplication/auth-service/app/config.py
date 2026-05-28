"""Environment-based configuration. No hardcoded values."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "dev"
    database_url: str
    aws_region: str = "ap-south-1"
    cognito_user_pool_id: str
    cognito_client_id: str
    cognito_client_secret: str = ""
    dynamodb_sessions_table: str
    jwt_secret_key: str

    class Config:
        env_file = ".env"


settings = Settings()
