# Proposal

## Why

El Ejercicio 2 exige el modelo de datos completo de la librería: 9 tablas obligatorias (`editorial`, `genero`, `autor`, `libro`, `libro_autor`, `cliente`, `perfil_cliente`, `venta`, `renglon_venta`) con sus PK simples y compuestas, restricciones UNIQUE y CHECK, claves foráneas indexadas y las 7 relaciones del dominio con navegación bidireccional.

En la rama `ejercicio-2-modelos` ya se escribieron los modelos con muy buena calidad, pero faltan los elementos que acreditan su correctitud frente a la consigna:

1. No existe change OPSX que documente la capability del modelo de datos.
2. No exista ninguna prueba automatizada de tablas, columnas, PK/UNIQUE/CHECK/FK/índices, relaciones, tipos `Decimal`/`NUMERIC` ni cascadas de composición.
3. La aplicación (`main.py`, rama `ejercicio-1`) todavía no importa los módulos de modelos antes de `SQLModel.metadata.create_all`: el esquema generado en el arranque estaría vacío. (La integración final se realiza sobre la rama de integración; este change deja los modelos listos e importables sin dependencias circulares.)

## What Changes

- Registrar y auditar los modelos existentes en 6 módulos (`app/modules/{editoriales,generos,autores,libros,clientes,ventas}/models.py`), confirmando la correspondencia estricta con la consigna (nombres de tablas y columnas obligatorios).
- Incorporar infraestructura de pruebas a la rama (`pytest.ini`, `requirements.txt`) coherente con la del Ejercicio 1, para una integración posterior limpia.
- Crear `tests/test_modelos_datos.py` con verificaciones de metadata por SQLModel/SQLAlchemy (sin PostgreSQL): 9 tablas, columnas, PK compuesta en `libro_autor`, UNIQUE, CHECK, FKs, índices de FK, relaciones bidireccionales (`back_populates`), uno a uno (`uselist=False`), N:M con datos propios, `Decimal` + `NUMERIC(10,2)`/`NUMERIC(12,2)`, composición con `all, delete-orphan` y `configure_mappers()` sin errores.
- Verificar la importación independiente de cada módulo de modelos en un proceso Python limpio (sin errores de dependencias circulares).
- Creación real del esquema completo con `SQLModel.metadata.create_all` sobre `sqlite+aiosqlite` como prueba de que los mappers y la DDL son configurables (PostgreSQL queda pendiente de validación en VPS/DB real para los casos D).

## Capabilities

### New Capabilities
- `datos-catalogo-ventas`: modelo de datos obligatorio con restricciones y relaciones, garantizado por pruebas de metadata.

### Modified Capabilities
*(Ninguna)*

## Impact
- **Código**: los 6 módulos de modelos (auditados, sin cambios de nombres obligatorios), archivos de prueba `tests/pytest.ini`, `requirements.txt`.
- **Sin cambios de API HTTP**: los routers de catálogo/ventas quedan para ejercicios siguientes (3-8).
