"""Verificaciones de integración base (tarea 1.1, 1.2)."""

import asyncio

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

# Asegura registro de modelos en metadata
import app.modules.autores.models  # noqa: F401
import app.modules.clientes.models  # noqa: F401
import app.modules.editoriales.models  # noqa: F401
import app.modules.generos.models  # noqa: F401
import app.modules.libros.models  # noqa: F401
import app.modules.ventas.models  # noqa: F401
from app.core.database import crear_fabrica_sesiones, crear_motor, get_session
from app.core.errors import MENSAJE_INTEGRIDAD, integrity_error_handler
from app.modules.editoriales.models import Editorial


def test_startup_registra_tablas_dominio_en_metadata():
    """1.1: metadata/app reconoce las 9 tablas de dominio tras importar modelos."""
    esperadas = {
        "editorial",
        "genero",
        "autor",
        "libro",
        "libro_autor",
        "cliente",
        "perfil_cliente",
        "venta",
        "renglon_venta",
    }
    assert esperadas.issubset(set(SQLModel.metadata.tables))


def test_integrity_handler_respuesta_limpia():
    """1.2: handler traduce IntegrityError a 409 sin detalles internos."""

    class DummyRequest:
        pass

    exc = IntegrityError("INSERT ...", {}, Exception("uq_cliente_email duplicate key"))
    resp = asyncio.run(integrity_error_handler(DummyRequest(), exc))
    assert resp.status_code == 409
    body = bytes(resp.body).decode("utf-8").lower()
    assert "uq_cliente" not in body
    assert "duplicate" not in body
    assert "insert" not in body
    assert "traceback" not in body
    assert "conflicto" in body


def test_integrity_error_409_end_to_end_sin_fuga(database_url_sqlite):
    """1.2: conflicto de unicidad vía HTTP devuelve 409 limpio (RN-12)."""
    import pytest

    pytest.importorskip("aiosqlite")
    probe_app = FastAPI()
    probe_app.add_exception_handler(IntegrityError, integrity_error_handler)
    engine = crear_motor(database_url_sqlite)
    probe_app.state.session_factory = crear_fabrica_sesiones(engine)

    async def init_db():
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    asyncio.run(init_db())

    @probe_app.post("/probe-editorial")
    async def probe(session: AsyncSession = Depends(get_session)):
        session.add(Editorial(nombre="Planeta", pais="AR"))
        await session.commit()
        result = await session.execute(select(Editorial))
        await session.refresh(result.scalars().first())
        return {"ok": True}

    with TestClient(probe_app) as client:
        r1 = client.post("/probe-editorial")
        assert r1.status_code == 200
        r2 = client.post("/probe-editorial")
    assert r2.status_code == 409
    cuerpo = r2.text.lower()
    assert "uq_editorial" not in cuerpo and "unique" not in cuerpo
    assert "traceback" not in cuerpo and "editorial.nombre" not in cuerpo
    asyncio.run(engine.dispose())

