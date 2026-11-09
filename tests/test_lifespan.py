"""Pruebas reales del ciclo de vida de la aplicación (lifespan).

Se verifica el comportamiento, no solo la existencia de la función:
- estado guardado en app.state (motor y fábrica),
- create_all ejecutado durante el arranque,
- cierre del motor al apagar,
- cierre del motor aunque la inicialización falle.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.database import crear_fabrica_sesiones, crear_motor
from app.main import app, lifespan


def test_main_app_instance():
    assert isinstance(app, FastAPI)
    assert app.title == "Librería API"


def test_main_app_has_health_routes():
    openapi_schema = app.openapi()
    paths = openapi_schema.get("paths", {})
    assert "/health/live" in paths
    assert "/health/ready" in paths


@pytest.mark.asyncio
async def test_lifespan_inicializa_estado_y_cierra_motor(database_url_sqlite, monkeypatch):
    """Recorrido completo del lifespan con base de datos real (sqlite)."""
    motor_real = crear_motor(database_url_sqlite)

    class MotorEspia:
        """Delegante de AsyncEngine que registra las llamadas a dispose."""

        def __init__(self, real) -> None:
            self._real = real
            self.dispose_llamadas: list[bool] = []

        def begin(self):
            return self._real.begin()

        async def dispose(self) -> None:
            self.dispose_llamadas.append(True)
            await self._real.dispose()

    motor_espia = MotorEspia(motor_real)
    monkeypatch.setattr(
        "app.main.crear_motor", lambda url, echo=False: motor_espia
    )

    destino = FastAPI()

    async with lifespan(destino):
        # Durante la vida de la app: los recursos quedaron en app.state.
        assert destino.state.engine is motor_espia
        assert destino.state.session_factory.kw.get("expire_on_commit") is False

    # Al finalizar: el motor fue liberado exactamente una vez.
    assert motor_espia.dispose_llamadas == [True]


def test_lifespan_mapeo_http_completo(database_url_sqlite):
    """TestClient real: el lifespan corre, la app vive y health responde."""
    with TestClient(app) as client:
        assert isinstance(app.state.engine, object)
        assert app.state.session_factory.kw.get("expire_on_commit") is False
        response = client.get("/health/live")
        assert response.status_code == 200
    # Tras cerrar el cliente el lifespan terminó sin excepciones.


class MotorQueFalla:
    """Doble del motor cuya inicialización (begin) falla.

    Reproduce una base de datos inalcanzable: el create_all nunca concluye.
    """

    def __init__(self) -> None:
        self.dispose_llamadas: list[bool] = []

    def begin(self):
        raise RuntimeError("DB inalcanzable al crear tablas")

    async def dispose(self) -> None:
        self.dispose_llamadas.append(True)


@pytest.mark.asyncio
async def test_lifespan_dispone_motor_si_la_inicializacion_falla(
    database_url_sqlite, monkeypatch
):
    """Si create_all falla en el arranque, el motor se libera y el error se propaga."""
    motor = MotorQueFalla()
    monkeypatch.setattr("app.main.crear_motor", lambda url, echo=False: motor)
    monkeypatch.setattr("app.main.crear_fabrica_sesiones", crear_fabrica_sesiones)

    destino = FastAPI()
    with pytest.raises(RuntimeError, match="DB inalcanzable"):
        async with lifespan(destino):
            pytest.fail("No debe alcanzarse el yield si la inicialización falla")

    assert motor.dispose_llamadas == [True]
    # El motor llegó a quedar registrado en app.state antes del fallo.
    assert destino.state.engine is motor
