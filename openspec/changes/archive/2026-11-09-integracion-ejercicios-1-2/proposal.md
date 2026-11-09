# Proposal

## Why

La rama de integración `integracion/ejercicios-1-2` ya contiene el Ejercicio 1 corregido (conexión, lifespan, health) y el Ejercicio 2 (modelos del dominio con sus pruebas de metadata). Falta el último eslabón: la aplicación (`app/main.py`) registra solo el router de health y NO importa los módulos de modelos, por lo que `SQLModel.metadata.create_all` del lifespan generaría un esquema vacío. La consigna exige que las 9 tablas obligatorias estén registradas antes del `create_all`.

## What Changes

- `app/main.py`: importación explícita de los 6 módulos de modelos (`editoriales`, `generos`, `autores`, `libros`, `clientes`, `ventas`) para dar de alta sus clases en `SQLModel.metadata` de forma determinista antes de `metadata.create_all`.
- Verificación integral: suite completa de ambos ejercicios en verde (42 pruebas) y `create_all` generando físicamente las 9 tablas en las pruebas del lifespan.

## Capabilities

### Modified Capabilities
- `health-and-lifecycle`: el arranque ahora garantiza el registro de todos los modelos antes de ejecutar `create_all`.

## Impact
- **Código**: `app/main.py` únicamente (importaciones; sin cambios de endpoints ni de restricciones).
- **Riesgo resuelto**: esquema vacío en arranque; se consolida la unión de ambas ramas con sus historyales preservados (merge `--no-ff`).
