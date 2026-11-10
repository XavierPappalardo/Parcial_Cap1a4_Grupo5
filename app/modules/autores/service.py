from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.common import aplicar_patch, obtener_o_404
from app.modules.autores.models import Autor
from app.modules.autores.schemas import AutorCreate, AutorUpdate
from app.modules.libros.models import LibroAutor


async def crear(session: AsyncSession, datos: AutorCreate) -> Autor:
    obj = Autor(**datos.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def obtener(session: AsyncSession, autor_id: int) -> Autor:
    return await obtener_o_404(session, Autor, autor_id, "Autor")


async def actualizar(session: AsyncSession, autor_id: int, datos: AutorUpdate) -> Autor:
    obj = await obtener(session, autor_id)
    aplicar_patch(obj, datos)
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def listar_libros(session: AsyncSession, autor_id: int):
    await obtener(session, autor_id)
    stmt = (
        select(LibroAutor)
        .where(LibroAutor.autor_id == autor_id)
        .options(selectinload(LibroAutor.libro))
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())
