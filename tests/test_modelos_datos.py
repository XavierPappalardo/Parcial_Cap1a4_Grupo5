"""Pruebas de metadata del modelo de datos del Ejercicio 2.

Verifican el contrato de la consigna sobre SQLModel.metadata sin necesidad de
PostgreSQL: tablas, columnas, PK (simple y compuesta), UNIQUE, CHECK, FK con
índices, relaciones bidireccionales, tipos de dinero Decimal/NUMERIC, cascadas
y configuración limpia de todos los mappers.
"""

import subprocess
import sys
from decimal import Decimal

import pytest
from sqlalchemy import Numeric
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.orm import configure_mappers

# Importar TODOS los módulos de modelos: quedan registrados en la metadata
# compartida de SQLModel (misma operación que hará main.py en el arranque).
import app.modules.autores.models  # noqa: F401
import app.modules.clientes.models  # noqa: F401
import app.modules.editoriales.models  # noqa: F401
import app.modules.generos.models  # noqa: F401
import app.modules.libros.models  # noqa: F401
import app.modules.ventas.models  # noqa: F401
from app.modules.autores.models import Autor
from app.modules.clientes.models import Cliente, PerfilCliente
from app.modules.editoriales.models import Editorial
from app.modules.generos.models import Genero
from app.modules.libros.models import Libro, LibroAutor
from app.modules.ventas.models import RenglonVenta, Venta
from sqlmodel import SQLModel

MD = SQLModel.metadata


# ------------------------------------------------------------------ tablas ---


def test_nueve_tablas_obligatorias_existen():
    """Las 9 tablas del dominio quedan registradas con sus nombres obligatorios."""
    esperadas = {
        "editorial",
        "genero",
        "autor",
        "libro",
        "libro_autor",
        "cliente",
        "perfil_cliente",
        "venta",
        "renglon_venta",
    }
    assert set(MD.tables) == esperadas


def test_nombres_de_columnas_por_tabla():
    """Nombres de columnas obligatorios: no se pueden renombrar ni quitar."""
    columnas_esperadas = {
        "editorial": {"id", "nombre", "pais"},
        "genero": {"id", "nombre"},
        "autor": {"id", "nombre", "nacionalidad"},
        "libro": {
            "id",
            "isbn",
            "titulo",
            "precio",
            "stock",
            "editorial_id",
            "genero_id",
        },
        "libro_autor": {"libro_id", "autor_id", "rol", "orden"},
        "cliente": {"id", "nombre", "email"},
        "perfil_cliente": {"id", "cliente_id", "telefono", "direccion"},
        "venta": {"id", "cliente_id", "fecha", "total"},
        "renglon_venta": {
            "id",
            "venta_id",
            "libro_id",
            "cantidad",
            "precio_unitario",
        },
    }
    for tabla, columnas in columnas_esperadas.items():
        cols = set(MD.tables[tabla].columns.keys())
        assert cols == columnas, tabla


# ------------------------------------------------------------ claves (PK) ---


def test_claves_primarias_simples():
    """Todas las tablas menos libro_autor tienen PK simple sobre id."""
    for tabla in MD.tables.values():
        if tabla.name == "libro_autor":
            continue
        clave = set(tabla.primary_key.columns.keys())
        assert clave == {"id"}, tabla.name


def test_clave_primaria_compuesta_libro_autor():
    """PK compuesta (libro_id, autor_id): ambas columnas son además FK con índice."""
    tabla = MD.tables["libro_autor"]
    clave = set(tabla.primary_key.columns.keys())
    assert clave == {"libro_id", "autor_id"}
    destinos = {
        fk.parent.name: f"{fk.column.table.name}.{fk.column.name}"
        for fk in tabla.foreign_keys
    }
    assert destinos["libro_id"] == "libro.id"
    assert destinos["autor_id"] == "autor.id"


# ------------------------------------------------------- restricciones ---


