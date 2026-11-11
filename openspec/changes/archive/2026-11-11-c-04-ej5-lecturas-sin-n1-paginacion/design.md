# Design

## Context

Los módulos de lectura (`libros`, `ventas`, `editoriales`, `generos`, `autores`, `clientes`) ya existen con routers y servicios que usan `Depends(get_session)` y handlers `async def`. Las lecturas de detalle y catálogo no especifican estrategias de carga anticipada, por lo que el acceso a relaciones en Python dispara consultas perezosas (N+1) en async. La búsqueda por título (`GET /libros/?titulo=...`) y la paginación (`limit`/`offset`) ya están implementadas a nivel de router y servicio conforme a RN-11 y RN-10. No se modifican modelos de tabla ni se agregan columnas; solo las estrategias de carga en las consultas y los DTOs de respuesta.

## Goals / Non-Goals

**Goals:**
- Cada lectura detallada emita un número fijo de sentencias SQL verificable con `SQL_ECHO=true` (Caso C-07), sin consultas secundarias por entidad relacionada.
- `GET /libros/{id}` use `joinedload` (editorial, género) y `selectinload` (autorias → autor).
- `GET /ventas/{id}` use `joinedload` (cliente) y `selectinload` (renglones → libro).
- `GET /editoriales/{id}/libros`, `GET /generos/{id}/libros`, `GET /autores/{id}/libros` usen carga anticipada; el de autores incluya `rol` y `orden` de cada autoría.
- `GET /clientes/{id}` exponga `perfil` como objeto único (o `null`), nunca lista.
- `GET /clientes/{id}/ventas` devuelva historial con renglones precargados.
- `GET /libros/` busque por título case-insensitive con parámetros ligados (RN-11 / Caso C-08) y pagine con `limit`/`offset` (RN-10).

**Non-Goals:**
- Modificar modelos de tabla, añadir columnas o renombrar restricciones.
- Cambiar el comportamiento de paginación o búsqueda ya especificado en `api-referencia-contratos`.
- Agregar endpoints de escritura o modificar las altas existentes.

## Decisions

- **Estrategia de carga**: `joinedload` para relaciones a uno (editorial, género, cliente) y `selectinload` para colecciones (autorias → autor, renglones → libro, ventas). Justificación: evita productos cartesianos en colecciones grandes y mantiene un número fijo de queries. Alternativa considerada: `subqueryload`; descartada porque `selectinload` es más eficiente en SQLAlchemy async para colecciones.
- **Ausencia de `if exists`**: las lecturas usan `session.exec(statement).unique().first()` y devuelven 404 si no hay resultado, sin consulta previa de existencia. Alternativa: `exists()` + `get()`; descartada porque duplica viajes a la base.
- **Búsqueda segura**: `lower(libro.titulo).like(:param)` o `ilike` con bind parameter de SQLAlchemy, nunca concatenación de strings. Alternativa: `text()` con interpolación; descartada por RN-11 / prevención de inyección SQL.
- **DTOs de respuesta separados**: se reutilizan/extienden los `*Read` existentes con campos anidados (`editorial`, `genero`, `autorias`, `renglones`, etc.) para serializar las relaciones cargadas.

## Risks / Trade-offs

- [joinedload en relaciones a uno con libros muchos] → Puede generar filas duplicadas en el resultado crudo; mitigado con `.unique()` al extraer y serialización por DTO.
- [Carga de colecciones grandes] → `selectinload` emite una consulta adicional por colección pero evita N+1; aceptable dado el requisito de número fijo de sentencias.
- [Perfil 1 a 1 como objeto] → El schema debe exponer `perfil` como objeto opcional, no lista, para cumplir US-007; riesgo de serializar como lista si el Relationship no se configura correctamente; mitigado con back_populates y `from_attributes`.

## Open Questions

Ninguna.
