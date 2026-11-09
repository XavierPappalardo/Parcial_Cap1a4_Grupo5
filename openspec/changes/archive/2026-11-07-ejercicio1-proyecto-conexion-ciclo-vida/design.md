# Design: Ejercicio 1 · Proyecto, conexión y ciclo de vida

## Context

Este cambio establece los cimientos del backend FastAPI 0.111+ para la librería de barrio, configurando el entorno de ejecución, la estructura modular de directorios obligatoria, el ciclo de vida asincrónico (lifespan) y la conexión a PostgreSQL con SQLAlchemy 2.0 y asyncpg.

Ver `proposal.md` para la motivación y `knowledge-base/08_arquitectura_propuesta.md` para la arquitectura modular de referencia.

## Goals / Non-Goals

**Goals:**
- Estructurar el proyecto bajo la arquitectura modular funcional: `app/main.py`, `app/core/config.py`, `app/core/database.py` y `app/modules/health/{router,service}.py`.
- Configuración tipada con `pydantic-settings` para cargar `DATABASE_URL` y `SQL_ECHO` desde `.env` y variables del sistema.
- Ciclo de vida asincrónico con `@asynccontextmanager async def lifespan(app: FastAPI)` en `app/main.py` que cree el `AsyncEngine` y el `async_sessionmaker` y los guarde en `app.state`.
- Creación de tablas al arrancar con `await conn.run_sync(SQLModel.metadata.create_all)` dentro del startup del lifespan.
- Cierre ordenado de conexiones en el shutdown mediante `await engine.dispose()`.
- Fábrica de sesiones con `expire_on_commit=False` y dependencia generadora asincrónica `get_session` para inyección en handlers vía `Depends()`.
- Endpoints de salud en `/health/live` (HTTP 200 `{"estado": "vivo"}`) y `/health/ready` (HTTP 200 ejecutando `SELECT 1`).
- Archivos de soporte: `env.example`, `requirements.txt` y `test/health.http`.

**Non-Goals:**
- Modelos de tabla de catálogo y ventas (corresponden al Ejercicio 2).
- Contratos DTO de negocio y endpoints de catálogo (corresponden a Ejercicios 3 y 4).
- Despliegue en VPS y Dockerfile (corresponden a Ejercicios 7 y 8).

## Decisions

### 1. Configuración tipada con Pydantic Settings
- **Decisión**: Utilizar `pydantic_settings.BaseSettings` en `app/core/config.py`.
- **Justificación**: Provee validación automática de tipos, soporte nativo para archivos `.env` y variables de entorno del sistema, y permite normalizar URLs de PostgreSQL para asegurar el esquema `postgresql+asyncpg://`.
- **Alternativa descartada**: `os.environ` directo o funciones ad-hoc sin validación de tipos ni valores por defecto claros.

### 2. Motor y Sesiones en `app.state` dentro de Lifespan
- **Decisión**: Inicializar `create_async_engine` y `async_sessionmaker` en el context manager `lifespan` de FastAPI, guardándolos en `app.state.engine` y `app.state.session_factory`.
- **Justificación**: Cumple estrictamente con la consigna de la cátedra (secciones 1.9 y 4.5). Asegura que el motor no sea un estado global inaccesible y garantiza la liberación del pool con `await engine.dispose()` al recibir `SIGINT` o `SIGTERM`.
- **Alternativa descartada**: Variables globales instanciadas al momento de importar módulos en `database.py`.

### 3. Dependencia `get_session` con `expire_on_commit=False`
- **Decisión**: Implementar `async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]` extrayendo la fábrica desde `request.app.state.session_factory`.
- **Justificación**: Cada petición HTTP recibe una sesión limpia que se cierra automáticamente en el bloque `finally` / context manager. `expire_on_commit=False` evita que los atributos de las entidades expiren al hacer `commit()`, facilitando su serialización posterior sin requerir lecturas diferidas no soportadas en async.

### 4. Creación de tablas mediante `conn.run_sync` en Lifespan
- **Decisión**: Ejecutar `await conn.run_sync(SQLModel.metadata.create_all)` dentro de un bloque `async with engine.begin() as conn:` al iniciar el lifespan.
- **Justificación**: `metadata.create_all` es una operación de DDL sincrónica que SQLAlchemy permite correr de forma segura dentro del loop asincrónico usando `run_sync`.

### 5. Arquitectura del Módulo Health
- **Decisión**: Crear `app/modules/health/service.py` con `verificar_liveness()` y `async def verificar_readiness(session: AsyncSession)` y exponerlos en `app/modules/health/router.py`.
- **Justificación**: Mantiene la separación de responsabilidades: el router se encarga de HTTP y el servicio ejecuta la lógica y la consulta `SELECT 1`.

## Risks / Trade-offs

- **Formato de `DATABASE_URL`** → *Riesgo*: Si el usuario o el servidor entrega `postgresql://` en vez de `postgresql+asyncpg://`, asyncpg fallará al inicializarse.  
  *Mitigación*: En `app/core/config.py`, un validador de Pydantic reemplaza automáticamente el esquema si es necesario.
- **Base de datos no disponible al arranque** → *Riesgo*: Si PostgreSQL no responde durante el lifespan, la aplicación fallará al iniciar.  
  *Mitigación*: Es el comportamiento deseado según la consigna: un contenedor que no alcanza su base de datos no debe quedar sirviendo tráfico.
- **Healthcheck en Alpine/Docker** → *Riesgo*: Futura verificación de Docker HEALTHCHECK.  
  *Mitigación*: Endpoint `/health/live` responde de forma inmediata en < 5ms sin tocar recursos externos.
