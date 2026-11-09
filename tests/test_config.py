import pytest
from pydantic import ValidationError

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


def test_settings_falla_de_manera_controlada_sin_database_url(monkeypatch):
    """Sin DATABASE_URL (variable de entorno ni .env) la configuración no puede crearse.

    La aplicación debe fallar de manera controlada: no arrancar con una URL de
    credenciales embebidas ni asumir valores por defecto del entorno.
    """
    monkeypatch.delenv("DATABASE_URL", raising=False)
    # _env_file=None: ignora cualquier .env local del directorio de trabajo.
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_settings_sin_env_file_lee_variables_de_entorno(database_url_sqlite):
    """Con DATABASE_URL en el entorno (ignorando .env) la configuración carga."""
    settings = Settings(_env_file=None)
    assert settings.DATABASE_URL == database_url_sqlite
