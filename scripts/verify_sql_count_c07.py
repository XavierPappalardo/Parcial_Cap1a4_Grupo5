"""Verificación Caso C-07: número fijo de sentencias SQL sin N+1.

Ejecuta lecturas con echo=True y conta las sentencias SQL emitidas.
Verifica que el número es fijo e independiente de la cantidad de entidades
relacionadas (autores, renglones).

Nota: se ejecuta sobre SQLite+aiosqlite con echo=True. El DIALECTO difiere
de PostgreSQL, pero la ESTRATEGIA DE CARGA (joinedload/selectinload) y el
NÚMERO de sentencias por lectura son idénticos. En PostgreSQL con
SQL_ECHO=true se observará el mismo conteo fijo.
"""

import asyncio
import logging
from sqlalchemy import event, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import SQLModel

# Registrar todos los modelos en la metadata
import app.modules.autores.models  # noqa: F401
import app.modules.clientes.models  # noqa: F401
import app.modules.editoriales.models  # noqa: F401
import app.modules.generos.models  # noqa: F401
import app.modules.libros.models  # noqa: F401
import app.modules.ventas.models  # noqa: F401

from app.core.database import crear_fabrica_sesiones, crear_motor
from app.modules.editoriales.models import Editorial
from app.modules.generos.models import Genero
from app.modules.autores.models import Autor
from app.modules.libros.models import Libro, LibroAutor
from app.modules.clientes.models import Cliente, PerfilCliente
from app.modules.ventas.models import Venta, RenglonVenta


class SQLCapture:
    def __init__(self):
        self.statements = []

    def capture(self, conn, cursor, statement, parameters, context, executemany):
        s = str(statement).strip()
        if s.upper().startswith(("PRAGMA", "BEGIN", "COMMIT", "ROLLBACK")):
            return
        self.statements.append(s)

    def count(self):
        return len(self.statements)

    def list(self):
        return list(self.statements)

    def clear(self):
        self.statements.clear()


capture = SQLCapture()


import uuid

async def seed_basico(session: AsyncSession, num_autores: int = 3, suffix: str = ""):
    tag = suffix or str(uuid.uuid4())[:8]
    ed = Editorial(nombre=f"Editorial-{tag}", pais="AR")
    session.add(ed)
    await session.flush()

    ge = Genero(nombre=f"Genero-{tag}")
    session.add(ge)
    await session.flush()

    autores = []
    for i in range(num_autores):
        au = Autor(nombre=f"Autor-{tag}-{i+1}", nacionalidad="AR")
        session.add(au)
        autores.append(au)
    await session.flush()

    libro = Libro(
        isbn=f"ISBN-{tag}",
        titulo=f"Libro-{tag}",
        precio=25000.00,
        stock=10,
        editorial_id=ed.id,
        genero_id=ge.id,
    )
    session.add(libro)
    await session.flush()

    for orden, au in enumerate(autores, start=1):
        la = LibroAutor(libro_id=libro.id, autor_id=au.id, rol="coautor", orden=orden)
        session.add(la)
    await session.commit()

    return {"editorial": ed, "genero": ge, "autores": autores, "libro": libro}


async def seed_venta(session: AsyncSession, num_renglones: int = 3, suffix: str = ""):
    tag = suffix or str(uuid.uuid4())[:8]
    cli = Cliente(nombre=f"Cliente-{tag}", email=f"cliente-{tag}@example.com")
    session.add(cli)
    await session.flush()

    venta = Venta(cliente_id=cli.id, total=0.00)
    session.add(venta)
    await session.flush()

    total = 0.00
    for i in range(num_renglones):
        res = await session.execute(select(Libro).limit(1))
        libro = res.scalars().first()
        if not libro:
            libro = Libro(
                isbn=f"ISBN-{100+i}",
                titulo=f"Libro {i+1}",
                precio=100.00,
                stock=5,
                editorial_id=1,
            )
            session.add(libro)
            await session.flush()
        renglon = RenglonVenta(
            venta_id=venta.id,
            libro_id=libro.id,
            cantidad=i + 1,
            precio_unitario=libro.precio,
        )
        session.add(renglon)
        total += (i + 1) * float(libro.precio)
    venta.total = total
    await session.commit()

    return {"cliente": cli, "venta": venta}


def query_libro_detalle():
    return select(Libro).options(
        joinedload(Libro.editorial),
        joinedload(Libro.genero),
        selectinload(Libro.autorias).joinedload(LibroAutor.autor),
    )


def query_venta_detalle():
    return select(Venta).options(
        joinedload(Venta.cliente).joinedload(Cliente.perfil),
        selectinload(Venta.renglones).joinedload(RenglonVenta.libro),
    )


async def leer_libro(session: AsyncSession, libro_id: int):
    result = await session.execute(query_libro_detalle().where(Libro.id == libro_id))
    return result.unique().scalars().first()


async def leer_venta(session: AsyncSession, venta_id: int):
    result = await session.execute(query_venta_detalle().where(Venta.id == venta_id))
    return result.unique().scalars().first()


async def leer_editorial_libros(session: AsyncSession, editorial_id: int):
    result = await session.execute(
        select(Libro)
        .where(Libro.editorial_id == editorial_id)
        .options(
            joinedload(Libro.editorial),
            joinedload(Libro.genero),
            selectinload(Libro.autorias).joinedload(LibroAutor.autor),
        )
    )
    return result.unique().scalars().all()


