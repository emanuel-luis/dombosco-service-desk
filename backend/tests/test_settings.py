import pytest
from pydantic import ValidationError

from dombosco_service_desk.config import AppSettings

KEY = "k" * 32


def make(monkeypatch, **env):
    for name in (
        "SECRET_KEY",
        "DEBUG",
        "ALLOWED_HOSTS",
        "CSRF_TRUSTED_ORIGINS",
        "CORS_ALLOWED_ORIGINS",
    ):
        monkeypatch.delenv(name, raising=False)
    for name, value in env.items():
        monkeypatch.setenv(name, value)
    return AppSettings(_env_file=None)


def test_missing_secret_key_is_a_validation_error(monkeypatch):
    with pytest.raises(ValidationError):
        make(monkeypatch)


def test_short_secret_key_is_a_validation_error(monkeypatch):
    with pytest.raises(ValidationError, match="at least 32 characters"):
        make(monkeypatch, SECRET_KEY="k" * 31)


def test_debug_defaults_to_false(monkeypatch):
    assert make(monkeypatch, SECRET_KEY=KEY).debug is False


def test_secret_key_is_not_leaked_in_repr(monkeypatch):
    assert "hunter2" not in repr(make(monkeypatch, SECRET_KEY="hunter2" * 5))


def test_list_defaults(monkeypatch):
    env = make(monkeypatch, SECRET_KEY=KEY)
    assert env.allowed_hosts == ["localhost", "127.0.0.1"]
    assert "http://localhost:3000" in env.cors_allowed_origins
    assert "http://localhost:3000" in env.csrf_trusted_origins


def test_comma_separated_lists_are_parsed(monkeypatch):
    env = make(
        monkeypatch,
        SECRET_KEY=KEY,
        ALLOWED_HOSTS="a.example.com, b.example.com,,",
        CORS_ALLOWED_ORIGINS="https://a.example.com",
    )
    assert env.allowed_hosts == ["a.example.com", "b.example.com"]
    assert env.cors_allowed_origins == ["https://a.example.com"]
