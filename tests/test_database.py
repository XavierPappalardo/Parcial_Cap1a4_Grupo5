import inspect
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, AsyncSession
from app.core.database import crear_motor, crear_fabrica_sesiones, get_session


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
