from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common import aplicar_patch, obtener_o_404
from app.modules.editoriales.models import Editorial
from app.modules.editoriales.schemas import EditorialCreate, EditorialUpdate
from app.modules.libros.models import Libro


async def crear(session: AsyncSession, datos: EditorialCreate) -> Editorial:
    obj = Editorial(**datos.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def listar(session: AsyncSession, limit: int, offset: int) -> list[Editorial]:
    result = await session.execute(select(Editorial).offset(offset).limit(limit))
    return list(result.scalars().all())


async def obtener(session: AsyncSession, editorial_id: int) -> Editorial:
    return await obtener_o_404(session, Editorial, editorial_id, "Editorial")


async def actualizar(session: AsyncSession, editorial_id: int, datos: EditorialUpdate) -> Editorial:
    obj = await obtener(session, editorial_id)
    aplicar_patch(obj, datos)
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def listar_libros(session: AsyncSession, editorial_id: int) -> list[Libro]:
    await obtener(session, editorial_id)
    result = await session.execute(select(Libro).where(Libro.editorial_id == editorial_id))
    return list(result.scalars().all())
