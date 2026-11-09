# Spec Delta

## Purpose

Refuerza la capability `health-and-lifecycle` con requisitos de configuración segura y liberación de recursos ante fallos de inicialización, detectados por la auditoría del Ejercicio 1.

## MODIFIED Requirements

### Requirement: Application lifespan management and table creation
The system SHALL initialize the async database engine and session factory during application startup and automatically invoke `SQLModel.metadata.create_all` for uncreated tables. The engine SHALL be disposed both on clean shutdown and when startup initialization fails.

#### Scenario: Clean application startup
- **WHEN** the application starts up
- **THEN** async engine and session factory are stored in `app.state`, and all tables defined in models are created if they do not exist

#### Scenario: Clean application shutdown
- **WHEN** the application receives a termination signal
- **THEN** the database engine pool is cleanly disposed without blocking

#### Scenario: Failed startup initialization
- **WHEN** `SQLModel.metadata.create_all` fails during startup (e.g., database unreachable)
- **THEN** the engine is disposed before the exception propagates and no connections are left behind

### Requirement: Environment-driven configuration without embedded credentials
The system SHALL read `DATABASE_URL` from the environment with **no default value containing credentials**, and SHALL fail in a controlled manner when the variable is missing. The environment template `env.example` SHALL present the structure of the variables only.

#### Scenario: Missing DATABASE_URL
- **WHEN** the application starts without a `DATABASE_URL` provided by environment or `.env`
- **THEN** settings instantiation raises `ValidationError` and startup aborts in a controlled way

#### Scenario: Provided DATABASE_URL with plain scheme
- **WHEN** `DATABASE_URL` is provided as `postgresql://...` or `postgres://...`
- **THEN** the setting is normalized to `postgresql+asyncpg://`

#### Scenario: Environment template without secrets
- **WHEN** `env.example` is inspected
- **THEN** it contains no real credentials, only placeholder structure of the variables

## ADDED Requirements

### Requirement: Session per request dependency
The system SHALL provide `get_session` as a FastAPI dependency delivering one `AsyncSession` per request, built from the session factory stored in `app.state`.

#### Scenario: One session per request
- **WHEN** a request uses `Depends(get_session)`
- **THEN** the same session instance is shared among all consumers within the request and a new session is created for the next request, with each session properly closed

### Requirement: Health endpoints verified over real HTTP transport
The suite SHALL verify `/health/live` and `/health/ready` behavior through FastAPI `TestClient` (real HTTP transport and lifespan), including the 500 mapping of `/health/ready` when the database is unreachable.

#### Scenario: Readiness against unreachable database
- **WHEN** `GET /health/ready` targets an unreachable database
- **THEN** the response status is 500 and the body exposes no internal error details or traces
