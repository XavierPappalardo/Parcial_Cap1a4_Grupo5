# Tasks

## 1. Auditoria de asincronia (verificacion de estado actual)

- [x] 1.1 Confirmar que todos los handlers de los routers (autores, clientes, editoriales, generos, health, libros, ventas) son `async def` y no invocan llamadas bloqueantes (`time.sleep`, `requests`, acceso sincronico a la base) — Verificar inspeccionando `app/modules/*/router.py`; cada handler esta definido con `async def` y ninguno llama a funciones bloqueantes.
- [x] 1.2 Confirmar que `verificar_readiness` es asincronica — Verificar `app/modules/health/service.py:12` esta definido con `async def` y usa `await session.execute`.

## 2. Implementar aviso de comprobante en segundo plano en POST /ventas/

- [x] 2.1 Agregar `BackgroundTasks` como parametro del handler `crear` en `app/modules/ventas/router.py` — Verificar que la firma del endpoint incluye `background_tasks: BackgroundTasks` de `fastapi`.
- [x] 2.2 Crear la funcion `enviar_aviso_comprobante` que simula el envio con `await asyncio.sleep(0.5)` y registra un mensaje en el log — Verificar que la función existe, usa `asyncio.sleep(0.5)` y hace `logging.info`.
- [x] 2.3 Agendar `enviar_aviso_comprobante` con `background_tasks.add_task(...)` tras registrar la venta y antes de retornar la respuesta — Verificar que `POST /ventas/` devuelve la respuesta sin esperar el aviso y el aviso se ejecuta despues en segundo plano.

## 3. Verificacion de carga anticipada (sin N+1)

- [x] 3.1 Confirmar que las lecturas con relaciones usan `joinedload` (relaciones a uno) y `selectinload` (colecciones) — Verificar `app/modules/ventas/service.py:_query_venta_detalle` combina ambas opciones de carga.

## 4. Prueba de comportamiento de no-bloqueo

- [x] 4.1 Ejecutar `POST /ventas/` y verificar que la respuesta llega antes del aviso de comprobante y que el servidor sigue atendiendo `/health/ready` mientras el aviso corre — Verificar con un cliente HTTP (`.http` o curl) que la respuesta de venta retorna inmediata, el log muestra el aviso despues de la respuesta, y `/health/ready` responde mientras el aviso esta en curso.

## Workflow follow-up

- Ejecutar `openspec status --change c-05-ej6-asicronia-sin-bloqueos` para confirmar que todos los artefatos de planificacion esten `done`.
- Archivar el cambio con `/opsx:archive` una vez satisfechos los requisitos de revision del proyecto.
