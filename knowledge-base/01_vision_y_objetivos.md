# 01 — Visión y Objetivos

## Propósito del sistema
Construir una API REST asincrónica y robusta para la gestión del catálogo de libros y el registro de ventas de una librería de barrio, cumpliendo con las buenas prácticas de arquitectura web moderna en Python, persistencia relacional estricta sin el problema N+1, y empaquetado seguro en contenedor Docker para despliegue en un VPS sin filtración de secretos.

El sistema sirve como entrega integral para la evaluación de Programación III (UTN - Tecnicatura Universitaria en Programación), cubriendo del objeto a la persistencia (Capítulos 1 a 4).

## Objetivos por actor

| Actor | Objetivo principal | Objetivos secundarios |
|---|---|---|
| **Personal de Librería / Sistema** | Administrar el catálogo de libros y registrar ventas atómicas con sus renglones. | Consultar autores, géneros y editoriales; buscar libros por título con filtros y paginación; consultar historial de ventas por cliente. |
| **Cliente** | Figurar en el sistema como comprador y asociar un perfil opcional de contacto. | Mantener actualizados sus datos de contacto (teléfono y dirección). |
| **Cátedra / Evaluador** | Verificar el cumplimiento estricto de los requisitos técnicos, de diseño y de despliegue. | Evaluar pruebas automatizadas (`.http`), ausencia de N+1 en consola, liveness/readiness, empaquetado Docker Alpine (< 100 MB base) y persistencia en VPS. |

## Alcance v1.0

- **Ciclo de vida y conexión asincrónica**: Lifespan en FastAPI, motor SQLAlchemy asincrónico con `asyncpg`, fábrica de sesiones con `expire_on_commit=False`, inyección con `Depends(get_session)`, y endpoints de salud (`/health/live` y `/health/ready`).
- **Modelo de dominio relacional completo**: 
  - Editoriales (`agregación`).
  - Géneros (`agregación opcional`).
  - Autores y autorías (`muchos a muchos con atributos propios` vía `LibroAutor`: rol y orden).
  - Libros con precio en `Decimal`, stock, ISBN único y validaciones de integridad.
  - Clientes con email único y perfil opcional (`1 a 1` estricto con `perfil_cliente.cliente_id UNIQUE`).
  - Ventas con renglones anidados (`composición`), congelamiento de precio unitario desde la base y cálculo de total en servidor.
- **Navegación y carga anticipada**: Navegación bidireccional en todas las relaciones; lecturas con `joinedload` (relaciones a uno) y `selectinload` (colecciones) para evitar el problema N+1.
- **Contratos DTO y endpoints CRUD**: DTOs separados para Create, Read, Update; códigos HTTP semánticos (201, 200, 404, 409, 422); paginación obligatoria (`limit`/`offset`) y búsqueda por título case-insensitive con parámetros ligados.
- **Asincronía y tareas en segundo plano**: Todos los handlers asincrónicos sin bloqueos; aviso de comprobante de venta simulado mediante `BackgroundTasks` (`asyncio.sleep(0.5)`).
- **Contenedor y Despliegue**: Dockerfile multi-etapa o directo basado en `python:3.12-alpine` (< 100 MB de imagen base), usuario sin privilegios (`USER`), sin secretos en capas, `HEALTHCHECK` configurado a `127.0.0.1`, y despliegue documentado en `DEPLOY.md`.
- **Casos de prueba y evidencias**: Casos C-01 a C-08 en `test/*.http` y evidencias de ejecución D-01 a D-07 en `evidencia/`.

## Fuera de alcance

- Autenticación y autorización de usuarios (JWT, OAuth2, roles de usuario en endpoints — Capítulo 5).
- Patrón Repositorio y Unit of Work (Capítulo 6) — la lógica reside directamente en los servicios de módulo.
- Colas de tareas distribuidas y workers con Redis/Celery (Capítulos 7 y 8).
- Orquestación multi-contenedor con Docker Compose — el despliegue es en una sola imagen ejecutada con `docker run`.
- Migraciones automáticas de esquema con Alembic — la base inicializa sus tablas mediante `SQLModel.metadata.create_all` en el lifespan.
- Modificación de ventas (no existe `PATCH` ni eliminación de ventas registradas).

## Métricas de éxito

1. **Aprobación del 100% de los casos de prueba mínimos**:
   - C-01 a C-08 aprobados sin errores de contrato.
   - D-01 a D-07 demostrados con evidencias claras en el VPS asignado.
2. **Eficiencia en consultas**: C-07 ejecutado con número fijo y predecible de sentencias SQL en consola tanto para 1 como para múltiples autores/renglones.
3. **Seguridad y robustez**: 0 secretos filtrados en git, en la imagen Docker o en el paquete `.zip`; ningún error 500 no controlado ni exposición de trazas de PostgreSQL (`RN-12`).
4. **Cumplimiento de tamaño de imagen**: Imagen base `python:3.12-alpine` verificada por debajo del umbral de 100 MB.
