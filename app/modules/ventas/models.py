import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import CheckConstraint, Column, DateTime, Numeric
from sqlmodel import Field, Relationship, SQLModel

from app.modules.clientes.models import Cliente
from app.modules.libros.models import Libro


class Venta(SQLModel, table=True):
    __tablename__ = "venta"
    __table_args__ = (
        CheckConstraint("total >= 0", name="chk_venta_total_gte_0"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    cliente_id: int = Field(foreign_key="cliente.id", index=True)
    fecha: datetime.datetime = Field(sa_column=Column(DateTime(timezone=True)))
    total: Decimal = Field(sa_column=Column(Numeric(12, 2)))

    cliente: Cliente = Relationship(back_populates="ventas")
    renglones: list["RenglonVenta"] = Relationship(
        back_populates="venta", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class RenglonVenta(SQLModel, table=True):
    __tablename__ = "renglon_venta"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="chk_renglon_venta_cantidad_gt_0"),
        CheckConstraint("precio_unitario > 0", name="chk_renglon_venta_precio_unitario_gt_0"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    venta_id: int = Field(foreign_key="venta.id", index=True)
    libro_id: int = Field(foreign_key="libro.id", index=True)
    cantidad: int
    precio_unitario: Decimal = Field(sa_column=Column(Numeric(10, 2)))

    venta: Venta = Relationship(back_populates="renglones")
    libro: Libro = Relationship(back_populates="renglones")
