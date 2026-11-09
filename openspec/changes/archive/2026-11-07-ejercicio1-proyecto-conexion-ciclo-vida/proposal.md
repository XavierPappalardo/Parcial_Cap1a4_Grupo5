# Proposal

## Why

Para iniciar el proyecto del parcial conforme a las consignas de la cátedra (Unidades 1 a 4 de Programación III UTN), se necesita establecer la estructura modular obligatoria, la configuración del entorno, la infraestructura de conexión asincrónica a PostgreSQL en el ciclo de vida (lifespan) de FastAPI y los endpoints de monitoreo de salud (`/health/live` y `/health/ready`). Esto sienta la base arquitectónica sin bloqueos sobre la cual se montarán los modelos de datos, endpoints de catálogo y ventas en los ejercicios siguientes.

## What Changes

- Creación de la estructura base del proyecto: `app/main.py`, `app/core/config.py`, `app/core/database.py`, `app/modules/health/{router,service}.py`.
- Configuración de variables de entorno con `python-dotenv` / `pydantic-settings` para `DATABASE_URL` y `SQL_ECHO`, incluyendo plantilla `env.example` y dependencias en `requirements.txt`.
- Inicialización asincrónica de SQLAlchemy (`create_async_engine` y `async_sessionmaker`) dentro del lifespan de FastAPI, almacenados en `app.state`, garantizando `expire_on_commit=False` y cierre ordenado del pool al apagar (`engine.dispose()`).
- Creación automática de tablas mediante `SQLModel.metadata.create_all` dentro del lifespan al arrancar.
- Dependencia `get_session` para inyección de `AsyncSession` con `Depends()`.
- Endpoints de salud:
  - `GET /health/live`: responde `{"estado": "vivo"}` con HTTP 200 sin tocar la base de datos.
  - `GET /health/ready`: ejecuta `SELECT 1` sobre la base de datos asincrónica y responde HTTP 200 con el estado de la base.
- Archivo de pruebas HTTP en `test/health.http`.

## Capabilities

### New Capabilities
- `health-and-lifecycle`: Monitoreo de liveness y readiness (`/health/live`, `/health/ready`), inicialización del motor asincrónico y ciclo de vida de la aplicación.

### Modified Capabilities
*(Ninguna; es el primer change del proyecto)*

## Impact
- **Código y APIs**: Nueva aplicación FastAPI con router de salud montado en `/health`, módulos centrales en `app/core/` y lifespan en `app/main.py`.
- **Dependencias**: `fastapi[standard]`, `sqlmodel`, `sqlalchemy`, `asyncpg`, `python-dotenv`, `pydantic-settings`.
- **Entorno**: Archivos `.env` (no versionado) y `env.example`. Pruebas en `test/health.http`.
