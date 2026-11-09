import inspect

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import app
from app.modules.health import service
from app.modules.health.router import live, ready, router


def test_verificar_liveness():
    resultado = service.verificar_liveness()
    assert resultado == {"estado": "vivo"}


@pytest.mark.asyncio
async def test_verificar_readiness_ejecuta_select_1(database_url_sqlite):
    """El servicio verifica la base de datos con SELECT 1 (sin PostgreSQL local: sqlite)."""
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

    engine = create_async_engine(database_url_sqlite)
    fabrica = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with fabrica() as session:
        resultado = await service.verificar_readiness(session)
    assert resultado == {"estado": "listo", "database": "conectada"}
    await engine.dispose()


@pytest.mark.asyncio
async def test_router_live_endpoint():
    resultado = await live()
    assert resultado == {"estado": "vivo"}


def test_router_has_routes():
    routes = [route.path for route in router.routes]
    assert "/live" in routes
    assert "/ready" in routes


def test_ready_is_async_function():
    assert inspect.iscoroutinefunction(ready)
    assert inspect.iscoroutinefunction(service.verificar_readiness)


# ---------------------------------------------------------------- HTTP real ---


def test_http_live_200_sin_base_de_datos(database_url_sqlite):
    """GET /health/live responde 200 sin necesitar base de datos (proceso vivo)."""
    with TestClient(app) as client:
        response = client.get("/health/live")
        assert response.status_code == 200
        assert response.json() == {"estado": "vivo"}


def test_http_ready_200_con_base_disponible(database_url_sqlite):
    """GET /health/ready responde 200 cuando SELECT 1 se ejecuta con éxito."""
    with TestClient(app) as client:
        response = client.get("/health/ready")
        assert response.status_code == 200
        assert response.json() == {"estado": "listo", "database": "conectada"}


def test_http_ready_500_inalcanzable_sin_trazas(monkeypatch):
    """Si la base no responde: 500, mensaje propio y sin detalles internos."""
    # App de sondeo: mismo router, pero sin lifespan (create_all) para
    # atacar un motor apuntando a una base inalcanzable.
    from app.core.database import crear_fabrica_sesiones, crear_motor
    from app.modules.health.router import router as health_router

    app_sondeo = FastAPI()
    app_sondeo.include_router(health_router, prefix="/health")
    motor = crear_motor(
        "postgresql+asyncpg://usuario:secreto@127.0.0.1:1/no_existe"
    )
    app_sondeo.state.session_factory = crear_fabrica_sesiones(motor)

    with TestClient(app_sondeo) as client:
        response = client.get("/health/ready")

    assert response.status_code == 500
    assert response.json() == {"detail": "Error de conexión con la base de datos"}

    cuerpo = response.text.lower()
    # RN-12: nada de trazas, sintaxis SQL ni detalles internos del driver.
    assert "traceback" not in cuerpo
    assert "select" not in cuerpo
    assert "asyncpg" not in cuerpo
    assert "secreto" not in cuerpo
    assert "ultima_peticion" not in cuerpo
