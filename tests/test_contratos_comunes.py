"""Verificaciones de contratos comunes (tarea 2.1, 2.2 parciales)."""

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.core.common import aplicar_patch, paginacion


class DemoUpdate(BaseModel):
    nombre: str | None = None
    pais: str | None = None


class Demo:
    def __init__(self):
        self.nombre = "A"
        self.pais = "B"


def test_aplicar_patch_solo_campos_enviados():
    obj = Demo()
    aplicar_patch(obj, DemoUpdate(nombre="Z"))
    assert obj.nombre == "Z"
    assert obj.pais == "B"


def test_paginacion_rn10_valida_y_422():
    app = FastAPI()

    @app.get("/items")
    async def items(p=Depends(paginacion)):
        return p

    with TestClient(app) as c:
        assert c.get("/items").json() == {"limit": 20, "offset": 0}
        assert c.get("/items?limit=5&offset=10").json() == {"limit": 5, "offset": 10}
        assert c.get("/items?limit=0").status_code == 422
        assert c.get("/items?limit=101").status_code == 422
        assert c.get("/items?offset=-1").status_code == 422
