from sqlmodel import SQLModel


class GeneroCreate(SQLModel):
    nombre: str


class GeneroRead(SQLModel):
    id: int
    nombre: str
