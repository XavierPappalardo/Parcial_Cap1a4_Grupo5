from pydantic import ConfigDict
from sqlmodel import SQLModel


class ClienteCreate(SQLModel):
    nombre: str
    email: str


class ClienteUpdate(SQLModel):
    nombre: str | None = None
    email: str | None = None


class PerfilClienteCreate(SQLModel):
    telefono: str
    direccion: str


class PerfilClienteRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cliente_id: int
    telefono: str
    direccion: str


class ClienteRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    email: str
    perfil: PerfilClienteRead | None = None
