"""Manejo central de errores para respuestas limpias (RN-12)."""

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

MENSAJE_INTEGRIDAD = "Conflicto de integridad: el dato ya existe o la referencia no es válida."


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """Traduce errores de integridad a HTTP 409 sin exponer detalles internos."""
    # RN-12: nunca incluir texto interno de base de datos, constraints o trazas.
    return JSONResponse(
        status_code=409,
        content={"detail": MENSAJE_INTEGRIDAD},
    )
