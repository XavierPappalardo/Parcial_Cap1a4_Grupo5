"""Servicio de verificación de salud del sistema."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text


def verificar_liveness() -> dict[str, str]:
    """Retorna el estado de liveness del proceso web sin consultar recursos externos."""
    return {"estado": "vivo"}


async def verificar_readiness(session: AsyncSession) -> dict[str, str]:
    """Ejecuta SELECT 1 sobre PostgreSQL para verificar la conexión asincrónica."""
    result = await session.execute(text("SELECT 1"))
    val = result.scalar()
    if val != 1:
        raise RuntimeError("Respuesta inesperada al verificar la base de datos")
    return {"estado": "listo", "database": "conectada"}
