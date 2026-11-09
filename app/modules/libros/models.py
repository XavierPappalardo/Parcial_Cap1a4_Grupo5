"""Modelos de tabla de libros y de su relación con autores.

- Libro ↔ Editorial: agregación (libro.editorial_id, obligatoria).
- Libro ↔ Genero: agregación opcional (libro.genero_id, admite NULL).
- Libro ↔ Autor: muchos a muchos CON DATOS PROPIOS (rol y orden), por eso la
  tabla intermedia es una entidad (LibroAutor) y no un link_model.
"""

from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, Column, Numeric, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.autores.models import Autor
    from app.modules.editoriales.models import Editorial
    from app.modules.generos.models import Genero
    from app.modules.ventas.models import RenglonVenta


class Libro(SQLModel, table=True):
    __tablename__ = "libro"
    __table_args__ = (
        UniqueConstraint("isbn", name="uq_libro_isbn"),  # RN-01
        CheckConstraint("precio > 0", name="ck_libro_precio_positivo"),  # RN-03
        CheckConstraint("stock >= 0", name="ck_libro_stock_no_negativo"),  # RN-03
    )

    id: int | None = Field(default=None, primary_key=True)
    isbn: str = Field(max_length=20)
    titulo: str = Field(max_length=200)
    # Dinero: Decimal / NUMERIC(10,2), nunca float.
    precio: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    stock: int = Field(default=0)

    # Claves foráneas, todas con índice (PostgreSQL no lo crea solo).
    editorial_id: int = Field(foreign_key="editorial.id", index=True)
    genero_id: int | None = Field(default=None, foreign_key="genero.id", index=True)

    editorial: "Editorial" = Relationship(back_populates="libros")
    genero: Optional["Genero"] = Relationship(back_populates="libros")
    # Autorías: se navega libro.autorias[i].autor. Las autorías nacen y mueren con el libro.
    autorias: list["LibroAutor"] = Relationship(
        back_populates="libro",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    renglones: list["RenglonVenta"] = Relationship(back_populates="libro")


class LibroAutor(SQLModel, table=True):
    """Objeto de asociación entre Libro y Autor, con el rol y el orden de la autoría."""

    __tablename__ = "libro_autor"
    __table_args__ = (
        CheckConstraint("orden >= 1", name="ck_libro_autor_orden_positivo"),
        CheckConstraint(
            "rol IN ('autor', 'coautor', 'traductor', 'ilustrador')",
            name="ck_libro_autor_rol",
        ),
    )

    # Clave primaria compuesta (libro_id, autor_id); cada columna es además FK con índice.
    libro_id: int = Field(foreign_key="libro.id", primary_key=True, index=True)
    autor_id: int = Field(foreign_key="autor.id", primary_key=True, index=True)
    rol: str = Field(max_length=20)
    orden: int

    libro: "Libro" = Relationship(back_populates="autorias")
    autor: "Autor" = Relationship(back_populates="autorias")
