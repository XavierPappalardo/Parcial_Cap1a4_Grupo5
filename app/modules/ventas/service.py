from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.modules.clientes.models import Cliente
from app.modules.libros.models import Libro
from app.modules.ventas.models import RenglonVenta, Venta
from app.modules.ventas.schemas import VentaCreate


def _query_venta_detalle():
    return select(Venta).options(
        joinedload(Venta.cliente).joinedload(Cliente.perfil),
        selectinload(Venta.renglones).joinedload(RenglonVenta.libro),
    )


async def crear(session: AsyncSession, datos: VentaCreate) -> Venta:
    # RN-05 ya validado por schema (422). Obtener precios (RN-06).
    ids_libros = [r.libro_id for r in datos.renglones]
    result = await session.execute(select(Libro).where(Libro.id.in_(ids_libros)))
    libros = {l.id: l for l in result.scalars().all()}
    # Si falta algún libro, la FK de renglon_venta.libro_id fallará al persistir -> 409.
    # Pero para copiar precio necesitamos el libro; si no está, no podemos calcular RN-06/07.
    # Intentamos construir con lo disponible y dejamos que DB valide cliente/libro inexistente.
    venta = Venta(cliente_id=datos.cliente_id, total=Decimal("0.00"))
    total = Decimal("0.00")
    for r in datos.renglones:
        libro = libros.get(r.libro_id)
        precio = libro.precio if libro else Decimal("0.01")
        renglon = RenglonVenta(
            libro_id=r.libro_id,
            cantidad=r.cantidad,
            precio_unitario=precio,
        )
        venta.renglones.append(renglon)
        total += Decimal(r.cantidad) * precio
    venta.total = total
    session.add(venta)
    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    result = await session.execute(_query_venta_detalle().where(Venta.id == venta.id))
    return result.unique().scalars().one()


async def listar(session: AsyncSession) -> list[Venta]:
    result = await session.execute(_query_venta_detalle())
    return list(result.unique().scalars().all())


async def obtener(session: AsyncSession, venta_id: int) -> Venta:
    result = await session.execute(_query_venta_detalle().where(Venta.id == venta_id))
    obj = result.unique().scalars().first()
    if obj is None:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return obj
