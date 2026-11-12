"""Carga de datos iniciales del proyecto (seed).

Uso dentro del contenedor o en local:

    python -m app.seed

El comando es idempotente: si un registro ya existe (por su clave única),
lo reutiliza y no lo duplica. Está pensado para una base vacía, de modo que
los identificadores coincidan con los ejemplos de la consigna:

    cliente 1 -> Ana Gómez (con perfil)
    cliente 2 -> Tomás Ríos (sin perfil)
    libro 1   -> Rayuela (25000.00)
    libro 4   -> Respiración artificial (27000.00)

Con esos ids, el POST /ventas/ de ejemplo (caso C-06 / D-03) suma 77000.00.
Si la base ya tenía datos, el comando imprime los ids reales y avisa si no
coinciden con los del ejemplo.
"""

import asyncio
from decimal import Decimal

from sqlalchemy import select
from sqlmodel import SQLModel

from app.core.config import get_settings
from app.core.database import crear_fabrica_sesiones, crear_motor

# Importar todos los modelos antes de create_all para que el metadata
# conozca las nueve tablas y sus relaciones.
from app.modules.autores.models import Autor  # noqa: F401
from app.modules.clientes.models import Cliente, PerfilCliente  # noqa: F401
from app.modules.editoriales.models import Editorial  # noqa: F401
from app.modules.generos.models import Genero  # noqa: F401
from app.modules.libros.models import Libro, LibroAutor  # noqa: F401
from app.modules.ventas.models import RenglonVenta, Venta  # noqa: F401


async def _primero(session, consulta):
    """Devuelve el primer resultado de una consulta o None."""
    resultado = await session.execute(consulta)
    return resultado.scalars().first()


async def _obtener_o_crear_editorial(session, nombre: str, pais: str) -> Editorial:
    editorial = await _primero(session, select(Editorial).where(Editorial.nombre == nombre))
    if editorial is None:
        editorial = Editorial(nombre=nombre, pais=pais)
        session.add(editorial)
        await session.flush()
    return editorial


async def _obtener_o_crear_genero(session, nombre: str) -> Genero:
    genero = await _primero(session, select(Genero).where(Genero.nombre == nombre))
    if genero is None:
        genero = Genero(nombre=nombre)
        session.add(genero)
        await session.flush()
    return genero


async def _obtener_o_crear_autor(session, nombre: str, nacionalidad: str) -> Autor:
    autor = await _primero(
        session,
        select(Autor).where(
            Autor.nombre == nombre,
            Autor.nacionalidad == nacionalidad,
        ),
    )
    if autor is None:
        autor = Autor(nombre=nombre, nacionalidad=nacionalidad)
        session.add(autor)
        await session.flush()
    return autor


async def _obtener_o_crear_libro(
    session,
    *,
    isbn: str,
    titulo: str,
    precio: Decimal,
    stock: int,
    editorial: Editorial,
    genero: Genero | None,
    autorias: list[tuple[Autor, str, int]],
) -> Libro:
    libro = await _primero(session, select(Libro).where(Libro.isbn == isbn))
    if libro is None:
        libro = Libro(
            isbn=isbn,
            titulo=titulo,
            precio=precio,
            stock=stock,
            editorial_id=editorial.id,
            genero_id=genero.id if genero else None,
        )
        for autor, rol, orden in autorias:
            libro.autorias.append(
                LibroAutor(autor_id=autor.id, rol=rol, orden=orden)
            )
        session.add(libro)
        await session.flush()
    return libro


async def _obtener_o_crear_cliente(session, nombre: str, email: str) -> Cliente:
    cliente = await _primero(session, select(Cliente).where(Cliente.email == email))
    if cliente is None:
        cliente = Cliente(nombre=nombre, email=email)
        session.add(cliente)
        await session.flush()
    return cliente


async def _asegurar_perfil(
    session,
    cliente: Cliente,
    telefono: str,
    direccion: str,
) -> PerfilCliente:
    perfil = await _primero(
        session,
        select(PerfilCliente).where(PerfilCliente.cliente_id == cliente.id),
    )
    if perfil is None:
        perfil = PerfilCliente(
            cliente_id=cliente.id,
            telefono=telefono,
            direccion=direccion,
        )
        session.add(perfil)
        await session.flush()
    return perfil