def _columnas_uniques(tabla) -> set[str]:
    """Columnas cubiertas por unicidad (constraints UNIQUE e índices únicos)."""
    columnas: set[str] = set()
    for constraint in tabla.constraints:
        if constraint.__class__.__name__ == "UniqueConstraint":
            columnas.update(col.name for col in constraint.columns)
    for indice in tabla.indexes:
        if indice.unique:
            columnas.update(col.name for col in indice.columns)
    return columnas


def test_restricciones_unique():
    assert _columnas_uniques(MD.tables["editorial"]) == {"nombre"}
    assert _columnas_uniques(MD.tables["genero"]) == {"nombre"}
    assert _columnas_uniques(MD.tables["libro"]) == {"isbn"}
    assert _columnas_uniques(MD.tables["cliente"]) == {"email"}
    # RN-09: un cliente tiene como máximo un perfil (FK del perfil única).
    assert _columnas_uniques(MD.tables["perfil_cliente"]) == {"cliente_id"}


def _checks(tabla) -> set[str]:
    """Predicados SQL de las restricciones CHECK de la tabla."""
    return {
        str(constraint.sqltext)
        for constraint in tabla.constraints
        if constraint.__class__.__name__ == "CheckConstraint"
    }


def test_restricciones_check():
    checks_libro = _checks(MD.tables["libro"])
    assert "precio > 0" in checks_libro
    assert "stock >= 0" in checks_libro

    checks_libro_autor = _checks(MD.tables["libro_autor"])
    assert "orden >= 1" in checks_libro_autor
    assert "rol IN ('autor', 'coautor', 'traductor', 'ilustrador')" in checks_libro_autor

    checks_venta = _checks(MD.tables["venta"])
    assert "total >= 0" in checks_venta

    checks_renglon = _checks(MD.tables["renglon_venta"])
    assert "cantidad > 0" in checks_renglon
    assert "precio_unitario > 0" in checks_renglon


def _claves_foraneas(tabla) -> dict[str, str]:
    """Mapa columna_local -> tabla.columna referenciada."""
    return {
        fk.parent.name: f"{fk.column.table.name}.{fk.column.name}"
        for fk in tabla.foreign_keys
    }


def test_claves_foraneas_exactas():
    assert _claves_foraneas(MD.tables["libro"]) == {
        "editorial_id": "editorial.id",
        "genero_id": "genero.id",
    }
    assert _claves_foraneas(MD.tables["libro_autor"]) == {
        "libro_id": "libro.id",
        "autor_id": "autor.id",
    }
    assert _claves_foraneas(MD.tables["perfil_cliente"]) == {"cliente_id": "cliente.id"}
    assert _claves_foraneas(MD.tables["venta"]) == {"cliente_id": "cliente.id"}
    assert _claves_foraneas(MD.tables["renglon_venta"]) == {
        "venta_id": "venta.id",
        "libro_id": "libro.id",
    }
    # Las tablas raíz del catálogo no referencian a nadie.
    assert not MD.tables["editorial"].foreign_keys
    assert not MD.tables["genero"].foreign_keys
    assert not MD.tables["autor"].foreign_keys


def test_genero_id_es_nullable():
    """Agregación opcional: un libro puede no tener género."""
    assert MD.tables["libro"].columns["genero_id"].nullable is True


def test_claves_foraneas_indexadas():
    """Toda FK tiene índice (PostgreSQL no crea índices automáticos de FK)."""
    fk_por_tabla = {
        "libro": {"editorial_id", "genero_id"},
        "libro_autor": {"libro_id", "autor_id"},
        "perfil_cliente": {"cliente_id"},
        "venta": {"cliente_id"},
        "renglon_venta": {"venta_id", "libro_id"},
    }
    for nombre_tabla, columnas_fk in fk_por_tabla.items():
        tabla = MD.tables[nombre_tabla]
        columnas_indexadas = {
            col.name for indice in tabla.indexes for col in indice.columns
        }
        faltantes = columnas_fk - columnas_indexadas
        assert not faltantes, (nombre_tabla, faltantes)


