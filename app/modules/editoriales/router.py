from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common import paginacion
from app.core.database import get_session
from app.modules.editoriales import service
from app.modules.editoriales.schemas import EditorialCreate, EditorialRead, EditorialUpdate

router = APIRouter(prefix="/editoriales", tags=["editoriales"])


@router.post("/", response_model=EditorialRead, status_code=201)
async def crear(data: EditorialCreate, session: AsyncSession = Depends(get_session)):
    return await service.crear(session, data)


@router.get("/", response_model=list[EditorialRead])
async def listar(p=Depends(paginacion), session: AsyncSession = Depends(get_session)):
    return await service.listar(session, p["limit"], p["offset"])


@router.get("/{editorial_id}", response_model=EditorialRead)
async def obtener(editorial_id: int, session: AsyncSession = Depends(get_session)):
    return await service.obtener(session, editorial_id)


@router.patch("/{editorial_id}", response_model=EditorialRead)
async def actualizar(
    editorial_id: int, data: EditorialUpdate, session: AsyncSession = Depends(get_session)
):
    return await service.actualizar(session, editorial_id, data)


@router.get("/{editorial_id}/libros")
async def listar_libros(editorial_id: int, session: AsyncSession = Depends(get_session)):
    libros = await service.listar_libros(session, editorial_id)
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
