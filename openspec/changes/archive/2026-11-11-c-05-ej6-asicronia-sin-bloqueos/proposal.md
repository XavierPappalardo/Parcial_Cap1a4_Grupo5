# Proposal

## Why

El sistema requiere que todos los handlers sean `async def` y no ejecuten llamadas bloqueantes, de modo que el servidor siga atendiendo otras peticiones mientras operaciones como el aviso de comprobante de venta corren en segundo plano. La epica Ejercicio 6 (asincronía sin bloqueos) no está cubierta por ninguna capacidad existente, y el registro atómico de venta usa `BackgroundTasks` sin garantizar que el aviso sea verdaderamente no bloqueante.

## What Changes

- Verificar que todos los handlers de los módulos (autores, clientes, editoriales, generos, health, libros, ventas) son `async def` y no usan llamadas bloqueantes (`time.sleep`, `requests`, acceso síncrono a la base).
- Implementar `POST /ventas/` para agendar con `BackgroundTasks` el aviso del comprobante al cliente, simulado con `await asyncio.sleep(0.5)` y un mensaje en el log, que corre después de enviar la respuesta.
- Verificar que `verificar_readiness` y demás operaciones de DB sean asincrónicas.
- Marcar todas las consultas con carga anticipada explícita (`joinedload` para 1:1, `selectinload` para colecciones) para evitar N+1.

## Capabilities

### New Capabilities

- `asincronia-sin-bloqueos`: Garantiza que todos los handlers sean `async def` sin llamadas bloqueantes, que el aviso de comprobante de venta se ejecute en segundo plano vía `BackgroundTasks` sin bloquear la respuesta, y que las operaciones de DB (incluido `verificar_readiness`) sean asincrónicas.

### Modified Capabilities

- (none)

## Impact

- Código: `app/modules/ventas/router.py`, `app/modules/ventas/service.py`, `app/main.py`, `app/core/database.py`, `app/core/common.py`, y routers de los demás módulos para verificar `async def`.
- APIs: `POST /ventas/` (agenda comprobante en background), endpoints de salud (`verificar_readiness`).
- Dependencias: `BackgroundTasks` de FastAPI, `asyncio.sleep`, `asyncpg` / SQLAlchemy async.
- Sistemas: comportamiento del servidor bajo carga concurrente; ninguna tabla o columna cambia.
