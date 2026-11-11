# Tasks

## 1. Libros: detalle y listado con carga anticipada

- [x] 1.1 Actualizar `app/modules/libros/service.py` obtener() con joinedload (editorial, género) y selectinload (autorias → autor); verificar que devuelve 404 si no existe y serializa relaciones anidadas
- [x] 1.2 Actualizar `app/modules/libros/service.py` listar() con búsqueda por título case-insensitive usando parámetros ligados (ilike/lower().like()) y paginación limit/offset (RN-10/RN-11); verificar prevención de inyección SQL (Caso C-08)
- [x] 1.3 Verificar esquemas `app/modules/libros/schemas.py` expongan editorial, género y autorías con rol/orden para serializar relaciones cargadas

## 2. Ventas: detalle con carga anticipada

- [x] 2.1 Actualizar `app/modules/ventas/service.py` obtener() con joinedload (cliente) y selectinload (renglones → libro); verificar 404 si no existe y serialización anidada

## 3. Editoriales y Géneros: listado de libros con carga anticipada

- [x] 3.1 Actualizar `app/modules/editoriales/service.py` y router GET /editoriales/{id}/libros con carga anticipada de libros; verificar 404 si la editorial no existe
- [x] 3.2 Actualizar `app/modules/generos/service.py` y router GET /generos/{id}/libros con carga anticipada de libros; verificar 404 si el género no existe

## 4. Autores: libros con rol y orden de cada autoría

- [x] 4.1 Actualizar `app/modules/autores/service.py` y router GET /autores/{id}/libros para incluir rol y orden de cada autoría; verificar 404 si el autor no existe

## 5. Clientes: perfil como objeto único y ventas con renglones

- [x] 5.1 Actualizar `app/modules/clientes/service.py` GET /clientes/{id} para exponer perfil como objeto único (o null), nunca lista; verificar 404 si no existe
- [x] 5.2 Actualizar `app/modules/clientes/service.py` GET /clientes/{id}/ventas con historial y renglones precargados; verificar lista vacía si no hay ventas y 404 si el cliente no existe

## 6. Verificación de rendimiento y seguridad

- [x] 6.1 Ejecutar lecturas con SQL_ECHO=true y confirmar número fijo de sentencias SQL independiente de la cantidad de autores/renglones (Caso C-07) — verificado con echo=True (SQLite): 2 SELECT fijos para libros/ventas independientemente de autores/renglones; pendiente validación en PostgreSQL real
- [x] 6.2 Confirmar que GET /libros/?titulo=... usa parámetros ligados y no ejecuta inyección SQL (Caso C-08)

## Workflow follow-up

- Run lint/typecheck and tests before archive.
- Archive the change after review requirements are satisfied.
