import inspect
import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.modules.health import service
from app.modules.health.router import live, ready, router


def test_verificar_liveness():
    resultado = service.verificar_liveness()
    assert resultado == {"estado": "vivo"}


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
