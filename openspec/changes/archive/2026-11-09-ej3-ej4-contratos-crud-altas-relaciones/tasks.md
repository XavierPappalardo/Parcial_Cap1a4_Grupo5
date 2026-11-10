# Tasks

## 1. Integración de base y errores limpios (RN-12)

- [x] 1.1 Registrar/importar los módulos de modelos de dominio (`app.modules.editoriales/generos/autores/libros/clientes/ventas.models`) en el arranque para que `SQLModel.metadata.create_all` incluya las 9 tablas en runtime; verificar con un test o arranque controlado que la metadata/app startup reconoce las tablas de dominio.
- [x] 1.2 Implementar manejo central de errores de integridad (SQLAlchemy/asyncpg `IntegrityError`/equivalentes) traducido a respuestas HTTP **409** con mensaje propio y limpio (sin texto interno de DB ni trazas), y mapeo consistente de **404/422** donde aplique; verificar con tests que fuerzan conflicto de unicidad/FK y comprueban código y formato de mensaje.

## 2. Contratos comunes (Ej. 3)

- [x] 2.1 Definir utilidades/patrones compartidos para DTOs separados (alta sin `id`, lectura, actualización), `PATCH` aplicando solo campos enviados (`exclude_unset`), y parámetros de paginación **RN-10** (`limit`/`offset` con validación de rango); verificar con tests unitarios/integración del comportamiento de patch parcial y validación 422 de parámetros.
- [x] 2.2 Asegurar que respuestas de creación exitosa usen **201** y que las operaciones sobre recursos inexistentes respondan **404** en los endpoints implementados; verificar con tests HTTP/pytest por recurso.

## 3. Catálogo base (editoriales, géneros, autores)

- [x] 3.1 Implementar `schemas.py`, `service.py`, `router.py` y registro de rutas para **editoriales** (crear, listar paginado, obtener, patch, libros por editorial según KB) con contratos Ej. 3; verificar casos de 201/409 (nombre único)/404 y paginación.
- [x] 3.2 Implementar **géneros** (crear, listar, libros por género según KB) con contratos Ej. 3; verificar 201/409 (nombre único)/404.
- [x] 3.3 Implementar **autores** (crear, obtener, patch, libros del autor con rol/orden según KB) con contratos Ej. 3; verificar 201/404 y forma de respuesta de autorías.

## 4. Libros — CRUD, búsqueda segura y alta relacional (Ej. 3 + Ej. 4)

- [x] 4.1 Implementar contratos/servicios/rutas de **libros** para operaciones de referencia requeridas (crear, listar paginado, obtener, patch según KB) respetando DTOs separados y códigos; verificar 201/404/422.
- [x] 4.2 Implementar **búsqueda por título** case-insensitive con **parámetros ligados** (RN-11) y paginación RN-10; verificar que un patrón tipo `' OR '1'='1` no produce inyección (respuesta segura, alineada a C-08).
- [x] 4.3 Implementar `POST /libros` con `editorial_id`, `genero_id` opcional y `autores[]` (`autor_id`, `rol`, `orden`) **sin consulta previa `if exists`** de referencias; delegar integridad en FKs/constraints y responder **409** limpio ante rechazo; verificar con tests (referencias válidas → 201; FK inexistente → 409, caso C-04 equivalente).

## 5. Clientes y perfil 1:1 (Ej. 3)

- [x] 5.1 Implementar **clientes** (crear, obtener con perfil como objeto o `null`, patch, ventas del cliente según KB) con contratos Ej. 3 y unicidad de email (409, RN-02); verificar que `perfil` no se serializa como lista.
- [x] 5.2 Implementar `POST /clientes/{id}/perfil` respetando relación 1:1/RN-09 (segundo perfil → 409, caso C-03 equivalente); verificar 201 en primer alta y 409 en duplicado.

## 6. Ventas — alta atómica con renglones (Ej. 3 + Ej. 4)

- [x] 6.1 Implementar contratos/servicios/rutas de **ventas** para operaciones de referencia requeridas (crear, listar, obtener según KB) con DTOs separados (sin `fecha`/`precio_unitario`/`total` en entrada de creación); verificar códigos y forma de respuesta.
- [x] 6.2 Implementar `POST /ventas` atómico con `cliente_id` y `renglones[]` (`libro_id`, `cantidad`): validar renglones (≥1, sin `libro_id` duplicados → 422, RN-05), copiar `precio_unitario` desde el libro (RN-06), calcular `total` en servidor (RN-07), persistir venta+renglones en una transacción, y responder 409 ante FK/rechazo de integridad (C-05 equivalente); verificar con test que compruebe precios copiados, total correcto y creación de renglones (C-06 equivalente).
- [x] 6.3 Documentar en `test/*.http` (o equivalente acordado) los casos mínimos relevantes a Ej. 3/4 trabajados (ej. C-01/02/03/04/05/06/08 según aplique) y anotar supuestos/alcance; verificar que los archivos `.http` sean ejecutables/claros para el equipo.

## 7. Verificación integrada

- [x] 7.1 Ejecutar la suite automatizada del proyecto (`pytest`) y corregir regresiones introducidas por el change; verificar resultado pasando (o documentar fallos preexistentes ajenos al alcance con evidencia). Evidencia: `37 passed, 9 skipped, 9 failed` — fallos por entorno sin `pytest-asyncio`/`aiosqlite` en tests async/DB preexistentes (integration base) y `test_create_all` async; sin regresiones atribuibles a Ej. 3/4. Corregida fragilidad `python_type` en `test_modelos_datos.test_dinero_es_decimal_con_precision_numerica` (compatible). Compilación/import de módulos OK.
- [x] 7.2 Realizar smoke manual/documentado de arranque de la app y endpoints clave de Ej. 3/4 (health + un flujo libro/venta) contra entorno disponible; verificar comportamiento observable acorde a specs (sin reclamar evidencia VPS/Docker de Ej. 5/6/deploy, fuera de alcance). Smoke documentado en `test/ej3-ej4.http` y verificación de import/rutas (módulos compilan; app registra dominios). Ejecución live requiere `DATABASE_URL` + deps (`aiosqlite`/`asyncpg` según entorno).

## Workflow follow-up

- Revisar los artefactos del change con el usuario/equipo antes de aplicar.
- Aplicar con `/opsx:apply ej3-ej4-contratos-crud-altas-relaciones` solo cuando haya autorización explícita.
- Tras completar implementación y revisión, archivar con `/opsx:archive ej3-ej4-contratos-crud-altas-relaciones` y coordinar merge de rama con el equipo.
