"""Localization service — fetches Tamil/English strings from S3 (US-027)."""
import json
from functools import lru_cache
import boto3
from app.config import settings


class LocalizationService:
    def __init__(self):
        self.s3 = boto3.client("s3", region_name=settings.aws_region)
        self.bucket = settings.localization_bucket

    @lru_cache(maxsize=4)
    def get_bundle(self, language_code: str) -> dict:
        """Fetch language bundle from S3."""
        key = f"localization/{language_code}.json"
        response = self.s3.get_object(Bucket=self.bucket, Key=key)
        return json.loads(response["Body"].read())

    def translate(self, key: str, language_code: str, **params) -> str:
        """Get translated string with parameter substitution."""
        bundle = self.get_bundle(language_code)
        template = bundle.get(key, key)
        return template.format(**params) if params else template

    def clear_cache(self):
        """Clear cached bundles (call after S3 update)."""
        self.get_bundle.cache_clear()


localization_service = LocalizationService()
