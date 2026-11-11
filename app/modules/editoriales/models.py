from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class Editorial(SQLModel, table=True):
    __tablename__ = "editorial"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True, index=True)
    pais: str

    libros: list["Libro"] = Relationship(back_populates="editorial")
