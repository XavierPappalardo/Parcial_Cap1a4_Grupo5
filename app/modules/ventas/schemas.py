from datetime import datetime
from decimal import Decimal

from pydantic import ConfigDict, Field, field_validator, model_validator
from sqlmodel import SQLModel


class RenglonCreate(SQLModel):
    libro_id: int
    cantidad: int = Field(gt=0)


class VentaCreate(SQLModel):
    cliente_id: int
    renglones: list[RenglonCreate]

    @model_validator(mode="after")
    def validar_renglones(self):
        if not self.renglones:
            raise ValueError("La venta debe tener al menos un renglón")
        ids = [r.libro_id for r in self.renglones]
        if len(ids) != len(set(ids)):
            raise ValueError("No se puede repetir el mismo libro en la venta")
        return self


class PerfilClienteRef(SQLModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cliente_id: int
    telefono: str
    direccion: str


class ClienteRef(SQLModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    email: str
    perfil: PerfilClienteRef | None = None


class LibroRef(SQLModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    titulo: str


class RenglonRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    venta_id: int
    libro_id: int
    cantidad: int
    precio_unitario: Decimal
    libro: LibroRef | None = None

    @property
    def subtotal(self) -> Decimal:
        return self.cantidad * self.precio_unitario


class RenglonReadOut(SQLModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    venta_id: int
    libro_id: int
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal
    titulo: str | None = None


class VentaRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cliente_id: int
    fecha: datetime
    total: Decimal
    cliente: ClienteRef | None = None
    renglones: list[RenglonReadOut] = Field(default_factory=list)


def venta_a_read(venta) -> dict:
    renglones = []
    for r in venta.renglones:
        titulo = r.libro.titulo if getattr(r, "libro", None) else None
        renglones.append(
            {
                "id": r.id,
                "venta_id": r.venta_id,
                "libro_id": r.libro_id,
                "cantidad": r.cantidad,
                # La consigna muestra los importes como strings con dos
                # decimales; FastAPI convertiría un Decimal a float si se
                # devolviera el objeto directamente.
                "precio_unitario": str(r.precio_unitario),
                "subtotal": str(r.cantidad * r.precio_unitario),
                "titulo": titulo,
            }
        )
    cliente = None
    if getattr(venta, "cliente", None):
        c = venta.cliente
        perfil = None
        if getattr(c, "perfil", None):
            p = c.perfil
            perfil = {
                "id": p.id,
                "cliente_id": p.cliente_id,
                "telefono": p.telefono,
                "direccion": p.direccion,
            }
        cliente = {"id": c.id, "nombre": c.nombre, "email": c.email, "perfil": perfil}
    return {
        "id": venta.id,
        "cliente_id": venta.cliente_id,
        "fecha": venta.fecha,
        "total": str(venta.total),
        "cliente": cliente,
        "renglones": renglones,
    }
