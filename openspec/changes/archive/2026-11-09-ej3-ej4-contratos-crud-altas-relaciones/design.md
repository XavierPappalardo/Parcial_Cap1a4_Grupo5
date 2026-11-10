# Design

## Context

Ver `proposal.md` (Why/What). El repo ya implementa Ej. 1 (`app/main.py` lifespan + `app.state` + `get_session` con `expire_on_commit=False`, `app/core/*`, `app/modules/health`) y Ej. 2 (modelos de tabla y relaciones en `app/modules/*/models.py`, con `tests/test_modelos_datos.py`). Faltan los contratos HTTP y la lógica de negocio de Ej. 3 y 4. Restricciones duras: `Decimal/NUMERIC` para dinero, nombres de tablas/columnas exactos (`knowledge-base/04_modelo_de_datos.md`), índices en FKs, sin `float`, sin pre-check `if exists` para validar relaciones en altas donde aplique la consigna, `IntegrityError` → 409 limpio (RN-12), handlers `async def`, estructura modular `app/modules/<dominio>/`.

## Goals / Non-Goals

**Goals:**
- Entregar Ej. 3 y 4: DTOs separados, CRUD/contratos de endpoints de referencia, códigos 201/404/409/422, `PATCH` con `exclude_unset`, paginación RN-10, búsqueda por título con parámetros ligados RN-11.
- Implementar altas relacionales: `POST /libros` con `editorial_id`/`genero_id`/`autores[]` sin consulta previa de existencia; `POST /ventas` con `cliente_id`/`renglones[]`, copia de `precio_unitario` desde libro y `total` calculado por servidor (RN-04–RN-07), persistencia atómica de venta+renglones.
- Asegurar integración de arranque importando modelos de dominio para `create_all` en runtime.

**Non-Goals:**
- Ej. 5 como entregable formal (auditoría/corrección exhaustiva de N+1 en todas las lecturas con evidencia C-07) y Ej. 6 (BackgroundTasks/comprobante post-venta).
- Dockerfile, `DEPLOY.md`, `evidencia/D-*`, seed completo, y merge final a `main` (equipo).
- Cambiar nombres de tablas/columnas/modelos del Ej. 2 salvo corrección estrictamente necesaria y alineada a KB.

## Decisions

1. **Arquitectura modular por dominio**: `app/modules/<dominio>/{models.py,schemas.py,service.py,router.py}`. Reusar `models.py` existentes del Ej. 2. *Alternativa*: capa única/routers planos — descartada por consigna/KB (`08_arquitectura_propuesta.md`).
2. **DTOs con SQLModel/Pydantic**: esquemas `*Create` (sin `id`), `*Read` (incluye `id` y relaciones anidadas donde corresponda), `*Update` (campos opcionales). En `PATCH`, construir dict con `model_dump(exclude_unset=True)` y aplicar solo campos presentes. *Alternativa*: reutilizar modelos de tabla como contratos — descartada por Ej. 3.
3. **Manejo de integridad y 409 limpio (RN-12)**: capturar errores de integridad de SQLAlchemy/asyncpg en un punto común (handler de excepción en `app/main.py` y/o helper en `app/core/`) y traducir a respuesta JSON propia (sin trazas ni texto interno de Postgres). Mapear unicidad/FK a 409; 404 para inexistencia de recurso consultado por ruta. *Alternativa*: `try/except` ad-hoc en cada endpoint — mayor duplicación y riesgo de filtrar detalles.
4. **Altas con relaciones sin pre-check (libro)**: en `POST /libros`, construir `Libro` y `LibroAutor` y persistir en la misma transacción; no ejecutar `SELECT` previo para validar `editorial_id/genero_id/autor_id`. Si la DB rechaza FK/constraint, responder 409. Para venta, consultar libros necesarios para obtener `precio` actual y validar reglas de renglones (RN-05) como parte de la lógica de negocio, pero no sustituir la integridad referencial por `if exists` como patrón; la FK sigue siendo garante ante referencias inválidas → 409.
5. **Venta atómica (RN-04–RN-07)**: en una transacción de servicio, cargar precios de libros referenciados, validar renglones (≥1, sin `libro_id` duplicados → 422 RN-05), crear `Venta` y `RenglonVenta` con `precio_unitario` copiado del libro y `total = sum(cantidad * precio_unitario)` calculado en servidor. Persistir en conjunto (composición). No aceptar `fecha`, `precio_unitario` ni `total` desde el cliente.
6. **Paginación y búsqueda**: `limit`/`offset` según RN-10 en listados. Búsqueda por título en `GET /libros` case-insensitive usando predicados parametrizados del ORM (`ilike`/equivalente con binding), nunca concatenación SQL.
7. **Registro de modelos en startup**: en `app/main.py` (o módulo de registro), importar módulos de modelos de dominio antes de/durante el contexto de `create_all` para que la metadata incluya las 9 tablas. Mantener compatibilidad con lifespan existente.
8. **Async y sesiones**: todos los handlers/servicios de I/O como `async def`, usando `AsyncSession` vía `Depends(get_session)`. No llamadas bloqueantes. (BackgroundTasks de venta es Ej. 6, fuera de alcance.)

## Risks / Trade-offs

- [Desalineación con contratos exactos de la KB/endpoints de referencia] → Mitigar leyendo `02/03/04/06/11` al implementar y cubriendo rutas/campos esperados en tests `.http`/pytest.
- [Mapeo incompleto de `IntegrityError` filtra detalles] → Mitigar con handler central + mensajes genéricos propios; nunca retornar `str(exc.orig)` al cliente.
- [Consultas de venta para obtener precios + composición con Ej. 5] → Obtener precios es necesario para RN-06; implementar de forma explícita/eficiente. Lecturas N+1 exhaustivas quedan para Ej. 5, pero evitar patrones obviamente ineficientes.
- [Cambios concurrentes por compañeros en ramas] → Mantener alcance acotado a módulos/schemas/routers/servicios y `main.py`; coordinar merge.
- [Scope amplio de “endpoints de referencia”] → Priorizar cobertura fiel a KB; si algún endpoint no es imprescindible para 3–4, documentar en tareas como asumido/pendiente de equipo.

## Migration Plan

- Sin migraciones Alembic (fuera de alcance). `create_all` crea tablas faltantes al arranque.
- Despliegue/rollback operativo (Docker/VPS) fuera de este change; a nivel de código, rollback es revertir el change/rama.
- Tras aplicar: ejecutar tests automatizados y, si hay DB disponible, smoke con `test/*.http`.

## Open Questions

- Ninguna que bloquee el diseño: los detalles finos de campos de respuesta anidados por recurso se resolverán siguiendo `knowledge-base/04_modelo_de_datos.md` y `06_funcionalidades.md` durante la implementación, sin cambiar el comportamiento contractual de Ej. 3/4.
