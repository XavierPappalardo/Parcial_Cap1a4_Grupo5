from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.modules.clientes.models import Cliente
from app.modules.libros.models import Libro
from app.modules.ventas.models import RenglonVenta, Venta
from app.modules.ventas.schemas import VentaCreate

# Precio válido usado solo cuando el libro referenciado no existe: permite
# construir el renglón y delegar el rechazo a la FK de la base (409), sin
# sustituir la integridad referencial por un "if exists" previo.
PRECIO_SENTINELA = Decimal("0.01")


def _query_venta_detalle():
    return select(Venta).options(
        joinedload(Venta.cliente).joinedload(Cliente.perfil),
        selectinload(Venta.renglones).joinedload(RenglonVenta.libro),
    )


async def crear(session: AsyncSession, datos: VentaCreate) -> Venta:
    # RN-05 ya validado por el schema (422). Una sola consulta para copiar los
    # precios actuales de todos los libros (RN-06), sin N+1.
    ids_libros = [r.libro_id for r in datos.renglones]
    result = await session.execute(select(Libro).where(Libro.id.in_(ids_libros)))
    libros = {libro.id: libro for libro in result.scalars().all()}

    venta = Venta(cliente_id=datos.cliente_id, total=Decimal("0.00"))
    total = Decimal("0.00")
    for renglon_in in datos.renglones:
        libro = libros.get(renglon_in.libro_id)
        # RN-06: el precio unitario se copia del libro, nunca lo envía el cliente.
        precio = libro.precio if libro else PRECIO_SENTINELA
        venta.renglones.append(
            RenglonVenta(
                libro_id=renglon_in.libro_id,
                cantidad=renglon_in.cantidad,
                precio_unitario=precio,
            )
        )
        total += Decimal(renglon_in.cantidad) * precio

    # RN-07: el total lo calcula el servidor a partir de los renglones.
    venta.total = total
    session.add(venta)
    try:
        # Venta + renglones se confirman en una única transacción (RN-04).
        # Si cliente o libro no existen, la FK lanza IntegrityError -> 409.
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    result = await session.execute(_query_venta_detalle().where(Venta.id == venta.id))
    return result.unique().scalars().one()


async def listar(session: AsyncSession, limit: int = 20, offset: int = 0) -> list[Venta]:
    stmt = _query_venta_detalle().order_by(Venta.id).offset(offset).limit(limit)
    result = await session.execute(stmt)
    return list(result.unique().scalars().all())


async def obtener(session: AsyncSession, venta_id: int) -> Venta:
    result = await session.execute(_query_venta_detalle().where(Venta.id == venta_id))
    obj = result.unique().scalars().first()
    if obj is None:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return obj
