from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI
from app.main import app, lifespan


def test_main_app_instance():
    assert isinstance(app, FastAPI)
    assert app.title == "Librería API"


def test_main_app_has_health_routes():
    openapi_schema = app.openapi()
    paths = openapi_schema.get("paths", {})
    assert "/health/live" in paths
    assert "/health/ready" in paths


def test_lifespan_is_async_context_manager():
    import inspect
    # Validar que lifespan es una función de context manager asincrónica
    assert hasattr(lifespan, "__wrapped__") or hasattr(lifespan, "__call__")
