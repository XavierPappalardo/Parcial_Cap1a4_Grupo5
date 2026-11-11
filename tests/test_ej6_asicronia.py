"""Tests para Ejercicio 6: Asincronía sin bloqueos (BackgroundTasks en POST /ventas/)."""

import inspect
import logging

import pytest
from fastapi import BackgroundTasks
from fastapi.testclient import TestClient

from app.main import app as main_app
from app.modules.ventas import router as ventas_router


# ---------------------------------------------------------------------------
# Task 2.1: BackgroundTasks parameter in crear handler
# ---------------------------------------------------------------------------


def test_crear_handler_tiene_background_tasks():
    """El handler crear de POST /ventas/ acepta background_tasks: BackgroundTasks."""
    sig = inspect.signature(ventas_router.crear)
    assert "background_tasks" in sig.parameters
    param = sig.parameters["background_tasks"]
    assert param.annotation is BackgroundTasks


# ---------------------------------------------------------------------------
# Task 2.2: enviar_aviso_comprobante exists with asyncio.sleep(0.5) + logging.info
# ---------------------------------------------------------------------------


def test_enviar_aviso_comprobante_existe():
    """Existe la función enviar_aviso_comprobante en el módulo de ventas router."""
    assert hasattr(ventas_router, "enviar_aviso_comprobante")
    assert inspect.iscoroutinefunction(ventas_router.enviar_aviso_comprobante)


def test_enviar_aviso_comprobante_usa_asyncio_sleep_y_log():
    """enviar_aviso_comprobante usa asyncio.sleep(0.5) y logging.info."""
    src = inspect.getsource(ventas_router.enviar_aviso_comprobante)
    assert "asyncio.sleep(0.5)" in src
    assert "logging.info" in src


@pytest.mark.asyncio
async def test_enviar_aviso_comprobante_registra_log(caplog):
    """Llamar a enviar_aviso_comprobante registra un mensaje en el log."""
    caplog.set_level(logging.INFO)
    await ventas_router.enviar_aviso_comprobante(venta_id=42)
    assert any("comprobante" in r.getMessage().lower() for r in caplog.records)


# ---------------------------------------------------------------------------
# Task 2.3: background_tasks.add_task scheduled after registering the sale
# ---------------------------------------------------------------------------


def test_crear_programa_aviso_comprobante_en_background():
    """El handler crear agenda enviar_aviso_comprobante con background_tasks.add_task."""
    src = inspect.getsource(ventas_router.crear)
    assert "background_tasks.add_task" in src
    assert "enviar_aviso_comprobante" in src


# ---------------------------------------------------------------------------
# Task 4.1: POST /ventas/ devuelve 201 inmediatamente (no bloquea por el aviso)
# ---------------------------------------------------------------------------


def _seed_venta(c):
    ed = c.post("/editoriales/", json={"nombre": "E1", "pais": "AR"}).json()
    au = c.post("/autores/", json={"nombre": "A1", "nacionalidad": "AR"}).json()
    cli = c.post("/clientes/", json={"nombre": "Ana", "email": "ana@example.com"}).json()
    lib = c.post(
        "/libros/",
        json={
            "isbn": "ISBN-001",
            "titulo": "Rayuela",
            "precio": "25000.00",
            "stock": 10,
            "editorial_id": ed["id"],
            "genero_id": None,
            "autores": [{"autor_id": au["id"], "rol": "autor", "orden": 1}],
        },
    ).json()
    return cli, lib


def _app_con_sqlite(database_url_sqlite):
    pytest.importorskip("aiosqlite")
    from sqlmodel import SQLModel

    from app.core import config
    from app.core.database import crear_fabrica_sesiones, crear_motor

    import app.modules.autores.models  # noqa: F401
    import app.modules.clientes.models  # noqa: F401
    import app.modules.editoriales.models  # noqa: F401
    import app.modules.generos.models  # noqa: F401
    import app.modules.libros.models  # noqa: F401
    import app.modules.ventas.models  # noqa: F401

    engine = crear_motor(database_url_sqlite)

    async def init():
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
            await conn.run_sync(SQLModel.metadata.create_all)

    import asyncio

    asyncio.run(init())
    main_app.state.engine = engine
    main_app.state.session_factory = crear_fabrica_sesiones(engine)
    return engine


def test_post_ventas_devuelve_201_inmediato(database_url_sqlite):
    """POST /ventas/ responde 201 sin esperar el aviso de comprobante."""
    engine = _app_con_sqlite(database_url_sqlite)
    try:
        with TestClient(main_app) as c:
            cli, lib = _seed_venta(c)
            r = c.post(
                "/ventas/",
                json={"cliente_id": cli["id"], "renglones": [{"libro_id": lib["id"], "cantidad": 1}]},
            )
            assert r.status_code == 201
            assert r.json()["id"]
    finally:
        import asyncio

        asyncio.run(engine.dispose())
        from app.core import config

        config.get_settings.cache_clear()


def test_post_ventas_ejecuta_aviso_despues_de_respuesta(database_url_sqlite, caplog):
    """El aviso de comprobante se ejecuta después de la respuesta HTTP (no bloquea)."""
    caplog.set_level(logging.INFO)
    engine = _app_con_sqlite(database_url_sqlite)
    try:
        with TestClient(main_app) as c:
            cli, lib = _seed_venta(c)
            r = c.post(
                "/ventas/",
                json={"cliente_id": cli["id"], "renglones": [{"libro_id": lib["id"], "cantidad": 1}]},
            )
            assert r.status_code == 201
        # Fuera del bloque TestClient las tareas en segundo plano ya se ejecutaron.
        assert any("comprobante" in rec.getMessage().lower() for rec in caplog.records)
    finally:
        import asyncio

        asyncio.run(engine.dispose())
        from app.core import config

        config.get_settings.cache_clear()
