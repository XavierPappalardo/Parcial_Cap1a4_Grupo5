"""Módulo de conexión y gestión de sesiones asincrónicas con SQLAlchemy/SQLModel."""

from typing import AsyncGenerator
from fastapi import Request
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def crear_motor(database_url: str, echo: bool = False) -> AsyncEngine:
    """Crea y retorna un motor asincrónico para la base de datos."""
    return create_async_engine(
        database_url,
        echo=echo,
        future=True,
    )


def crear_fabrica_sesiones(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """Crea una fábrica de sesiones asincrónicas con expire_on_commit=False."""
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


async def get_session(
    request: Request,
) -> AsyncGenerator[AsyncSession, None]:
    """Dependencia para inyectar una AsyncSession por petición desde app.state."""
    session_factory: async_sessionmaker[AsyncSession] = (
        request.app.state.session_factory
    )
    async with session_factory() as session:
        yield session
