# Design

## Contexto

Los modelos del Ejercicio 2 existen y siguen fielmente `knowledge-base/04_modelo_de_datos.md`: entidad asociativa `LibroAutor` con datos propios (no link model), uno a uno con `uselist=False`, composición con `all, delete-orphan` en Venta→RenglonVenta y Libro→LibroAutor, dinero con `Decimal`/NUMERIC y FKs indexadas. El deficit son las pruebas y su registro OPSX.

## Decisiones

### DD-E1 — Pruebas por metadata y no por esquema físico PostgreSQL
Los contratos de la consigna (nombres, PK, UNIQUE, CHECK, FK, índices, relaciones, tipos) viven en la metadata de SQLAlchemy y son verificables 1:1 desde `SQLModel.metadata` sin levantar PostgreSQL. Los tests corren así en cualquier entorno; los casos de persistencia real (D-01..D-07) se marcan para VPS con PostgreSQL y NO se reportan como verificados si no hay servidor.

### DD-E2 — Doble verificación estructural
1. `configure_mappers()`: SQLAlchemy resuelve TODAS las relaciones y falla ante mappings mal armados (circularidades, lados sin `back_populates` coherentes, FKs inexistentes).
2. `create_all` sobre `sqlite+aiosqlite` en memoria: genera la DDL completa de 9 tablas: prueba end to end de que `main.py` (integración) podrá crear el esquema.

### DD-E3 — Importación limpia en proceso aislado
Se importa cada módulo de modelos en un subproceso Python independiente (`sys.executable -c ...`). Interprete nuevo = primera ejecución real de cada import; una dependencia circular o un import roto fallaría ahí, cosa que en el proceso de test ya cargado no se deteecta.

### DD-E4 — Escenarios verificados (mapa de la consigna)

| # | Escenario | Cómo se verifica con metadata |
|---|---|---|
| 1 | 9 tablas existen | claves de `SQLModel.metadata.tables` |
| 2 | nombres de tablas y columnas | set de columnas por tabla |
| 3 | PK simple y compuesta | `table.primary_key.columns.keys()` |
| 4 | UNIQUE | `UniqueConstraint`/índices únicos por tabla |
| 5 | CHECK | `CheckConstraint.sqltext` por tabla |
| 6 | FK | `table.foreign_keys` destino exacto |
| 7 | índices de FK | `table.indexes` cubre cada FK |
| 8 | uno a uno | `uselist=False` + FK UNIQUE en `perfil_cliente.cliente_id` |
| 9 | N:M con datos propios | tabla intermedia con PK compuesta + rol/orden |
| 10 | bidireccionalidad | `back_populates` en ambos lados de las 7 relaciones |
| 11 | Decimal y NUMERIC | `python_type == Decimal`, precision/scale |
| 12 | composición y cascada | `cascade all, delete-orphan` en venta→renglones y libro→autorías |

## Riesgos
- `DateTime(timezone=True)` sobre SQLite genera la DDL sin zona horaria; la verificación de tipo DATE TIME con tz | PostgreSQL se documentará en los casos D (pendientes de DB real).
- `index=True` en columnas PK compuestas crea índices individuales sobre las FK; en PostgreSQL esto es útil (consultas solo-PK secundaria: `WHERE libro_id=...`); se mantiene tal cual para respetar la especificación.
