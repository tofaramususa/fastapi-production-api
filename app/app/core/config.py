import secrets
import os
from typing import Any, Dict, List, Union, Annotated, Optional
from pathlib import Path

from pydantic import AnyHttpUrl, EmailStr, HttpUrl, field_validator, BeforeValidator
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    TOTP_SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 30
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24 * 30
    JWT_ALGO: str = "HS512"
    TOTP_ALGO: str = "SHA-1"
    SERVER_NAME: str
    # SERVER_HOST: AnyHttpUrl
    SERVER_BOT: str = "Symona"
    PRODUCT_PROMPT_GENERATION_URL: str
    PIPEDREAM_AUTH_KEY: str
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    # BACKEND_CORS_ORIGINS: Annotated[
    #     list[AnyHttpUrl] | str, BeforeValidator(parse_cors)
    # ] = []

    PROJECT_NAME: str
    DOMAIN_URL: str
    SENTRY_DSN: str
    GOOGLE_APPLICATION_CREDENTIALS: str | None
    MASTER_TOKEN: str
    PRODUCTION: bool = False
    # SENTRY_DSN: HttpUrl | None = None

    # @field_validator("SENTRY_DSN", mode="before")
    # def sentry_dsn_can_be_blank(cls, v: str) -> str | None:
    #     if isinstance(v, str) and len(v) == 0:
    #         return None
    #     return v

    # GENERAL SETTINGS

    MULTI_MAX: int = 20

    # COMPONENT SETTINGS
    MONGO_DATABASE: str
    MONGO_DATABASE_URI: str

    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: str | None = None
    EMAILS_TO_EMAIL: EmailStr | None = None

    @field_validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: str | None, info: ValidationInfo) -> str:
        if not v:
            return info.data["PROJECT_NAME"]
        return v

    EMAIL_TEST_USER: EmailStr = "test@example.com"
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str
    USERS_OPEN_REGISTRATION: bool = True

    # Redis settings
    UPSTASH_REDIS_REST_URL: Optional[str] = None
    UPSTASH_REDIS_REST_TOKEN: Optional[str] = None

    # Rate limit settings
    RATE_LIMIT_DEFAULT: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    RATE_LIMIT_ADMIN: int = 10000
    RATE_LIMIT_ADMIN_WINDOW: int = 60  # seconds

    # Product creation rate limit settings
    RATE_LIMIT_PRODUCT_CREATION_MAX: int = 1
    RATE_LIMIT_PRODUCT_CREATION_WINDOW: int = 7200  # 2 hours in seconds

settings = Settings()
