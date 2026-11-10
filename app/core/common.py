"""Utilidades compartidas: paginación (RN-10) y helpers de actualización."""

from typing import Any

from fastapi import HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession


async def paginacion(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> dict[str, int]:
    """Parámetros de paginación estándar (RN-10)."""
    return {"limit": limit, "offset": offset}


def aplicar_patch(modelo: Any, datos: BaseModel) -> Any:
    """Aplica solo los campos enviados (exclude_unset) sobre un modelo."""
    valores = datos.model_dump(exclude_unset=True)
    for campo, valor in valores.items():
        setattr(modelo, campo, valor)
    return modelo


async def obtener_o_404(session: AsyncSession, model: type, obj_id: int, nombre: str = "Recurso"):
    obj = await session.get(model, obj_id)
    if obj is None:
        raise HTTPException(status_code=404, detail=f"{nombre} no encontrado")
    return obj
