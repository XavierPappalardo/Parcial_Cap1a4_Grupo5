"""Tests de API para Ejercicios 3 y 4 (casos representativos)."""

import asyncio
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel

from app.core import config
from app.core.database import crear_fabrica_sesiones, crear_motor
from app.main import app as main_app

import app.modules.autores.models  # noqa: F401
import app.modules.clientes.models  # noqa: F401
import app.modules.editoriales.models  # noqa: F401
import app.modules.generos.models  # noqa: F401
import app.modules.libros.models  # noqa: F401
import app.modules.ventas.models  # noqa: F401


@pytest.fixture
def cliente_api(database_url_sqlite):
    pytest.importorskip("aiosqlite")
    engine = crear_motor(database_url_sqlite)

    async def init():
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
            await conn.run_sync(SQLModel.metadata.create_all)

    asyncio.run(init())
    main_app.state.engine = engine
    main_app.state.session_factory = crear_fabrica_sesiones(engine)
    with TestClient(main_app) as c:
        yield c
    asyncio.run(engine.dispose())
    config.get_settings.cache_clear()


def _seed_basico(c):
    ed = c.post("/editoriales/", json={"nombre": "Sudamericana", "pais": "AR"}).json()
    au = c.post("/autores/", json={"nombre": "Julio Cortazar", "nacionalidad": "AR"}).json()
    cli = c.post("/clientes/", json={"nombre": "Ana", "email": "ana@example.com"}).json()
    lib = c.post(
        "/libros/",
        json={
            "isbn": "ISBN-001",
            "titulo": "Rayuela",
            "precio": "25000.00",
            "stock": 10,
            "editorial_id": ed["id"],
            "genero_id": None,
            "autores": [{"autor_id": au["id"], "rol": "autor", "orden": 1}],
        },
    ).json()
    return {"editorial": ed, "autor": au, "cliente": cli, "libro": lib}


# 3.1 Editoriales
def test_editoriales_201_409_404_paginacion(cliente_api):
    c = cliente_api
    r = c.post("/editoriales/", json={"nombre": "Planeta", "pais": "AR"})
    assert r.status_code == 201 and r.json()["id"]
    r2 = c.post("/editoriales/", json={"nombre": "Planeta", "pais": "AR"})
    assert r2.status_code == 409
    assert "traceback" not in r2.text.lower() and "uq_" not in r2.text.lower()
    assert c.get("/editoriales/99999").status_code == 404
    lst = c.get("/editoriales/?limit=1&offset=0")
    assert lst.status_code == 200 and len(lst.json()) == 1


# 3.2 Géneros
def test_generos_201_409_404(cliente_api):
    c = cliente_api
    assert c.post("/generos/", json={"nombre": "Novela"}).status_code == 201
    assert c.post("/generos/", json={"nombre": "Novela"}).status_code == 409
    assert c.get("/generos/99999/libros").status_code == 404


# 3.3 Autores
def test_autores_201_404_y_libros_con_rol(cliente_api):
    c = cliente_api
    s = _seed_basico(c)
    r = c.get(f"/autores/{s['autor']['id']}/libros")
    assert r.status_code == 200
    data = r.json()
    assert any(x["rol"] == "autor" and x["orden"] == 1 for x in data)
    assert c.get("/autores/99999").status_code == 404


# 4.1, 4.3 Libros + alta relacional sin pre-check
def test_libro_alta_relacional_201_y_fk_inexistente_409(cliente_api):
    c = cliente_api
    ed = c.post("/editoriales/", json={"nombre": "E1", "pais": "AR"}).json()
    au = c.post("/autores/", json={"nombre": "A1", "nacionalidad": "AR"}).json()
    ok = c.post(
        "/libros/",
        json={
            "isbn": "X1",
            "titulo": "Libro X",
            "precio": "10.00",
            "stock": 1,
            "editorial_id": ed["id"],
            "genero_id": None,
            "autores": [{"autor_id": au["id"], "rol": "autor", "orden": 1}],
        },
    )
    assert ok.status_code == 201
    body = ok.json()
    assert body["editorial"]["id"] == ed["id"]
    assert body["autorias"][0]["autor"]["id"] == au["id"]
    bad = c.post(
        "/libros/",
        json={
            "isbn": "X2",
            "titulo": "Libro Y",
            "precio": "10.00",
            "stock": 1,
            "editorial_id": 99999,
            "genero_id": None,
            "autores": [{"autor_id": au["id"], "rol": "autor", "orden": 1}],
        },
    )
    assert bad.status_code == 409
    assert "traceback" not in bad.text.lower()


