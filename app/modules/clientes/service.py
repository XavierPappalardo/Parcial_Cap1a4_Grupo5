from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.common import aplicar_patch, obtener_o_404
from app.modules.clientes.models import Cliente, PerfilCliente
from app.modules.clientes.schemas import ClienteCreate, ClienteUpdate, PerfilClienteCreate
from app.modules.ventas.models import Venta


async def crear(session: AsyncSession, datos: ClienteCreate) -> Cliente:
    obj = Cliente(**datos.model_dump())
    session.add(obj)
    await session.commit()
    return await obtener(session, obj.id)


async def obtener(session: AsyncSession, cliente_id: int) -> Cliente:
    stmt = select(Cliente).where(Cliente.id == cliente_id).options(joinedload(Cliente.perfil))
    result = await session.execute(stmt)
    obj = result.unique().scalars().first()
    if obj is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return obj


async def actualizar(session: AsyncSession, cliente_id: int, datos: ClienteUpdate) -> Cliente:
    obj = await session.get(Cliente, cliente_id)
    if obj is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    aplicar_patch(obj, datos)
    session.add(obj)
    await session.commit()
    return await obtener(session, cliente_id)


async def crear_perfil(session: AsyncSession, cliente_id: int, datos: PerfilClienteCreate) -> PerfilCliente:
    await obtener(session, cliente_id)
    # No if-exists pattern for "already has profile"? RN-09 says DB UNIQUE on cliente_id rejects second;
    # inserting will trigger IntegrityError -> 409 via handler. That's fine (and aligns with "let DB validate").
    perfil = PerfilCliente(cliente_id=cliente_id, **datos.model_dump())
    session.add(perfil)
    await session.commit()
    await session.refresh(perfil)
    return perfil


async def listar_ventas(session: AsyncSession, cliente_id: int):
    await obtener(session, cliente_id)
    stmt = (
        select(Venta)
        .where(Venta.cliente_id == cliente_id)
        .options(selectinload(Venta.renglones))
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())
