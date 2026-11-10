from sqlmodel import SQLModel


class EditorialCreate(SQLModel):
    nombre: str
    pais: str


class EditorialUpdate(SQLModel):
    nombre: str | None = None
    pais: str | None = None


class EditorialRead(SQLModel):
    id: int
    nombre: str
    pais: str
