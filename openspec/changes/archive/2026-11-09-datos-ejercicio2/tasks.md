# Tasks

## 1. Infraestructura de pruebas de la rama

- [x] 1.1 Crear `pytest.ini` (pythonpath ., asyncio mode auto) y `requirements.txt` unificados con los del Ejercicio 1 (incluye aiosqlite para pruebas sin PostgreSQL).
- [x] 1.2 Crear el paquete `tests/` con inicialización explícita.

## 2. Pruebas de metadata del modelo de datos

- [x] 2.1 Tests de las 9 tablas obligatorias y sus columnas exactas (`tests/test_modelos_datos.py`).
- [x] 2.2 Tests de PK simple (`id`) y compuesta (`libro_autor`).
- [x] 2.3 Tests de UNIQUE (editorial, genero, isbn, email, cliente_id del perfil).
- [x] 2.4 Tests de CHECK (precio, stock, orden, rol, total, cantidad, precio_unitario).
- [x] 2.5 Tests de FK y sus índices.
- [x] 2.6 Tests de relaciones bidireccionales con `back_populates` (7 relaciones), uno a uno (`uselist=False`) y N:M con datos propios.
- [x] 2.7 Tests de `Decimal` + `NUMERIC(10,2)/NUMERIC(12,2)` (sin float para dinero).
- [x] 2.8 Tests de composición con cascada `all, delete-orphan`.
- [x] 2.9 Test de `configure_mappers()` sin errores.
- [x] 2.10 Test de importación aislada de cada módulo de modelos (subproceso limpio, sin dependencias circulares).

## 3. Verificación de esquema generable

- [x] 3.1 `SQLModel.metadata.create_all` real sobre `sqlite+aiosqlite` generando las 9 tablas.
- [x] 3.2 Ejecutar la suite completa (`pytest -q`) en verde.
