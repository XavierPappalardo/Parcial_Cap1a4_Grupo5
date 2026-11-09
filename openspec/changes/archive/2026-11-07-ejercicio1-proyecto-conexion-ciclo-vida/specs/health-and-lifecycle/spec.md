# Spec Delta

## Purpose

Proporciona verificación de salud operativa (liveness y readiness) y gestión del ciclo de vida asincrónico para la aplicación de la librería.

## ADDED Requirements

### Requirement: Liveness verification
The system SHALL provide a `GET /health/live` endpoint that confirms the web process is running without interacting with the database.

#### Scenario: Successful liveness check
- **WHEN** client sends a GET request to `/health/live`
- **THEN** system responds with HTTP status 200 and JSON body `{"estado": "vivo"}`

### Requirement: Database readiness verification
The system SHALL provide a `GET /health/ready` endpoint that executes a database query (`SELECT 1`) using an async session to confirm database availability.

#### Scenario: Successful readiness check
- **WHEN** client sends a GET request to `/health/ready` and database is reachable
- **THEN** system executes `SELECT 1` and responds with HTTP status 200 and JSON body indicating database availability

#### Scenario: Database unavailable readiness check
- **WHEN** client sends a GET request to `/health/ready` and database is unreachable
- **THEN** system responds with HTTP status 500

### Requirement: Application lifespan management and table creation
The system SHALL initialize the async database engine and session factory during application startup and automatically invoke `SQLModel.metadata.create_all` for uncreated tables.

#### Scenario: Clean application startup
- **WHEN** the application starts up
- **THEN** async engine and session factory are stored in `app.state`, and all tables defined in models are created if they do not exist

#### Scenario: Clean application shutdown
- **WHEN** the application receives a termination signal
- **THEN** the database engine pool is cleanly disposed without blocking
