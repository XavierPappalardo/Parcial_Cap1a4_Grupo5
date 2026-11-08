"""Rutas de monitoreo de salud: /health/live y /health/ready."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.modules.health import service

router = APIRouter(tags=["health"])


@router.get("/live", summary="Liveness probe")
async def live() -> dict[str, str]:
    """Verifica que el proceso del servidor esté activo sin tocar la base de datos."""
    return service.verificar_liveness()


@router.get("/ready", summary="Readiness probe")
async def ready(
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    """Verifica que la base de datos responda ejecutando SELECT 1."""
    try:
        return await service.verificar_readiness(session)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error de conexión con la base de datos",
        ) from exc
