# Tasks

## 1. Configuración segura

- [x] 1.1 Quitar el valor por defecto con credenciales de `DATABASE_URL` en `app/core/config.py` (fallo controlado al instanciar `Settings` sin la variable) y conservar el validador de normalización del esquema.
- [x] 1.2 Reemplazar credenciales de `env.example` por placeholders de estructura.
- [x] 1.3 Agregar en `tests/test_config.py` el test de `ValidationError` cuando falta `DATABASE_URL` (sin depender de `.env` ni variables del entorno heredadas).

## 2. Ciclo de vida resiliente

- [x] 2.1 En `app/main.py`, garantizar `engine.dispose()` cuando `create_all` falla en el arranque (re-lanzar la excepción original).
- [x] 2.2 Test de integración real del lifespan sobre `sqlite+aiosqlite` (motor, fábrica y estado en `app.state`, tablas creadas, pool cerrado al finalizar) en `tests/test_lifespan.py`.
- [x] 2.3 Test del error path: con `crear_motor`/`crear_fabrica_sesiones` sustituidos por dobles que fallan en `begin()`, verificar `dispose()` y la propagación de la excepción.

## 3. Pruebas funcionales de salud y sesión

- [x] 3.1 Tests HTTP de `/health/live` (200 sin DB) y `/health/ready` (200 con DB disponible; 500 sin exponer trazas frente a DB inalcanzable) vía `TestClient` en `tests/test_health.py`.
- [x] 3.2 Test funcional de `get_session` en `tests/test_database.py`: igual sesión dentro de una petición, sesión distinta en la siguiente petición (`sqlite+aiosqlite`).

## 4. Dependencias y suite

- [x] 4.1 Agregar `aiosqlite` a `requirements.txt` para pruebas sin PostgreSQL.
- [x] 4.2 Ejecutar `pytest -q` completo en verde y documentar el resultado.