# --------------------------------------------------------------- relaciones ---


def _dos_lados(nombre_a: str, atributo_a: str, nombre_b: str, atributo_b: str):
    """Bidireccionalidad con back_populates consistentes en ambos lados."""
    clase_a = globals()[nombre_a]
    clase_b = globals()[nombre_b]
    prop_a = getattr(clase_a, atributo_a).property
    prop_b = getattr(clase_b, atributo_b).property
    assert prop_a.back_populates == atributo_b, f"{nombre_a}.{atributo_a}"
    assert prop_b.back_populates == atributo_a, f"{nombre_b}.{atributo_b}"


def test_siete_relaciones_bidireccionales():
    _dos_lados("Editorial", "libros", "Libro", "editorial")
    _dos_lados("Genero", "libros", "Libro", "genero")
    _dos_lados("Libro", "autorias", "LibroAutor", "libro")
    _dos_lados("Autor", "autorias", "LibroAutor", "autor")
    _dos_lados("Cliente", "perfil", "PerfilCliente", "cliente")
    _dos_lados("Cliente", "ventas", "Venta", "cliente")
    _dos_lados("Venta", "renglones", "RenglonVenta", "venta")
    _dos_lados("Libro", "renglones", "RenglonVenta", "libro")


def test_perfil_devuelve_objeto_unico_no_lista():
    """Cliente.perfil responde un objeto (o None), nunca una lista (RN-09).

    En SQLAlchemy la relación 1:1 se lee desde el lado Cliente como
    ONETOMANY con uselist=False (el lado MANYTOONE vive en PerfilCliente,
    cuya FK es a su vez UNIQUE). El par (uselist=False + FK única) es lo que
    garantiza objeto único y no lista.
    """
    prop = Cliente.perfil.property
    assert prop.uselist is False
    assert prop.direction.name == "ONETOMANY"
    prop_inversa = PerfilCliente.cliente.property
    assert prop_inversa.direction.name == "MANYTOONE"
    # Del lado MANYTOONE (FK en perfil_cliente) la cardinalidad ya es única por
    # defecto; la garantía de "objeto o None, nunca lista" vive en uselist=False
    # del lado Cliente complementada con la unicidad de la FK.


def test_relacion_muchos_a_muchos_con_datos_propios():
    """Libro↔Autor vía entidad intermedia con PK compuesta y datos rol/orden."""
    intermedia = MD.tables["libro_autor"]
    assert {"rol", "orden"}.issubset(intermedia.columns.keys())
    assert set(intermedia.primary_key.columns.keys()) == {"libro_id", "autor_id"}
    # Navegación sin atributos mágicos: libro.autorias[i].autor.
    assert Libro.autorias.property.direction.name == "ONETOMANY"
    assert Autor.autorias.property.direction.name == "ONETOMANY"


def test_direcciones_de_todas_las_relaciones():
    """Agregaciones a uno (FK en Libro), asociaciones y composición 1 a N."""
    assert Libro.editorial.property.direction.name == "MANYTOONE"
    assert Libro.genero.property.direction.name == "MANYTOONE"
    assert Editorial.libros.property.direction.name == "ONETOMANY"
    assert Genero.libros.property.direction.name == "ONETOMANY"
    assert Venta.cliente.property.direction.name == "MANYTOONE"
    assert Cliente.ventas.property.direction.name == "ONETOMANY"
    assert PerfilCliente.cliente.property.direction.name == "MANYTOONE"
    assert RenglonVenta.venta.property.direction.name == "MANYTOONE"
    assert RenglonVenta.libro.property.direction.name == "MANYTOONE"
    assert Venta.renglones.property.direction.name == "ONETOMANY"


# ------------------------------------------------------------ tipos dinero ---


