"""Modelo de tabla de editoriales.

Relación con Libro: AGREGACIÓN. El libro incorpora una editorial que ya existe
(viaja su id) y la misma editorial la comparten muchos libros.
"""

from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.libros.models import Libro


class Editorial(SQLModel, table=True):
    __tablename__ = "editorial"
    __table_args__ = (
        # RN-01 análoga para editoriales: el nombre es único, lo garantiza la base.
        UniqueConstraint("nombre", name="uq_editorial_nombre"),
    )

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=150)
    pais: str = Field(max_length=80)

    # Lado "uno" de la agregación: una editorial, muchos libros.
    libros: list["Libro"] = Relationship(back_populates="editorial")
