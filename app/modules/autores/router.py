from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.autores import service
from app.modules.autores.schemas import AutorCreate, AutorRead, AutorUpdate

router = APIRouter(prefix="/autores", tags=["autores"])


@router.post("/", response_model=AutorRead, status_code=201)
async def crear(data: AutorCreate, session: AsyncSession = Depends(get_session)):
    return await service.crear(session, data)


@router.get("/{autor_id}", response_model=AutorRead)
async def obtener(autor_id: int, session: AsyncSession = Depends(get_session)):
    return await service.obtener(session, autor_id)


@router.patch("/{autor_id}", response_model=AutorRead)
async def actualizar(
    autor_id: int, data: AutorUpdate, session: AsyncSession = Depends(get_session)
):
    return await service.actualizar(session, autor_id, data)


@router.get("/{autor_id}/libros")
async def listar_libros(autor_id: int, session: AsyncSession = Depends(get_session)):
    autorias = await service.listar_libros(session, autor_id)
    return [
        {
            "id": a.libro.id,
            "isbn": a.libro.isbn,
            "titulo": a.libro.titulo,
            "precio": str(a.libro.precio),
            "stock": a.libro.stock,
            "rol": a.rol,
            "orden": a.orden,
        }
        for a in autorias
    ]
