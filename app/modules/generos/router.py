from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.generos import service
from app.modules.generos.schemas import GeneroCreate, GeneroRead
from app.modules.libros.schemas import LibroRead

router = APIRouter(prefix="/generos", tags=["generos"])


@router.post("/", response_model=GeneroRead, status_code=201)
async def crear(data: GeneroCreate, session: AsyncSession = Depends(get_session)):
    return await service.crear(session, data)


@router.get("/", response_model=list[GeneroRead])
async def listar(session: AsyncSession = Depends(get_session)):
    return await service.listar(session)


@router.get("/{genero_id}/libros", response_model=list[LibroRead])
async def listar_libros(genero_id: int, session: AsyncSession = Depends(get_session)):
    return await service.listar_libros(session, genero_id)
