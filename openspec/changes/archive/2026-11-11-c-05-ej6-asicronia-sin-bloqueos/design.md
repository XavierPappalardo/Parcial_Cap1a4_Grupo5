# Design

## Context

La aplicación ya cuenta con handlers definidos en `async def` sobre FastAPI/SQLAlchemy async (asyncpg) y una sesión por request mediante `Depends(get_session)` con `app.state.engine` y `app.state.session_factory` creadas en el lifespan (`app/main.py`, `app/core/database.py`). El registro atómico de venta existe (`app/modules/ventas/service.py` y `app/modules/ventas/router.py`), pero no se garantiza que el aviso del comprobante se envíe en segundo plano sin bloquear la respuesta, ni que todas las operaciones de DB (incluido `verificar_readiness`) sean asincrónicas. Véase `proposal.md` (Why) y `specs/asincronia-sin-bloqueos/spec.md` para los requisitos.

## Goals / Non-Goals

**Goals:**
- Todos los handlers de los módulos (autores, clientes, editoriales, generos, health, libros, ventas) sean `async def` sin llamadas bloqueantes.
- `POST /ventas/` agende el aviso de comprobante con `BackgroundTasks` (`await asyncio.sleep(0.5)` + log) que corra después de enviar la respuesta.
- El servidor siga atendiendo otras peticiones mientras corre el aviso en segundo plano.
- `verificar_readiness` y el resto de operaciones de DB sean asincrónicas, con carga anticipada explícita (`joinedload` 1:1, `selectinload` colecciones).

**Non-Goals:**
- Cambiar el modelo de datos (no se crean ni se eliminan tablas ni columnas).
- Introducir nuevas dependencias externas.
- Modificar el esquema de respuestas de los endpoints existentes.

## Decisions

- **Usar `BackgroundTasks` de FastAPI para el aviso del comprobante** en `POST /ventas/` en lugar de un hilo o tarea bloqueante: `BackgroundTasks` se ejecuta tras enviar la respuesta y no bloquea el event loop; el aviso se simula con `await asyncio.sleep(0.5)` y un mensaje de log. Alternativa considerada: `asyncio.create_task` directamente, desestimada porque `BackgroundTasks` es el patrón idiomático de FastAPI y se integra con el ciclo de vida de la request.
- **Mantener una sesión asincrónica por request** vía `Depends(get_session)` y `expire_on_commit=False`, sin `if exists` antes de persistir; se capturan `IntegrityError` y se responde HTTP 409 con mensaje limpio (RN-12).
- **Carga anticipada explícita** en todas las lecturas con relaciones: `joinedload` para relaciones a uno y `selectinload` para colecciones, evitando N+1 y carga perezosa.

## Risks / Trade-offs

- [El aviso en segundo plano puede fallar silenciosamente si el servidor se detiene antes de completarlo] → Mitigación: registrar en log el envío; el comprobante es informativo y no afecta la consistencia de la venta ya registrada.
- [Si algún handler olvidado usa una llamada bloqueante, el event loop se bloquea para todas las peticiones] → Mitigación: revisar todos los routers de módulos para confirmar `async def` y ausencia de bloqueos.

## Migration Plan

- Desplegar el cambio sin migración de base de datos (no hay cambios de esquema).
- Rollback: revertir el código a la versión anterior; no hay datos nuevos que migrar.

## Open Questions

Ninguna.
