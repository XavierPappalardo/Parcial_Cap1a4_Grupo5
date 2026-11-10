from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.clientes import service
from app.modules.clientes.schemas import (
    ClienteCreate,
    ClienteRead,
    ClienteUpdate,
    PerfilClienteCreate,
    PerfilClienteRead,
)

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.post("/", response_model=ClienteRead, status_code=201)
async def crear(data: ClienteCreate, session: AsyncSession = Depends(get_session)):
    return await service.crear(session, data)


@router.get("/{cliente_id}", response_model=ClienteRead)
async def obtener(cliente_id: int, session: AsyncSession = Depends(get_session)):
    return await service.obtener(session, cliente_id)


@router.patch("/{cliente_id}", response_model=ClienteRead)
async def actualizar(
    cliente_id: int, data: ClienteUpdate, session: AsyncSession = Depends(get_session)
):
    return await service.actualizar(session, cliente_id, data)


@router.post("/{cliente_id}/perfil", response_model=PerfilClienteRead, status_code=201)
async def crear_perfil(
    cliente_id: int, data: PerfilClienteCreate, session: AsyncSession = Depends(get_session)
):
    return await service.crear_perfil(session, cliente_id, data)


@router.get("/{cliente_id}/ventas")
async def listar_ventas(cliente_id: int, session: AsyncSession = Depends(get_session)):
    ventas = await service.listar_ventas(session, cliente_id)
    return [
        {
            "id": v.id,
            "cliente_id": v.cliente_id,
            "fecha": v.fecha,
            "total": str(v.total),
            "renglones": [
                {
                    "id": r.id,
                    "venta_id": r.venta_id,
                    "libro_id": r.libro_id,
                    "cantidad": r.cantidad,
                    "precio_unitario": str(r.precio_unitario),
                }
                for r in v.renglones
            ],
        }
        for v in ventas
    ]