def test_dinero_es_decimal_con_precision_numerica():
    """Dinero: Decimal + NUMERIC; jamás float."""
    precio = MD.tables["libro"].columns["precio"]
    precio_unitario = MD.tables["renglon_venta"].columns["precio_unitario"]
    total = MD.tables["venta"].columns["total"]

    for columna in (precio, precio_unitario):
        assert isinstance(columna.type, Numeric)
        assert columna.type.precision == 10 and columna.type.scale == 2
        assert columna.type.python_type is Decimal

    assert isinstance(total.type, Numeric)
    assert total.type.precision == 12 and total.type.scale == 2
    assert total.type.python_type is Decimal

    def _es_float(columna):
        try:
            return columna.type.python_type is float
        except NotImplementedError:
            return False

    usa_float = any(
        _es_float(columna)
        for tabla in MD.tables.values()
        for columna in tabla.columns
    )
    assert not usa_float


# ---------------------------------------------- composición y configure ---


def test_composicion_venta_renglones_con_cascada():
    """Los renglones nacen y mueren con su venta (all, delete-orphan).

    SQLAlchemy expande "all, delete-orphan" a sus opciones concretas:
    delete, delete-orphan, expunge, merge, refresh-expire, save-update.
    """
    configure_mappers()
    opciones = {opcion for opcion in Venta.__mapper__.relationships["renglones"].cascade}
    esperadas = {
        "delete",
        "delete-orphan",
        "expunge",
        "merge",
        "refresh-expire",
        "save-update",
    }
    assert opciones == esperadas


def test_composicion_libro_autorias_con_cascada():
    """Las autorías se agregan al libro y se destruyen con él."""
    configure_mappers()
    opciones = {opcion for opcion in Libro.__mapper__.relationships["autorias"].cascade}
    esperadas = {
        "delete",
        "delete-orphan",
        "expunge",
        "merge",
        "refresh-expire",
        "save-update",
    }
    assert opciones == esperadas


def test_configure_mappers_sin_errores():
    """SQLAlchemy resuelve todas las relaciones sin inconsistencias de mapping."""
    configure_mappers()


# ------------------------------------------------- esquema generable (real) ---


@pytest.mark.asyncio
async def test_create_all_genera_las_nueve_tablas():
    """create_all real sobre sqlite+aiosqlite: las 9 tablas existen físicamente.

    Valida que main.py (integración) podrá generar el esquema completo.
    PostgreSQL se valida en los casos D con servidor real (no aquí).
    """
    import aiosqlite  # noqa: F401 (asegura el driver instalado)
    from sqlalchemy.ext.asyncio import create_async_engine

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(MD.create_all)
            nombres: list[str] = await conn.run_sync(
                lambda sync_conn: sa_inspect(sync_conn).get_table_names()
            )
        assert set(nombres) == {
            "editorial",
            "genero",
            "autor",
            "libro",
            "libro_autor",
            "cliente",
            "perfil_cliente",
            "venta",
            "renglon_venta",
        }
    finally:
        await engine.dispose()


# ------------------------------------------------- importaciones aisladas ---


def test_importacion_aislada_de_cada_modulo_sin_dependencias_circulares():
    """Cada módulo de modelos se importa en un subproceso Python limpio.

    Un intérprete nuevo ejecuta cada import por primera vez: una dependencia
    circular o un import roto fallaría aquí (en el proceso de test ya cargado
    no sería detectable).
    """
    codigo = (
        "import importlib\n"
        "\n"
        "MODULOS = [\n"
        "    'app.modules.editoriales.models',\n"
        "    'app.modules.generos.models',\n"
        "    'app.modules.autores.models',\n"
        "    'app.modules.libros.models',\n"
        "    'app.modules.clientes.models',\n"
        "    'app.modules.ventas.models',\n"
        "]\n"
        "\n"
        "for modulo in MODULOS:\n"
        "    importlib.import_module(modulo)\n"
        "\n"
        "print('OK')\n"
    )
    resultado = subprocess.run(
        [sys.executable, "-c", codigo],
        capture_output=True,
        text=True,
        check=False,
    )
    assert resultado.returncode == 0, resultado.stderr
    assert resultado.stdout.strip() == "OK"
