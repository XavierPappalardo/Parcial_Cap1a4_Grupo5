# Tasks

## 1. Configuración de Entorno y Dependencias

- [x] 1.1 Crear `requirements.txt` fijando versiones mínimas del stack (`fastapi[standard]>=0.111.0`, `sqlmodel>=0.0.24`, `sqlalchemy>=2.0.0`, `asyncpg>=0.30.0`, `pydantic-settings>=2.0.0`, `python-dotenv>=1.0.0`, `pytest>=8.0.0`, `pytest-asyncio>=0.23.0`, `httpx>=0.27.0`) y verificar archivo creado.
- [x] 1.2 Crear `env.example` con la plantilla de variables requeridas (`DATABASE_URL`, `SQL_ECHO`) sin valores reales y verificar formato.
- [x] 1.3 Implementar `app/core/config.py` con clase `Settings` (`BaseSettings`), validador para normalizar esquema `postgresql+asyncpg://` y test unitario de carga de configuración.

## 2. Motor Asincrónico y Fábrica de Sesiones

- [x] 2.1 Escribir test unitario en `tests/test_database.py` que compruebe la creación del motor asincrónico y la fábrica con `expire_on_commit=False` (RED).
- [x] 2.2 Implementar en `app/core/database.py` las funciones `crear_motor()` y `crear_fabrica_sesiones()` y verificar que los tests pasen (GREEN).
- [x] 2.3 Implementar la dependencia generadora asincrónica `get_session` para inyección vía `Depends(get_session)` y verificar que libere la sesión correctamente.

## 3. Módulo Health y Endpoints de Salud

- [x] 3.1 Escribir test en `tests/test_health.py` para `GET /health/live` (código 200 y JSON `{"estado": "vivo"}`) y `GET /health/ready` (código 200 ejecutando `SELECT 1`) con `httpx.AsyncClient` (RED).
- [x] 3.2 Implementar `app/modules/health/service.py` con `verificar_liveness()` y `verificar_readiness(session: AsyncSession)`.
- [x] 3.3 Implementar `app/modules/health/router.py` con los endpoints `/live` y `/ready` y verificar que los tests pasen (GREEN).

## 4. Lifespan de FastAPI y Creación de Tablas

- [x] 4.1 Escribir test de integración en `tests/test_lifespan.py` que verifique que el lifespan almacena `engine` y `session_factory` en `app.state`, ejecuta `create_all` y cierra el pool de conexiones en shutdown (RED).
- [x] 4.2 Implementar `app/main.py` con el context manager `lifespan`, inicialización de tablas mediante `conn.run_sync(SQLModel.metadata.create_all)`, inclusión del router de salud bajo `/health` y cierre con `await engine.dispose()` (GREEN).

## 5. Verificación de Contratos y Casos HTTP

- [x] 5.1 Crear archivo `test/health.http` con las peticiones comentadas para `GET /health/live` y `GET /health/ready` según formato de entrega de la cátedra.
- [x] 5.2 Ejecutar la suite completa de tests automatizados (`pytest`) y certificar cobertura en verde.
