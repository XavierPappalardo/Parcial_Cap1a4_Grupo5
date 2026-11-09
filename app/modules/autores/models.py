"""Modelo de tabla de autores.

Un autor se vincula con sus libros a través de la entidad intermedia
LibroAutor (módulo libros), que guarda el rol y el orden de cada autoría.
"""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.libros.models import LibroAutor


class Autor(SQLModel, table=True):
    __tablename__ = "autor"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=150)
    nacionalidad: str = Field(max_length=80)

    # Se navega autor.autorias[i].libro (no hay link_model: la relación tiene datos propios).
    autorias: list["LibroAutor"] = Relationship(back_populates="autor")
