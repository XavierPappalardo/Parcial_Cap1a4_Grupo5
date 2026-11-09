# Design

## Contexto

El Ejercicio 1 implementa la fundación (config, motor async, `get_session`, lifespan y health). Su implementación es en lo esencial correcta; la auditoría detectó violaciones a verificaciones explícitas de la consigna que deben corregirse sin arquitecturas de reemplazo.

## Decisiones

### DD-C1 — `DATABASE_URL` sin valor por defecto
`Settings.DATABASE_URL: str` sin `= "..."`. Con `pydantic-settings`, la falta de la variable produce `ValidationError` en la instanciación → la app no arranca: es el "fallo de manera controlada" pedido. Las URLs de prueba se pasan explícitas por entorno/parametrización. El validador `normalizar_database_url` (acepta esquemas `postgresql://` y `postgres://` normalizándolos a `postgresql+asyncpg://`) se conserva.

### DD-C2 — Liberación del motor en fallo de inicialización
Estructura del lifespan:

```python
engine = crear_motor(...)
app.state.engine = engine
app.state.session_factory = crear_fabrica_sesiones(engine)
try:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
except BaseException:
    await engine.dispose()   # no dejar conexiones colgadas si el arranque aborta
    raise
yield
...
finally:
    await engine.dispose()
```

Se captura `BaseException` para cubrir cancelaciones de `asyncio` en el arranque; se re-lanza para no ocultar el error.

### DD-C3 — Estrategia de pruebas sin PostgreSQL local
La suite debe correr en verde sin servidor de base de datos. Se usa `sqlite+aiosqlite` para:
- el test funcional de `get_session` (mismo `AsyncSession` entre dos `Depends` de la misma petición; sesiones distintas entre peticiones),
- los tests HTTP de `/health` vía `TestClient` (el lifespan corre realmente, incluyendo `create_all` y `dispose`),
- el test de integración del lifespan con archivo temporal en disco (la conexión de `:memory:` no sobrevive a conexiones distintas del pool).

Los tests sobre PostgreSQL real quedan separados y se omite/reduce (`skipif`) cuando no hay PostgreSQL disponible, sin reportarlos como verificados.

### DD-C4 — Test del lifespan con simulación de fallo de inicialización
`crear_motor` y `crear_fabrica_sesiones` se sustituyen por dobles de prueba (monkeypatch) cuyo `begin()` lanza; se verifica que `engine.dispose()` fue esperado exactamente una vez y que la excepción se propaga. Es el comportamiento real del error path, no solo la firma de la función.

## Riesgos
- `DateTime(timezone=True)` sobre SQLite es aceptado por SQLAlchemy sin alterar el schema de prueba.
- `Settings` sin `.env` en el entorno de pruebas: los tests no dependen de archivos locales (`_env_file=None` y limpieza de variables de entorno con `monkeypatch`).
