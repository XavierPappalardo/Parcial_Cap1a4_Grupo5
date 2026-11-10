"""Modelos de tabla de clientes y su perfil.

- Cliente ↔ PerfilCliente: UNO A UNO. La FK vive en perfil_cliente.cliente_id y
  es UNIQUE: la base impide un segundo perfil para el mismo cliente (RN-09).
- Cliente ↔ Venta: asociación (la FK vive en venta.cliente_id, módulo ventas).
"""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.ventas.models import Venta


class Cliente(SQLModel, table=True):
    __tablename__ = "cliente"
    __table_args__ = (
        UniqueConstraint("email", name="uq_cliente_email"),  # RN-02
    )

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=150)
    email: str = Field(max_length=254)

    # Devuelve UN objeto (o None), no una lista: uselist=False es obligatorio
    # porque la FK está del lado de PerfilCliente.
    perfil: Optional["PerfilCliente"] = Relationship(
        back_populates="cliente",
        sa_relationship_kwargs={"uselist": False},
    )
    ventas: list["Venta"] = Relationship(back_populates="cliente")


class PerfilCliente(SQLModel, table=True):
    __tablename__ = "perfil_cliente"

    id: int | None = Field(default=None, primary_key=True)
    # unique=True + index=True => un único índice UNIQUE sobre la FK (RN-09).
    cliente_id: int = Field(foreign_key="cliente.id", unique=True, index=True)
    telefono: str = Field(max_length=30)
    direccion: str = Field(max_length=250)

    cliente: "Cliente" = Relationship(back_populates="perfil")
