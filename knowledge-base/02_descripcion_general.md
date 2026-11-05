# 02 — Descripción General

## Stack tecnológico

| Capa / Componente | Tecnología | Versión mínima | Uso / Justificación |
|---|---|---|---|
| **Lenguaje** | Python | 3.12 | Tipado moderno, async nativo, rendimiento mejorado. |
| **Framework Web** | FastAPI | 0.111+ | Endpoints asincrónicos (`async def`), inyección de dependencias `Depends()`, validación Pydantic v2. |
| **ORM / Modelado** | SQLModel | 0.0.24+ | Fusión de Pydantic y SQLAlchemy para modelos de tabla y contratos DTO. |
| **Motor DB & Sesión** | SQLAlchemy | 2.0+ (async) | Conexión asincrónica, `AsyncSession`, control fino de carga anticipada (`joinedload`, `selectinload`). |
| **Driver de DB** | asyncpg | 0.30+ | Driver asincrónico de alto rendimiento para PostgreSQL. |
| **Base de datos** | PostgreSQL | 16 | Servidor relacional provisto por el entorno/VPS. |
| **Servidor ASGI** | Uvicorn | Estándar (`fastapi[standard]`) | Ejecución ASGI con soporte HTTP/1.1 y WebSockets. |
| **Gestión de Entorno** | python-dotenv | 1.0+ | Carga de variables de entorno desde `.env` en desarrollo local. |
| **Contenedor** | Docker | 20.10+ | Empaquetado y aislamiento con imagen base `python:3.12-alpine` (< 100 MB). |

## Arquitectura general

La arquitectura sigue una organización **modular funcional** estricta (`package by feature`), donde cada dominio de negocio está contenido en su propio módulo bajo `app/modules/<nombre_modulo>/`.

```
                        [ Cliente HTTP / Evaluador / VPS ]
                                       │
                                       ▼ (HTTP / JSON)
                          ┌──────────────────────────┐
                          │   FastAPI (app/main.py)  │
                          │   Lifespan & Middlewares │
                          └────────────┬─────────────┘
                                       │ Rutas
                    ┌──────────────────┴──────────────────┐
                    ▼                                     ▼
        ┌───────────────────────┐             ┌───────────────────────┐
        │  Módulo de Catálogo   │             │   Módulo de Ventas    │
        │  (libros, autores...) │             │   (ventas, clientes)  │
        ├───────────────────────┤             ├───────────────────────┤
        │  router.py  (HTTP)    │             │  router.py  (HTTP)    │
        │  schemas.py (DTOs)    │             │  schemas.py (DTOs)    │
        │  service.py (Lógica)  │             │  service.py (Lógica)  │
        │  models.py  (Tablas)  │             │  models.py  (Tablas)  │
        └───────────┬───────────┘             └───────────┬───────────┘
                    │                                     │
                    └──────────────────┬──────────────────┘
                                       │ Depends(get_session)
                                       ▼
                          ┌──────────────────────────┐
                          │  SQLAlchemy AsyncSession │
                          │     (app/core/database)  │
                          └────────────┬─────────────┘
                                       │ asyncpg
                                       ▼
                          ┌──────────────────────────┐
                          │ PostgreSQL 16 (Servidor) │
                          └──────────────────────────┘
```

### Justificaciones de diseño:
1. **Sin repositorio ni Unit of Work**: La lógica vive en el `service.py` de cada módulo recibiendo la sesión `AsyncSession` directamente, simplificando la traza y respetando la directiva de la cátedra para este parcial.
2. **Ciclo de vida (Lifespan)**: El motor y la fábrica de sesiones se crean una sola vez en el startup de la aplicación, guardándose en `app.state`, y se liberan de forma segura en el shutdown.
3. **Manejo de transacciones y sesiones**: `expire_on_commit=False` evita que los atributos de las instancias expiren tras el commit, permitiendo serializar respuestas sin disparar accesos síncronos no deseados.

## Integraciones externas

| Servicio | Propósito | Tipo de integración |
|---|---|---|
| **PostgreSQL 16 (VPS)** | Persistencia de datos relacionales | Conexión TCP asincrónica mediante driver `postgresql+asyncpg` usando `DATABASE_URL`. |
| **BackgroundTasks (FastAPI)** | Envío asincrónico simulado de comprobante de venta | Cola de eventos en memoria del proceso ASGI (`asyncio.sleep(0.5)` y registro en log). |

## Resumen de endpoints principales

| Recurso | Endpoints | Descripción |
|---|---|---|
| `/health` | `GET /live`, `GET /ready` | Monitoreo de liveness y readiness (SELECT 1). |
| `/editoriales` | `POST /`, `GET /`, `GET /{id}`, `PATCH /{id}`, `GET /{id}/libros` | CRUD de editoriales y libros asociados. |
| `/generos` | `POST /`, `GET /`, `GET /{id}/libros` | Catálogo de géneros literarios y consulta de libros. |
| `/autores` | `POST /`, `GET /{id}`, `PATCH /{id}`, `GET /{id}/libros` | Registro de autores y consulta de obras con rol y orden. |
| `/libros` | `POST /`, `GET /`, `GET /{id}`, `PATCH /{id}` | Catálogo de libros con autores, editorial y género precargados. |
| `/clientes` | `POST /`, `GET /{id}`, `PATCH /{id}`, `POST /{id}/perfil`, `GET /{id}/ventas` | Gestión de clientes, perfil único de contacto y ventas asociadas. |
| `/ventas` | `POST /`, `GET /`, `GET /{id}` | Registro atómico de ventas con renglones, cálculo de total y consulta con relaciones. |
