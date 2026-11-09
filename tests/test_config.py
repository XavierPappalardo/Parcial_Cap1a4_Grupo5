import pytest
from app.core.config import Settings


def test_settings_default_values():
    settings = Settings(
        DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/libreria_test"
    )
    assert settings.DATABASE_URL == "postgresql+asyncpg://postgres:postgres@localhost:5432/libreria_test"
    assert settings.SQL_ECHO is False
    assert settings.PORT == 8000


def test_settings_normalizes_postgresql_scheme():
    # Si viene con postgresql:// debe normalizarse a postgresql+asyncpg://
    settings = Settings(
        DATABASE_URL="postgresql://user:pass@localhost:5432/libreria"
    )
    assert str(settings.DATABASE_URL).startswith("postgresql+asyncpg://")


def test_settings_preserves_asyncpg_scheme():
    settings = Settings(
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/libreria"
    )
    assert str(settings.DATABASE_URL).startswith("postgresql+asyncpg://")


def test_settings_sql_echo_configurable():
    settings = Settings(
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/libreria",
        SQL_ECHO=True,
    )
    assert settings.SQL_ECHO is True
