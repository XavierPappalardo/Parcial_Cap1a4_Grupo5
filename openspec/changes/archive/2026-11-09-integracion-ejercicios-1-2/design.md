# Design

## Contexto

`SQLModel` registra una clase en la metadata únicamente cuando su módulo se importa. El lifespan ejecuta `metadata.create_all`; sin importaciones previas, las tablas del dominio no existen en la base.

## Decisiones

### DD-I1 — Importación centralizada en main.py
Las 6 importaciones de modelos viven en `app/main.py` (antes de `app = FastAPI(...)` y del `create_all` del lifespan). Alternativas descartadas:
- Un `app/models/__init__.py` agregador: crea una capa extra sin beneficios; el lifespan no la encuentra salvo importarla igual. La convención del proyecto es modular (`package by feature`): cada módulo dueño de sus modelos.
- `create_all` por módulo: repetiría esquema; la metadata es global y basta un único punto de registro.

Marcadas con `# noqa: F401` porque se importan por efecto de registro, no por referencias directas.

### DD-I2 — Orden determinista
Las importaciones de módulos no dependen de orden entre sí (TYPE_CHECKING + anotaciones por string evitan los ciclos); la resolución de `Relationship` de SQLModel/SQLAlchemy es diferida, `configure_mappers()` se ejecuta y resuelve al primer uso. La prueba `test_importacion_aislada_de_cada_modulo_...` (Ejercicio 2) ya demostró la ausencia de ciclos reales.

### DD-I3 — Prueba de integración final
La suite combinada corre con la app real: los tests del lifespan (TestClient) ejecutan el arranque completo, creando las 9 tablas sobre `sqlite+aiosqlite`. PostgreSQL sigue pendiente de validación para los casos de datos del parcial (casos D), documentado en el informe.
