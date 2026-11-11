"""Modelo de tabla de géneros.

Relación con Libro: AGREGACIÓN OPCIONAL. El libro puede incorporar un género
que ya existe; es optativo, así que libro.genero_id admite NULL.
"""

from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.libros.models import Libro


class Genero(SQLModel, table=True):
    __tablename__ = "genero"
    __table_args__ = (
        UniqueConstraint("nombre", name="uq_genero_nombre"),
    )

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100)

    libros: list["Libro"] = Relationship(back_populates="genero")
