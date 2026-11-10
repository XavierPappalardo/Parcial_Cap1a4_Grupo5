from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common import paginacion
from app.core.database import get_session
from app.modules.libros import service
from app.modules.libros.schemas import LibroCreate, LibroRead, LibroUpdate

router = APIRouter(prefix="/libros", tags=["libros"])


@router.post("/", response_model=LibroRead, status_code=201)
async def crear(data: LibroCreate, session: AsyncSession = Depends(get_session)):
    return await service.crear(session, data)


@router.get("/", response_model=list[LibroRead])
async def listar(
    titulo: str | None = Query(default=None),
    genero_id: int | None = Query(default=None),
    p=Depends(paginacion),
    session: AsyncSession = Depends(get_session),
):
    return await service.listar(
        session, p["limit"], p["offset"], titulo, genero_id
    )


@router.get("/{libro_id}", response_model=LibroRead)
async def obtener(libro_id: int, session: AsyncSession = Depends(get_session)):
    return await service.obtener(session, libro_id)


@router.patch("/{libro_id}", response_model=LibroRead)
async def actualizar(
    libro_id: int, data: LibroUpdate, session: AsyncSession = Depends(get_session)
):
    return await service.actualizar(session, libro_id, data)