# 4.2 Búsqueda RN-11 / C-08
def test_busqueda_titulo_parametrizada_sin_inyeccion(cliente_api):
    c = cliente_api
    _seed_basico(c)
    r = c.get("/libros/", params={"titulo": "rayu"})
    assert r.status_code == 200 and len(r.json()) >= 1
    inj = c.get("/libros/", params={"titulo": "' OR '1'='1"})
    assert inj.status_code == 200
    assert inj.json() == []


# 5.1, 5.2 Cliente y perfil 1:1
def test_cliente_perfil_objeto_y_409_duplicado(cliente_api):
    c = cliente_api
    cli = c.post("/clientes/", json={"nombre": "B", "email": "b@example.com"}).json()
    got = c.get(f"/clientes/{cli['id']}").json()
    assert "perfil" in got and got["perfil"] is None
    p = c.post(f"/clientes/{cli['id']}/perfil", json={"telefono": "123", "direccion": "Calle 1"})
    assert p.status_code == 201
    got2 = c.get(f"/clientes/{cli['id']}").json()
    assert isinstance(got2["perfil"], dict)
    dup = c.post(f"/clientes/{cli['id']}/perfil", json={"telefono": "456", "direccion": "Calle 2"})
    assert dup.status_code == 409


# 6.2 Venta atómica, RN-04-07, C-05/C-06 equivalentes
def test_venta_atomica_precios_copiados_total_y_409_fk(cliente_api):
    c = cliente_api
    s = _seed_basico(c)
    # segundo libro
    lib2 = c.post(
        "/libros/",
        json={
            "isbn": "ISBN-002",
            "titulo": "Otro",
            "precio": "100.00",
            "stock": 5,
            "editorial_id": s["editorial"]["id"],
            "genero_id": None,
            "autores": [{"autor_id": s["autor"]["id"], "rol": "autor", "orden": 1}],
        },
    ).json()
    v = c.post(
        "/ventas/",
        json={
            "cliente_id": s["cliente"]["id"],
            "renglones": [
                {"libro_id": s["libro"]["id"], "cantidad": 2},
                {"libro_id": lib2["id"], "cantidad": 1},
            ],
        },
    )
    assert v.status_code == 201
    body = v.json()
    assert len(body["renglones"]) == 2
    precios = {r["libro_id"]: str(r["precio_unitario"]) for r in body["renglones"]}
    assert Decimal(precios[s["libro"]["id"]]) == Decimal("25000.00")
    assert Decimal(precios[lib2["id"]]) == Decimal("100.00")
    assert Decimal(str(body["total"])) == Decimal("50100.00")
    assert all("subtotal" in r and "titulo" in r for r in body["renglones"])
    # FK inexistente -> 409
    bad = c.post(
        "/ventas/",
        json={"cliente_id": s["cliente"]["id"], "renglones": [{"libro_id": 99999, "cantidad": 1}]},
    )
    assert bad.status_code == 409


def test_venta_rn05_422(cliente_api):
    c = cliente_api
    s = _seed_basico(c)
    assert c.post("/ventas/", json={"cliente_id": s["cliente"]["id"], "renglones": []}).status_code == 422
    dup = c.post(
        "/ventas/",
        json={
            "cliente_id": s["cliente"]["id"],
            "renglones": [
                {"libro_id": s["libro"]["id"], "cantidad": 1},
                {"libro_id": s["libro"]["id"], "cantidad": 2},
            ],
        },
    )
    assert dup.status_code == 422
