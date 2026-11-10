from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.ventas import service
from app.modules.ventas.schemas import VentaCreate, venta_a_read

router = APIRouter(prefix="/ventas", tags=["ventas"])


@router.post("/", status_code=201)
async def crear(data: VentaCreate, session: AsyncSession = Depends(get_session)):
    venta = await service.crear(session, data)
    return venta_a_read(venta)


@router.get("/")
async def listar(session: AsyncSession = Depends(get_session)):
    ventas = await service.listar(session)
    return [venta_a_read(v) for v in ventas]


@router.get("/{venta_id}")
async def obtener(venta_id: int, session: AsyncSession = Depends(get_session)):
    venta = await service.obtener(session, venta_id)
    return venta_a_read(venta)
