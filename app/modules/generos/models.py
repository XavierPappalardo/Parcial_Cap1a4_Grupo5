from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class Genero(SQLModel, table=True):
    __tablename__ = "genero"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True, index=True)

    libros: list["Libro"] = Relationship(back_populates="genero")
