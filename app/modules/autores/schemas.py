from sqlmodel import SQLModel


class AutorCreate(SQLModel):
    nombre: str
    nacionalidad: str


class AutorUpdate(SQLModel):
    nombre: str | None = None
    nacionalidad: str | None = None


class AutorRead(SQLModel):
    id: int
    nombre: str
    nacionalidad: str
