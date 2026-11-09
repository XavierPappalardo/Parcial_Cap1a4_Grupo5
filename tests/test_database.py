import inspect

import pytest
from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)

from app.core.database import crear_fabrica_sesiones, crear_motor, get_session


def test_crear_motor_retorna_async_engine():
    engine = crear_motor(
        "postgresql+asyncpg://postgres:postgres@localhost:5432/libreria",
        echo=False,
    )
    assert isinstance(engine, AsyncEngine)
    assert engine.url.drivername == "postgresql+asyncpg"


def test_crear_fabrica_sesiones_configuracion():
    engine = crear_motor(
        "postgresql+asyncpg://postgres:postgres@localhost:5432/libreria",
        echo=False,
    )
    session_factory = crear_fabrica_sesiones(engine)
    assert isinstance(session_factory, async_sessionmaker)
    assert session_factory.kw.get("expire_on_commit") is False
    assert session_factory.class_ is AsyncSession


def test_get_session_es_generador_asincronico():
    assert inspect.isasyncgenfunction(get_session)


@pytest.mark.asyncio
async def test_get_session_una_sesion_por_peticion(database_url_sqlite):
    """get_session entrega una sola AsyncSession por petición y una nueva en la siguiente."""
    app = FastAPI()

    # Sin lifespan: la fábrica se dispone directamente en app.state como en producción.
    engine = crear_motor(database_url_sqlite)
    app.state.session_factory = crear_fabrica_sesiones(engine)

    capturadas: list[tuple[AsyncSession, AsyncSession]] = []

    @app.get("/eco")
    async def eco(
        sesion_a: AsyncSession = Depends(get_session),
        sesion_b: AsyncSession = Depends(get_session),
    ) -> dict[str, bool]:
        capturadas.append((sesion_a, sesion_b))
        return {"ok": True}

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test"
    ) as cliente:
        r1 = await cliente.get("/eco")
        r2 = await cliente.get("/eco")

    # El endpoint se resolvió dos veces con la dependencia inyectada.
    assert r1.status_code == 200 and r2.status_code == 200

    # Dentro de UNA misma petición: una única instancia compartida.
    primer_peticion_a, primer_peticion_b = capturadas[0]
    assert primer_peticion_a is primer_peticion_b

    # Entre peticiones distintas: la sesión NO se comparte.
    segunda_peticion = capturadas[1][0]
    assert segunda_peticion is not primer_peticion_a

    # Cierre garantizado: get_session trabaja con `async with session_factory()`,
    # la sesión no puede seguir activa para transacciones nuevas tras la petición.
    assert primer_peticion_a.in_transaction() is False
    assert segunda_peticion.in_transaction() is False

    await engine.dispose()
