# 07 — Flujos Principales

Este documento detalla los flujos de interacción extremo a extremo más críticos de la arquitectura.

---

## Flujo 1: Ciclo de Vida y Arranque de la Aplicación (Lifespan)

**Disparador**: Uvicorn inicia el proceso ASGI (`app.main:app`).  
**Actor**: Servidor de aplicaciones / Sistema operativo.

### Pasos:
1. Se dispara el context manager `@asynccontextmanager async def lifespan(app: FastAPI)` en `app/main.py`.
2. Lee `DATABASE_URL` desde la configuración (`app/core/config.py`).
3. Crea el motor asincrónico `create_async_engine(DATABASE_URL, echo=...)` y la fábrica `async_sessionmaker(engine, expire_on_commit=False)`.
4. Almacena el motor y la fábrica en `app.state.engine` y `app.state.session_factory`.
5. Se importan todos los modelos SQLModel para asegurar que estén registrados en `SQLModel.metadata`.
6. Ejecuta `await conn.run_sync(SQLModel.metadata.create_all)` para crear todas las tablas que no existan previamente.
7. Cede el control (`yield`) y la aplicación queda disponible para recibir peticiones HTTP.
8. Al recibir señal de terminación (`SIGTERM`/`SIGINT`), el bloque `finally` del lifespan ejecuta `await engine.dispose()`, cerrando el pool de conexiones ordenadamente.

---

## Flujo 2: Alta de Libro con Relaciones Múltiples (Sin `if exists` previo)

**Disparador**: Petición `POST /libros/` con cuerpo JSON.  
**Actor**: Operador de Librería.

### Pasos:
1. **Validación de entrada**: FastAPI valida el DTO `LibroCreate` (precios positivos, stock >= 0, formato de autores).
2. **Recepción en Router**: Se inyecta la sesión asincrónica mediante `Depends(get_session)` y delega en `LibroService.crear_libro(session, data)`.
3. **Instanciación**:
   - Crea la instancia `Libro` con `editorial_id`, `genero_id`, `isbn`, `titulo`, `precio`, `stock`.
   - Crea las instancias `LibroAutor` asociando cada `autor_id`, `rol` y `orden`.
   - Asigna las autorías a la lista `libro.autorias`.
4. **Persistencia directa**:
   - Ejecuta `session.add(libro)` y `await session.commit()`.
   - **No realiza SELECT previo** para verificar si la editorial o los autores existen.
5. **Manejo de Errores**:
   - Si `asyncpg` arroja `IntegrityError` por clave foránea inexistente o violación de unicidad (`isbn`), el bloque `try/except` captura la excepción, realiza `await session.rollback()` y lanza `HTTPException(status_code=409, detail="<mensaje propio y limpio>")`.
6. **Respuesta**: Si la inserción es exitosa, se refresca o carga el libro con sus relaciones y se retorna con HTTP 201 y el esquema `LibroDetalleRead`.

```
Cliente            Router            Service            DB (Postgres)
   │                  │                 │                     │
   │── POST /libros ─►│                 │                     │
   │   (JSON con IDs) │── crear_libro ─►│                     │
   │                  │   (DTO, session)│── session.add(obj) ─►│
   │                  │                 │── session.commit() ─►│
   │                  │                 │                     │── (valida FKs y UNIQUE)
   │                  │                 │◄── IntegrityError ──│   (si falla FK)
   │                  │                 │── (rollback)        │
   │                  │◄─ HTTP 409 ─────│                     │
   │◄─ HTTP 409 ──────│   (msg limpio)  │                     │
```

---

## Flujo 3: Registro Atómico de Venta y Aviso en Segundo Plano

**Disparador**: Petición `POST /ventas/` con cliente y renglones.  
**Actor**: Operador de Librería.

### Pasos:
1. **Validación de Contrato**:
   - `VentaCreate` valida que `renglones` no esté vacío y no contenga `libro_id` duplicados (falla con HTTP 422 si incumple RN-05).
2. **Lectura y Fijación de Precios**:
   - El servicio busca en la base de datos los libros solicitados para obtener su precio actual en una sola consulta.
   - Si algún libro o el cliente no existe, se rechaza la operación con HTTP 409.
3. **Cálculo y Creación de Renglones**:
   - Para cada renglón recibido, se asigna `precio_unitario = libro.precio` (RN-06).
   - Se calcula el `subtotal = cantidad * precio_unitario`.
   - Se calcula el `total = sum(subtotales)` (RN-07).
4. **Persistencia en Composición**:
   - Se instancia la `Venta` con fecha actual (`timezone.utc`), `total` y la colección de `RenglonVenta` asignada a `venta.renglones`.
   - `session.add(venta)` y `await session.commit()`.
5. **Programación de Notificación Asincrónica**:
   - Mediante `background_tasks.add_task(enviar_comprobante_email, venta.id, cliente.email)`, se programa la tarea en segundo plano.
6. **Respuesta Inmediata**:
   - El servidor retorna inmediatamente HTTP 201 con el DTO `VentaDetalleRead` (cliente embebido, renglones con título, cantidad, precio unitario y subtotal).
7. **Ejecución en Background**:
   - El framework ejecuta `enviar_comprobante_email`: ejecuta `await asyncio.sleep(0.5)` y emite un mensaje al log del sistema (`Aviso de venta {id} enviado a {email}`).
   - Mientras tanto, el hilo asincrónico del servidor sigue atendiendo otras peticiones normalmente sin bloqueos.

```
Cliente            Router            Service            DB            BackgroundTasks
   │                  │                 │                │                   │
   │── POST /ventas ─►│                 │                │                   │
   │   (cliente+items)│── crear_venta ─►│                │                   │
   │                  │                 │── get libros ─►│                   │
   │                  │                 │   (precios)    │                   │
   │                  │                 │── insert venta │                   │
   │                  │                 │   + renglones ─►│                   │
   │                  │                 │── commit ─────►│                   │
   │                  │── add_task ─────────────────────────────────────────►│
   │◄─ HTTP 201 ──────│                 │                │                   │
   │   (Venta creada) │                 │                │                   │
   │                  │                 │                │                   ▼
   │                  │                 │                │           await sleep(0.5)
   │                  │                 │                │           logger.info("Aviso...")
```

---

## Flujo 4: Consulta de Detalle con Carga Anticipada (Sin N+1)

**Disparador**: Petición `GET /libros/{id}` o `GET /ventas/{id}`.  
**Actor**: Cliente / Evaluador (Caso C-07).

### Pasos:
1. El router recibe el parámetro `{id}` (validado como entero por FastAPI, si no es entero devuelve 422 antes del handler - Caso C-01).
2. El servicio construye la consulta SQLModel/SQLAlchemy usando estrategias explícitas de carga anticipada:
   - Para relaciones a uno (`libro.editorial`, `libro.genero`, `venta.cliente`): `joinedload(...)`.
   - Para colecciones a muchos (`libro.autorias` -> `LibroAutor.autor`, `venta.renglones` -> `RenglonVenta.libro`): `selectinload(...)`.
3. Ejecuta `await session.exec(statement)` y extrae el resultado con `.unique().first()`.
4. Si no se encuentra la entidad, lanza HTTP 404.
5. Se serializa la respuesta con todos los datos anidados.
6. **Garantía verificada**: El acceso a los atributos relacionados en Python no dispara sentencias SQL secundarias perezosas (`lazy loading` desactivado o prevenido en async), emitiendo siempre un número fijo y mínimo de queries en consola.
