from sqlalchemy import bindparam, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.common import aplicar_patch, obtener_o_404
from app.modules.libros.models import Libro, LibroAutor
from app.modules.libros.schemas import LibroCreate, LibroUpdate


def _query_libro_detalle():
    return select(Libro).options(
        joinedload(Libro.editorial),
        joinedload(Libro.genero),
        selectinload(Libro.autorias).joinedload(LibroAutor.autor),
    )


async def crear(session: AsyncSession, datos: LibroCreate) -> Libro:
    # Ej 4: sin SELECT previo para verificar existencia de FKs; la DB valida.
    libro = Libro(
        isbn=datos.isbn,
        titulo=datos.titulo,
        precio=datos.precio,
        stock=datos.stock,
        editorial_id=datos.editorial_id,
        genero_id=datos.genero_id,
    )
    for a in datos.autores:
        libro.autorias.append(
            LibroAutor(autor_id=a.autor_id, rol=a.rol, orden=a.orden)
        )
    session.add(libro)
    await session.commit()
    # Recargar con relaciones para respuesta 201 completa
    result = await session.execute(_query_libro_detalle().where(Libro.id == libro.id))
    return result.unique().scalars().one()


async def listar(
    session: AsyncSession, limit: int, offset: int, titulo: str | None = None
) -> list[Libro]:
    stmt = _query_libro_detalle()
    if titulo:
        stmt = stmt.where(Libro.titulo.ilike(bindparam("titulo", f"%{titulo}%")))
    stmt = stmt.offset(offset).limit(limit)
    result = await session.execute(stmt)
    return list(result.unique().scalars().all())


async def obtener(session: AsyncSession, libro_id: int) -> Libro:
    result = await session.execute(_query_libro_detalle().where(Libro.id == libro_id))
    obj = result.unique().scalars().first()
    if obj is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return obj


async def actualizar(session: AsyncSession, libro_id: int, datos: LibroUpdate) -> Libro:
    obj = await session.get(Libro, libro_id)
    if obj is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Libro no encontrado")
    aplicar_patch(obj, datos)
    session.add(obj)
    await session.commit()
    return await obtener(session, libro_id)