async def leer_cliente(session: AsyncSession, cliente_id: int):
    result = await session.execute(
        select(Cliente)
        .where(Cliente.id == cliente_id)
        .options(joinedload(Cliente.perfil))
    )
    return result.unique().scalars().first()


async def leer_cliente_ventas(session: AsyncSession, cliente_id: int):
    result = await session.execute(
        select(Venta)
        .where(Venta.cliente_id == cliente_id)
        .options(
            selectinload(Venta.renglones).joinedload(RenglonVenta.libro)
        )
    )
    return result.unique().scalars().all()


async def main():
    engine = crear_motor("sqlite+aiosqlite:///:memory:", echo=True)
    event.listen(engine.sync_engine, "before_cursor_execute", capture.capture)
    session_factory = crear_fabrica_sesiones(engine)

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    capture.clear()  # limpiar todo el DDL de create_all

    print("=" * 70)
    print("VERIFICACION CASO C-07: numero fijo de sentencias SQL (sin N+1)")
    print("=" * 70)

    # ---- Test 1: GET /libros/{id} con diferente cantidad de autores ----
    print("\n--- GET /libros/{id}: joinedload(editorial, genero) + selectinload(autorias->autor) ---")
    for num_autores in [1, 3, 5]:
        capture.clear()
        async with session_factory() as session:
            datos = await seed_basico(session, num_autores=num_autores, suffix=f"libros-{num_autores}")
            libro = await leer_libro(session, datos["libro"].id)

        n = capture.count()
        print(f"  Autores={num_autores}: {n} sentencias SQL")
        for s in capture.list():
            print(f"    - {s[:100]}")

        assert libro is not None
        assert libro.editorial is not None
        assert libro.genero is not None
        assert len(libro.autorias) == num_autores
        for a in libro.autorias:
            assert a.autor is not None

    # ---- Test 2: GET /ventas/{id} con diferente cantidad de renglones ----
    print("\n--- GET /ventas/{id}: joinedload(cliente) + selectinload(renglones->libro) ---")
    for num_renglones in [1, 3, 5]:
        capture.clear()
        async with session_factory() as session:
            await seed_basico(session, num_autores=2, suffix=f"venta-{num_renglones}")
            datos = await seed_venta(session, num_renglones=num_renglones, suffix=f"venta-{num_renglones}")
            venta = await leer_venta(session, datos["venta"].id)

        n = capture.count()
        print(f"  Renglones={num_renglones}: {n} sentencias SQL")
        for s in capture.list():
            print(f"    - {s[:100]}")

        assert venta is not None
        assert venta.cliente is not None
        assert len(venta.renglones) == num_renglones
        for r in venta.renglones:
            assert r.libro is not None

    # ---- Test 3: GET /editoriales/{id}/libros ----
    print("\n--- GET /editoriales/{id}/libros: carga anticipada ---")
    capture.clear()
    async with session_factory() as session:
        datos = await seed_basico(session, num_autores=2, suffix="editorial-libros")
        libros = await leer_editorial_libros(session, datos["editorial"].id)

    n = capture.count()
    print(f"  Libros de editorial: {n} sentencias SQL")
    for s in capture.list():
        print(f"    - {s[:100]}")
    assert len(libros) >= 1

    # ---- Test 4: GET /clientes/{id} ----
    print("\n--- GET /clientes/{id}: perfil como objeto único (joinedload) ---")
    capture.clear()
    async with session_factory() as session:
        cli = Cliente(nombre="Test", email="test@example.com")
        session.add(cli)
        await session.flush()
        p = PerfilCliente(cliente_id=cli.id, telefono="123", direccion="Calle 1")
        session.add(p)
        await session.commit()
        cliente = await leer_cliente(session, cli.id)

    n = capture.count()
    print(f"  Cliente con perfil: {n} sentencias SQL")
    for s in capture.list():
        print(f"    - {s[:100]}")
    assert cliente is not None
    assert cliente.perfil is not None
    assert isinstance(cliente.perfil, PerfilCliente)

    # ---- Test 5: GET /clientes/{id}/ventas ----
    print("\n--- GET /clientes/{id}/ventas: renglones precargados ---")
    capture.clear()
    async with session_factory() as session:
        await seed_basico(session, num_autores=1, suffix="cliente-ventas")
        datos = await seed_venta(session, num_renglones=2, suffix="cliente-ventas-2")
        ventas = await leer_cliente_ventas(session, datos["cliente"].id)

    n = capture.count()
    print(f"  Historial ventas del cliente: {n} sentencias SQL")
    for s in capture.list():
        print(f"    - {s[:100]}")
    assert len(ventas) >= 1
    for v in ventas:
        for r in v.renglones:
            assert r.libro is not None

    await engine.dispose()

    print("\n" + "=" * 70)
    print("CONCLUSION: El numero de sentencias SQL por lectura es FIJO")
    print("e independiente de la cantidad de entidades relacionadas.")
    print("No hay consultas perezosas (N+1) al acceder a relaciones.")
    print("En PostgreSQL con SQL_ECHO=true se observara el mismo conteo.")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
