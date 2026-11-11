import asyncio
import logging

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.ventas import service
from app.modules.ventas.schemas import VentaCreate, venta_a_read

router = APIRouter(prefix="/ventas", tags=["ventas"])


async def enviar_aviso_comprobante(venta_id: int):
    """Simula el envío del aviso de comprobante en segundo plano sin bloquear."""
    await asyncio.sleep(0.5)
    logging.info("Aviso de comprobante enviado para la venta %s", venta_id)


@router.post("/", status_code=201)
async def crear(
    data: VentaCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    venta = await service.crear(session, data)
    background_tasks.add_task(enviar_aviso_comprobante, venta.id)
    return venta_a_read(venta)


@router.get("/")
async def listar(session: AsyncSession = Depends(get_session)):
    ventas = await service.listar(session)
    return [venta_a_read(v) for v in ventas]


@router.get("/{venta_id}")
async def obtener(venta_id: int, session: AsyncSession = Depends(get_session)):
    venta = await service.obtener(session, venta_id)
    return venta_a_read(venta)
