"""Modelos de tabla de ventas y sus renglones.

- Venta ↔ Cliente: ASOCIACIÓN. La venta conoce al cliente (venta.cliente_id),
  pero ninguno es parte del otro.
- Venta ↔ RenglonVenta: COMPOSICIÓN. El renglón no tiene sentido sin su venta y
  nace con ella: la FK vive en renglon_venta.venta_id y la relación lleva
  cascade "all, delete-orphan".
- RenglonVenta ↔ Libro: ASOCIACIÓN. El renglón nombra un libro que ya existe.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Column, DateTime, Numeric, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.clientes.models import Cliente
    from app.modules.libros.models import Libro


class Venta(SQLModel, table=True):
    __tablename__ = "venta"
    __table_args__ = (
        CheckConstraint("total >= 0", name="ck_venta_total_no_negativo"),
    )

    id: int | None = Field(default=None, primary_key=True)
    cliente_id: int = Field(foreign_key="cliente.id", index=True)
    # Fecha con zona horaria; la pone el servidor, nunca viaja en el DTO de alta.
    fecha: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True), nullable=False, server_default=func.now()
        ),
    )
    # Dinero: Decimal / NUMERIC(12,2). Lo calcula el servidor (RN-07).
    total: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(Numeric(12, 2), nullable=False),
    )

    cliente: "Cliente" = Relationship(back_populates="ventas")
    # Composición: los renglones se agregan a venta.renglones y se guardan con ella.
    renglones: list["RenglonVenta"] = Relationship(
        back_populates="venta",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class RenglonVenta(SQLModel, table=True):
    __tablename__ = "renglon_venta"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="ck_renglon_venta_cantidad_positiva"),
        CheckConstraint(
            "precio_unitario > 0", name="ck_renglon_venta_precio_positivo"
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    venta_id: int = Field(foreign_key="venta.id", index=True)
    libro_id: int = Field(foreign_key="libro.id", index=True)
    cantidad: int
    # Precio copiado del libro al registrar la venta (RN-06): NUMERIC(10,2).
    precio_unitario: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))

    venta: "Venta" = Relationship(back_populates="renglones")
    libro: "Libro" = Relationship(back_populates="renglones")
