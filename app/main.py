"""Punto de entrada principal de la aplicación FastAPI y ciclo de vida."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel

from app.core.config import get_settings
from app.core.database import crear_fabrica_sesiones, crear_motor
from app.core.errors import integrity_error_handler
from app.modules.autores.router import router as autores_router
from app.modules.editoriales.router import router as editoriales_router
from app.modules.generos.router import router as generos_router
from app.modules.health.router import router as health_router
from app.modules.clientes.router import router as clientes_router
from app.modules.libros.router import router as libros_router
from app.modules.ventas.router import router as ventas_router

# Registrar TODOS los modelos de tabla en SQLModel.metadata antes de que el
# lifespan ejecute metadata.create_all: SQLModel registra la clase en la
# metadata cuando su módulo se importa. Sin estas importaciones, el efecto
# del arranque generaría un esquema vacío en la base de datos.
from app.modules.autores import models as autores_models  # noqa: F401
from app.modules.clientes import models as clientes_models  # noqa: F401
from app.modules.editoriales import models as editoriales_models  # noqa: F401
from app.modules.generos import models as generos_models  # noqa: F401
from app.modules.libros import models as libros_models  # noqa: F401
from app.modules.ventas import models as ventas_models  # noqa: F401


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

app.add_exception_handler(IntegrityError, integrity_error_handler)

# Registro de routers
app.include_router(health_router, prefix="/health")
app.include_router(editoriales_router)
app.include_router(generos_router)
app.include_router(autores_router)
app.include_router(libros_router)
app.include_router(clientes_router)
app.include_router(ventas_router)
