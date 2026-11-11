import datetime
from decimal import Decimal
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class Cliente(SQLModel, table=True):
    __tablename__ = "cliente"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    email: str = Field(unique=True, index=True)

    perfil: Optional["PerfilCliente"] = Relationship(back_populates="cliente")
    ventas: list["Venta"] = Relationship(back_populates="cliente")


class PerfilCliente(SQLModel, table=True):
    __tablename__ = "perfil_cliente"

    id: Optional[int] = Field(default=None, primary_key=True)
    cliente_id: int = Field(foreign_key="cliente.id", unique=True, index=True)
    telefono: str
    direccion: str

    cliente: Cliente = Relationship(back_populates="perfil")
