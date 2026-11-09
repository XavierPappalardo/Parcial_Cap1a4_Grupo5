"""Configuración compartida de las pruebas automatizadas."""

import pytest

from app.core import config


@pytest.fixture
def database_url_sqlite(tmp_path, monkeypatch):
    """DATABASE_URL sobre SQLite (aiosqlite) para pruebas sin PostgreSQL local.

    Vulnear la caché de `get_settings` es obligatorio: es lru_cache y, si no se
    limpia, los tests heredan la configuración de un test anterior.
    """
    url = f"sqlite+aiosqlite:///{(tmp_path / 'libreria_test.db').as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.delenv("SQL_ECHO", raising=False)
    config.get_settings.cache_clear()
    yield url
    config.get_settings.cache_clear()
