# Proposal

## Why

La auditoría del Ejercicio 1 (rama `ejercicio-1`) detectó desviaciones respecto de las verificaciones obligatorias de la consigna y de la reglas duras de AGENTS.md:

1. `app/core/config.py` define un valor por defecto para `DATABASE_URL` que incluye usuario y contraseña (`postgres:postgres@localhost:5432/libreria`). Se exige que la URL se lea desde el entorno **sin valor por defecto con credenciales** y que la aplicación falle de manera controlada si falta la variable.
2. `env.example` publica la URL con credenciales de ejemplo (`postgres:postgres...`) en lugar de mostrar únicamente la estructura de las variables.
3. `app/main.py`: si `SQLModel.metadata.create_all` falla en el arranque, la excepción se propaga antes de entrar al `try ... finally`, de modo que el motor **nunca** se cierra con `engine.dispose()` ("cerrar el motor incluso cuando falle la inicialización").
4. `tests/test_lifespan.py` solo comprueba que la función exista (`hasattr(lifespan, "__call__")`), sin verificar su comportamiento real (estado en `app.state`, `create_all`, cierre del pool).
5. `tests/test_health.py` no ejercita los endpoints vía HTTP real (solo llama funciones internas); falta verificación del manejo de error 500 en `/health/ready`.
6. No existe prueba del fallo controlado al faltar `DATABASE_URL`, ni prueba funcional de la dependencia `get_session` (una sesión por petición).

El trabajo existente es valioso y se conserva; este change **corrige y refuerza**, no reescribe.

## What Changes

- `app/core/config.py`: `DATABASE_URL: str` sin valor por defecto (fallo controlado de `Settings` cuando falta la variable); se mantiene el validador de normalización `postgresql://` → `postgresql+asyncpg://`.
- `env.example`: placeholders genéricos sin credenciales.
- `app/main.py`: `engine.dispose()` garantizado también cuando falla `create_all` en el arranque.
- `tests/test_config.py`: nuevo test de fallo controlado sin `DATABASE_URL`.
- `tests/test_database.py`: test funcional de `get_session` (instancia única por petición, distinta entre peticiones), ejecutado sobre `sqlite+aiosqlite` para prescindir de PostgreSQL local.
- `tests/test_health.py`: tests vía `TestClient` (client de FastAPI) de `/health/live` y `/health/ready` con base de datos `sqlite+aiosqlite`.
- `tests/test_lifespan.py`: test de integración real del lifespan: éxito sobre `sqlite+aiosqlite` (motor + fábrica en `app.state`, tablas creadas, pool cerrado al salir) y verificación de `engine.dispose()` cuando falla la inicialización (mock de `crear_motor`).
- `requirements.txt`: se agrega `aiosqlite` (solo pruebas; PostgreSQL sigue siendo la base de datos de la aplicación).

## Capabilities

### Modified Capabilities
- `health-and-lifecycle`: el requisito de gestión del ciclo de vida ahora incluye la liberación del motor cuando la inicialización falla, y la configuración exige `DATABASE_URL` sin valor por defecto con credenciales.

### New Capabilities
*(Ninguna)*

## Impact
- **Código**: `app/core/config.py`, `app/main.py`, `env.example`, `requirements.txt`, `tests/*`.
- **Comportamiento**: la aplicación no inicia sin `DATABASE_URL`; el arranque fallido no deja conexiones abiertas.
- **Pruebas**: suite reforzada sin dependencia de PostgreSQL local (`aiosqlite`); los casos específicos de PostgreSQL se validan con URL dedicada si el entorno la provee.
