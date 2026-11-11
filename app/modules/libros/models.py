from decimal import Decimal
from typing import Optional

from sqlalchemy import CheckConstraint, Column, Numeric
from sqlmodel import Field, Relationship, SQLModel

from app.modules.editoriales.models import Editorial
from app.modules.generos.models import Genero


class Libro(SQLModel, table=True):
    __tablename__ = "libro"
    __table_args__ = (
        CheckConstraint("precio > 0", name="chk_libro_precio_gt_0"),
        CheckConstraint("stock >= 0", name="chk_libro_stock_gte_0"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    isbn: str = Field(unique=True, index=True)
    titulo: str
    precio: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    stock: int
    editorial_id: int = Field(foreign_key="editorial.id", index=True)
    genero_id: Optional[int] = Field(default=None, foreign_key="genero.id", index=True)

    editorial: Editorial = Relationship(back_populates="libros")
    genero: Optional[Genero] = Relationship(back_populates="libros")
    autorias: list["LibroAutor"] = Relationship(
        back_populates="libro", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    renglones: list["RenglonVenta"] = Relationship(back_populates="libro")


class LibroAutor(SQLModel, table=True):
    __tablename__ = "libro_autor"
    __table_args__ = (
        CheckConstraint("orden >= 1", name="chk_libro_autor_orden_gte_1"),
        CheckConstraint(
            "rol IN ('autor', 'coautor', 'traductor', 'ilustrador')",
            name="chk_libro_autor_rol_valido",
        ),
    )

    libro_id: int = Field(foreign_key="libro.id", primary_key=True, index=True)
    autor_id: int = Field(foreign_key="autor.id", primary_key=True, index=True)
    rol: str
    orden: int

    libro: Libro = Relationship(back_populates="autorias")
    autor: "Autor" = Relationship(back_populates="autorias")
