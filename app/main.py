"""Punto de entrada principal de la aplicación FastAPI y ciclo de vida."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from sqlmodel import SQLModel

from app.core.config import get_settings
from app.core.database import crear_fabrica_sesiones, crear_motor
from app.modules.health.router import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gestiona el ciclo de vida de la aplicación: motor, sesiones y create_all."""
    settings = get_settings()

    # 1. Crear motor asincrónico y fábrica de sesiones
    engine = crear_motor(settings.DATABASE_URL, echo=settings.SQL_ECHO)
    session_factory = crear_fabrica_sesiones(engine)

    # 2. Guardar en app.state para inyección en handlers
    app.state.engine = engine
    app.state.session_factory = session_factory

    # 3. Crear tablas en la base de datos si no existen.
    # Si la inicialización falla (p. ej. base inalcanzable), el motor igual
    # debe liberarse: no se dejan conexiones abiertas al abortar el arranque.
    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
    except BaseException:
        await engine.dispose()
        raise

    try:
        yield
    finally:
        # 4. Cerrar el pool de conexiones ordenadamente al apagar
        await engine.dispose()


app = FastAPI(
    title="Librería API",
    description="API para catálogo y ventas de librería con despliegue en VPS (Programación III UTN)",
    version="1.0.0",
    lifespan=lifespan,
)

# Registro de routers
app.include_router(health_router, prefix="/health")
