# Proposal

## Why

Los endpoints de lectura de detalle y catálogo no cargan sus relaciones de forma anticipada, lo que dispara consultas perezosas (N+1) al acceder a los datos relacionados y degrada el rendimiento. El ejercicio 5 exige que todas las lecturas relacionales usen carga anticipada (`joinedload`/`selectinload`) con un número fijo de sentencias SQL, verificable con `SQL_ECHO=true` (Caso C-07), además de búsqueda por título segura y paginación estándar.

## What Changes

- Agregar capacidad de lecturas sin N+1 para los endpoints de detalle y catálogo:
  - `GET /libros/{id}`: `joinedload` (editorial, género) + `selectinload` (autorias → autor)
  - `GET /ventas/{id}`: `joinedload` (cliente) + `selectinload` (renglones → libro)
  - `GET /editoriales/{id}/libros`, `GET /generos/{id}/libros`, `GET /autores/{id}/libros`: carga anticipada de libros relacionados
  - `GET /clientes/{id}`: perfil como objeto único (no lista)
  - `GET /clientes/{id}/ventas`: historial de ventas con renglones precargados
- `GET /libros/`: búsqueda por título case-insensitive con parámetros ligados (RN-11) y paginación `limit`/`offset` (RN-10)
- Verificar número fijo de sentencias SQL con `SQL_ECHO=true` (Caso C-07) y prevención de inyección SQL (Caso C-08)

## Capabilities

### New Capabilities

- `lecturas-sin-n1`: Lecturas de detalle y catálogo con carga anticipada (cero N+1), búsqueda de libros por título case-insensitive con parámetros ligados y paginación estándar `limit`/`offset`.

### Modified Capabilities

- (ninguna): la paginación (RN-10) y la búsqueda de libros por título con parámetros ligados (RN-11) ya están especificadas en `api-referencia-contratos` y sus requisitos de comportamiento no cambian en este change.

## Impact

- `app/modules/libros/service.py` y `router.py`: detalle y listado con carga anticipada y búsqueda paginada.
- `app/modules/ventas/service.py` y `router.py`: detalle de venta con cliente y renglones precargados.
- `app/modules/editoriales/service.py` y `router.py`: listado de libros de una editorial con carga anticipada.
- `app/modules/generos/service.py` y `router.py`: listado de libros de un género con carga anticipada.
- `app/modules/autores/service.py` y `router.py`: listado de libros de un autor incluyendo `rol` y `orden` de cada autoría.
- `app/modules/clientes/service.py` y `router.py`: perfil como objeto único y ventas del cliente con renglones precargados.
- Esquemas de lectura (`schemas.py`) de cada módulo pueden requerir campos anidados para serializar relaciones cargadas.
- No se modifican modelos de tabla ni se agregan columnas; solo estrategias de carga en consultas y DTOs de respuesta.
