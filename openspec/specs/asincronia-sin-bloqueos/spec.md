# Asincronia Sin Bloqueos Specification

## Purpose

Garantiza que todos los handlers de la aplicación sean asincrónicos sin llamadas bloqueantes, y que operaciones de larga duración como el aviso del comprobante de venta se ejecuten en segundo plano sin impedir que el servidor atienda otras peticiones.

## Requirements

### Requirement: Handlers asincronos sin bloqueos

Todos los handlers HTTP de la aplicación SHALL estar definidos con `async def` y no SHALL ejecutar llamadas bloqueantes como `time.sleep`, clientes HTTP síncronos o acceso síncrono a la base de datos, de modo que el event loop no se bloquee.

#### Scenario: Handler es async def

- **WHEN** se inspecciona cualquier handler de ruta de los módulos autores, clientes, editoriales, generos, health, libros o ventas
- **THEN** la función está definida con `async def`

#### Scenario: No hay llamadas bloqueantes en handlers

- **WHEN** se ejecuta un handler de cualquier módulo
- **THEN** no se invoca `time.sleep`, `requests.get`/`requests.post` ni sesiones síncronas de SQLAlchemy dentro del handler

### Requirement: Aviso de comprobante en segundo plano

El registro de una venta SHALL agendar el envío del aviso de comprobante al cliente mediante `BackgroundTasks` de FastAPI, y el aviso SHALL correr después de que la respuesta HTTP se envíe al cliente, simulado con `await asyncio.sleep(0.5)` y un registro en el log.

#### Scenario: Comprobante se avisa tras la respuesta

- **WHEN** se realiza `POST /ventas/` con datos válidos
- **THEN** la respuesta HTTP se devuelve sin esperar el aviso, y el aviso del comprobante se ejecuta después en segundo plano con `await asyncio.sleep(0.5)` y un mensaje de log

### Requirement: Servidor atiende peticiones durante el aviso

Mientras el aviso de comprobante se ejecuta en segundo plano, el servidor SHALL seguir atendiendo otras peticiones entrantes sin bloqueos.

#### Scenario: Otras peticiones no se bloquean durante el aviso

- **WHEN** el aviso de comprobante de una venta está corriendo en segundo plano
- **THEN** el servidor puede atender simultáneamente otras peticiones (por ejemplo consultas de salud o de libros) sin esperar a que termine el aviso

### Requirement: Operaciones de base de datos asincronicas

Toda operación de base de datos, incluida `verificar_readiness` y las consultas de lectura y escritura, SHALL ser asincrónica mediante SQLAlchemy async / asyncpg, usando `joinedload` para relaciones a uno y `selectinload` para colecciones, para evitar consultas N+1.

#### Scenario: verificar_readiness es asincronica

- **WHEN** se invoca el endpoint de salud que verifica la disponibilidad de la base de datos
- **THEN** la operación de verificación se ejecuta de forma asincrónica sin bloquear el event loop

#### Scenario: Lecturas usan carga anticipada

- **WHEN** se lee un recurso con relaciones (por ejemplo libro con autores o venta con renglones)
- **THEN** la consulta precarga explícitamente las relaciones con `joinedload` (1:1) o `selectinload` (colecciones)
