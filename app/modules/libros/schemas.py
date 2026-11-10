from decimal import Decimal

from pydantic import ConfigDict, Field
from sqlmodel import SQLModel


class AutorLibroItem(SQLModel):
    autor_id: int
    rol: str
    orden: int = Field(ge=1)


class LibroCreate(SQLModel):
    isbn: str
    titulo: str
    precio: Decimal = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    editorial_id: int
    genero_id: int | None = None
    autores: list[AutorLibroItem] = Field(default_factory=list)


class LibroUpdate(SQLModel):
    isbn: str | None = None
    titulo: str | None = None
    precio: Decimal | None = Field(default=None, gt=0)
    stock: int | None = Field(default=None, ge=0)
    editorial_id: int | None = None
    genero_id: int | None = None


class EditorialRef(SQLModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    pais: str


class GeneroRef(SQLModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str


class AutorRef(SQLModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    nacionalidad: str


class AutoriaRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)
    autor_id: int
    rol: str
    orden: int
    autor: AutorRef | None = None


class LibroRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    isbn: str
    titulo: str
    precio: Decimal
    stock: int
    editorial_id: int
    genero_id: int | None = None
    editorial: EditorialRef | None = None
    genero: GeneroRef | None = None
    autorias: list[AutoriaRead] = Field(default_factory=list)