async def cargar_datos_iniciales() -> None:
    """Crea el catálogo y los clientes iniciales si todavía no existen."""
    settings = get_settings()
    engine = crear_motor(settings.DATABASE_URL, echo=settings.SQL_ECHO)
    fabrica = crear_fabrica_sesiones(engine)

    try:
        async with engine.begin() as conexion:
            await conexion.run_sync(SQLModel.metadata.create_all)

        async with fabrica() as session:
            # Catálogo
            sudamericana = await _obtener_o_crear_editorial(
                session, "Sudamericana", "Argentina"
            )
            alfaguara = await _obtener_o_crear_editorial(
                session, "Alfaguara", "España"
            )
            novela = await _obtener_o_crear_genero(session, "Novela")
            ensayo = await _obtener_o_crear_genero(session, "Ensayo")

            cortazar = await _obtener_o_crear_autor(
                session, "Julio Cortázar", "Argentina"
            )
            bioy = await _obtener_o_crear_autor(
                session, "Adolfo Bioy Casares", "Argentina"
            )
            ocampo = await _obtener_o_crear_autor(
                session, "Silvina Ocampo", "Argentina"
            )
            piglia = await _obtener_o_crear_autor(
                session, "Ricardo Piglia", "Argentina"
            )

            rayuela = await _obtener_o_crear_libro(
                session,
                isbn="978-84-376-0494-7",
                titulo="Rayuela",
                precio=Decimal("25000.00"),
                stock=10,
                editorial=sudamericana,
                genero=novela,
                autorias=[(cortazar, "autor", 1)],
            )
            los_que_aman = await _obtener_o_crear_libro(
                session,
                isbn="978-950-00-0006-6",
                titulo="Los que aman, odian",
                precio=Decimal("21000.00"),
                stock=4,
                editorial=sudamericana,
                genero=novela,
                autorias=[(bioy, "coautor", 1), (ocampo, "coautor", 2)],
            )
            bestiario = await _obtener_o_crear_libro(
                session,
                isbn="978-84-376-0495-4",
                titulo="Bestiario",
                precio=Decimal("19000.00"),
                stock=6,
                editorial=sudamericana,
                genero=novela,
                autorias=[(cortazar, "autor", 1)],
            )
            respiracion = await _obtener_o_crear_libro(
                session,
                isbn="978-84-376-0496-1",
                titulo="Respiración artificial",
                precio=Decimal("27000.00"),
                stock=8,
                editorial=sudamericana,
                # Sin género: demuestra que la agregación es opcional.
                genero=None,
                autorias=[(piglia, "autor", 1)],
            )

            # Clientes
            ana = await _obtener_o_crear_cliente(
                session, "Ana Gómez", "ana@example.com"
            )
            await _asegurar_perfil(
                session,
                ana,
                telefono="11-5555-0101",
                direccion="Av. Siempre Viva 742",
            )
            tomas = await _obtener_o_crear_cliente(
                session, "Tomás Ríos", "tomas@example.com"
            )

            await session.commit()

            # Refrescar para imprimir ids reales (los flush ya los asignaron).
            for entidad in (
                sudamericana,
                alfaguara,
                novela,
                ensayo,
                cortazar,
                bioy,
                ocampo,
                piglia,
                rayuela,
                los_que_aman,
                bestiario,
                respiracion,
                ana,
                tomas,
            ):
                await session.refresh(entidad)

            print("Seed completado.")
            print("")
            print("Editoriales:")
            print(f"  - Sudamericana: id={sudamericana.id}")
            print(f"  - Alfaguara: id={alfaguara.id}")
            print("Géneros:")
            print(f"  - Novela: id={novela.id}")
            print(f"  - Ensayo: id={ensayo.id}")
            print("Autores:")
            for autor in (cortazar, bioy, ocampo, piglia):
                print(f"  - {autor.nombre}: id={autor.id}")
            print("Libros:")
            for libro in (rayuela, los_que_aman, bestiario, respiracion):
                print(f"  - {libro.titulo} ({libro.isbn}): id={libro.id}")
            print("Clientes:")
            print(f"  - Ana Gómez: id={ana.id} (con perfil)")
            print(f"  - Tomás Ríos: id={tomas.id} (sin perfil)")
            print("")

            if (rayuela.id, respiracion.id, tomas.id) != (1, 4, 2):
                print(
                    "AVISO: los ids no son 1, 4 y 2 porque la base ya tenía datos. "
                    "Para el caso D-03, usá una base vacía o ajustá el cuerpo del POST."
                )
            else:
                print("Cuerpo de ejemplo para POST /ventas/ (C-06 / D-03):")
                print(
                    '  {"cliente_id": 2, "renglones": ['
                    '{"libro_id": 1, "cantidad": 2}, '
                    '{"libro_id": 4, "cantidad": 1}]}'
                )
    finally:
        await engine.dispose()


def main() -> None:
    """Punto de entrada del comando ``python -m app.seed``."""
    try:
        asyncio.run(cargar_datos_iniciales())
    except Exception as exc:  # noqa: BLE001 - mensaje limpio para operación
        print(f"ERROR al cargar los datos iniciales: {exc}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
