"""Typed application settings, read once from the environment (and an optional `.env`)."""

from pathlib import Path
from typing import Annotated

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
CommaList = Annotated[list[str], NoDecode]


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore", env_ignore_empty=True)

    secret_key: SecretStr
    debug: bool = False

    allowed_hosts: CommaList = ["localhost", "127.0.0.1"]
    csrf_trusted_origins: CommaList = ["http://localhost:3000", "http://127.0.0.1:3000"]
    cors_allowed_origins: CommaList = ["http://localhost:3000", "http://127.0.0.1:3000"]

    database_url: str = "sqlite:///db.sqlite3"

    frontend_url: str = "http://localhost:3000"
    login_url: str | None = None

    email_backend: str = "django.core.mail.backends.console.EmailBackend"
    email_host: str = "smtp.gmail.com"
    email_port: int = 587
    email_use_tls: bool = True
    email_host_user: str | None = None
    email_host_password: SecretStr | None = None

    account_email_verification: str = "mandatory"
    dom_bosco_email_domain: str | None = None

    google_oauth_client_id: str | None = None
    google_oauth_client_secret: SecretStr | None = None
    google_oauth_callback_url: str | None = None

    @field_validator("allowed_hosts", "csrf_trusted_origins", "cors_allowed_origins", mode="before")
    @classmethod
    def _split_commas(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value
