# Spec Delta

## Purpose

Cierra la capability `health-and-lifecycle` para la integración de los ejercicios 1 y 2: el arranque garantiza que TODOS los modelos del dominio estén registrados en la metadata antes de ejecutar `SQLModel.metadata.create_all`.

## MODIFIED Requirements

### Requirement: Application lifespan management and table creation
The system SHALL initialize the async database engine and session factory during application startup, SHALL register all nine domain models in `SQLModel.metadata` (explicit imports of the six model modules in `app/main.py`), and automatically invoke `SQLModel.metadata.create_all` so the full mandatory schema (`editorial`, `genero`, `autor`, `libro`, `libro_autor`, `cliente`, `perfil_cliente`, `venta`, `renglon_venta`) is created when it does not exist.

#### Scenario: Startup creates the full mandatory schema
- **WHEN** the application starts against an empty database
- **THEN** `create_all` runs with every model registered and the nine mandatory tables are created

#### Scenario: Clean application shutdown
- **WHEN** the application receives a termination signal
- **THEN** the database engine pool is cleanly disposed without blocking

#### Scenario: Failed startup initialization
- **WHEN** `SQLModel.metadata.create_all` fails during startup (e.g., database unreachable)
- **THEN** the engine is disposed before the exception propagates and no connections are left behind
