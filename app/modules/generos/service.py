from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common import obtener_o_404
from app.modules.generos.models import Genero
from app.modules.generos.schemas import GeneroCreate
from app.modules.libros.models import Libro


async def crear(session: AsyncSession, datos: GeneroCreate) -> Genero:
    obj = Genero(**datos.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def listar(session: AsyncSession) -> list[Genero]:
    result = await session.execute(select(Genero))
    return list(result.scalars().all())


async def obtener(session: AsyncSession, genero_id: int) -> Genero:
    return await obtener_o_404(session, Genero, genero_id, "Género")


async def listar_libros(session: AsyncSession, genero_id: int) -> list[Libro]:
    await obtener(session, genero_id)
    result = await session.execute(select(Libro).where(Libro.genero_id == genero_id))
    return list(result.scalars().all())
