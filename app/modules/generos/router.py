from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.generos import service
from app.modules.generos.schemas import GeneroCreate, GeneroRead

router = APIRouter(prefix="/generos", tags=["generos"])


@router.post("/", response_model=GeneroRead, status_code=201)
async def crear(data: GeneroCreate, session: AsyncSession = Depends(get_session)):
    return await service.crear(session, data)


@router.get("/", response_model=list[GeneroRead])
async def listar(session: AsyncSession = Depends(get_session)):
    return await service.listar(session)


@router.get("/{genero_id}/libros")
async def listar_libros(genero_id: int, session: AsyncSession = Depends(get_session)):
    libros = await service.listar_libros(session, genero_id)
    return [
        {
            "id": l.id,
            "isbn": l.isbn,
            "titulo": l.titulo,
            "precio": str(l.precio),
            "stock": l.stock,
            "editorial_id": l.editorial_id,
            "genero_id": l.genero_id,
        }
        for l in libros
    ]
