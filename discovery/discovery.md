# Discovery — La librería con despliegue en el VPS (UTN Programación III)

**Fecha**: 2026-11-05  
**Fuentes investigadas**: Consigna oficial del Parcial "La librería con despliegue en el VPS", UTN Tecnicatura Universitaria en Programación (Unidades 1 a 4).

---

## 1. Problema que resuelve

Construcción de un backend API REST asincrónico para una librería de barrio que gestiona su catálogo (libros, autores, géneros, editoriales) y ventas (clientes, perfiles 1:1, renglones de venta). El sistema debe integrar FastAPI, SQLModel y PostgreSQL (asyncpg), resolviendo relaciones complejas (agregación, composición, 1:1, N:N con datos propios) sin caer en el problema N+1, y empaquetado en Docker (Alpine) para su despliegue en un VPS sin filtrar credenciales ni secretos.

---

## 2. Usuarios / roles

- **Personal / Sistema de la Librería**: gestiona las altas y consultas de catálogo (editoriales, géneros, autores y libros), administra clientes y registra ventas con sus renglones.
- **Cliente**: entidad del dominio que compra libros; puede asociar un perfil opcional con teléfono y dirección de contacto.
- **Cátedra / Evaluador**: ejecuta las pruebas automatizadas (healthchecks, endpoints, consultas en consola y despliegue en VPS).

*(Nota: La autenticación y autorización mediante usuarios/roles de seguridad quedan fuera del alcance de este parcial).*

---

## 3. Casos de uso

1. **Gestión de Catálogo**:
   - Crear, consultar y actualizar `editoriales` y `generos`.
   - Crear autores y consultar sus libros con rol y orden de autoría.
   - Crear libros asociando editorial (`agregación`), género opcional (`agregación opcional`) y lista de autores con rol y orden (`muchos a muchos con datos de relación`).
   - Listar libros con paginación (`limit`, `offset`) y filtros combinados por título (búsqueda insensible a mayúsculas con parámetros ligados) y género.
2. **Gestión de Clientes y Perfiles**:
   - Registrar cliente con email único.
   - Crear y asociar como máximo un único perfil de cliente (`1 a 1` con `perfil_cliente.cliente_id UNIQUE`).
   - Consultar cliente con su perfil precargado y listar sus ventas históricas.
3. **Registro y Detalle de Ventas**:
   - Registrar una venta atómica con renglones anidados (`composición`), validando que contenga al menos un renglón y libros no repetidos (`422`).
   - Copiar el precio unitario del libro al renglón desde la base de datos al momento de la venta y calcular el total en el servidor.
   - Disparar tarea en segundo plano (`BackgroundTasks`) simulando el envío de comprobante sin bloquear la respuesta.
   - Consultar el detalle de una venta con cliente y renglones con carga anticipada sin N+1.
4. **Health y Diagnóstico**:
   - `GET /health/live`: prueba de vida inmediata sin consultar la base de datos.
   - `GET /health/ready`: prueba de preparación ejecutando `SELECT 1` sobre la base de datos.

---

## 4. Competidores / soluciones existentes

| Solución / Referencia | Contexto | Aspectos Relevantes |
|---|---|---|
| Ejercicios de clase (Caps. 1 a 4) | Prácticas UTN | Fundamentos de FastAPI, CRUD, asincronía y SQLModel |
| Despliegue estándar en VPS | Entorno de producción | Docker Alpine sin compose, contenedor no root, inyección de variables vía `--env-file` |

---

## 5. Funcionalidades necesarias (Innegociables - 8 Ejercicios)

- **Ejercicio 1 (Conexión y ciclo de vida)**: Lifespan asincrónico en `app/main.py`, fábrica de sesiones con `expire_on_commit=False`, dependencia `get_session`, creación de tablas con `SQLModel.metadata.create_all`, endpoints `/health/live` y `/health/ready`.
- **Ejercicio 2 (Modelos, restricciones y relaciones)**: Modelos de dominio completos con `UNIQUE`, `CHECK`, claves foráneas indexadas, navegación bidireccional con `Relationship(back_populates=...)`, entidad intermedia `LibroAutor`, y dinero representado con `Decimal`.
- **Ejercicio 3 (Contratos y CRUD)**: DTOs separados de entrada/salida (sin id en creación, `exclude_unset` en PATCH), códigos HTTP estrictos (201, 404, 409 por integridad, 422 por validación), paginación RN-10 y búsqueda con parámetros ligados RN-11.
- **Ejercicio 4 (Altas con relaciones)**: Alta de libro y venta recibiendo IDs de relaciones existentes; captura de violación de FK por la base traduciéndola a HTTP 409 (sin chequeos previos con `if`).
- **Ejercicio 5 (Lecturas sin N+1)**: Carga anticipada obligatoria (`joinedload` para relaciones a uno, `selectinload` para colecciones), número fijo de consultas demostrado en consola.
- **Ejercicio 6 (Asincronía sin bloqueos)**: Handlers 100% `async def`, sin bloqueos síncronos, simulación de notificación con `BackgroundTasks` (`asyncio.sleep(0.5)`).
- **Ejercicio 7 (Contenedor Docker)**: `Dockerfile` con base `python:3.12-alpine` (< 100 MB), usuario sin privilegios, sin secretos en imagen ni capas, uvicorn en `0.0.0.0:8000`, `HEALTHCHECK` a `127.0.0.1`.
- **Ejercicio 8 (Despliegue y Pruebas)**: Despliegue en VPS con `docker run`, script de carga de datos iniciales (`docker exec libreria ...`), casos de prueba en `test/*.http` (C-01 a C-08), evidencias en `evidencia/` (D-01 a D-07) y documentación en `DEPLOY.md`.

---

## 6. Funcionalidades opcionales (Quedan fuera explícitamente)

- Autenticación y autorización (Capítulo 5).
- Repositorios y patrón Unit of Work (Capítulo 6) — la lógica vive en `service.py`.
- Colas de tareas distribuidas con Redis/Celery/ARQ (Capítulos 7 y 8).
- Orquestación con Docker Compose — se usa una sola imagen con `docker run`.
- Migraciones automáticas con Alembic — se usa `create_all`.
- Modificación (PATCH) de ventas — las ventas son inmutables.

---

## 7. Reglas de negocio

- **RN-01**: ISBN de un libro es único (`UNIQUE`; 409).
- **RN-02**: Email de un cliente es único (`UNIQUE`; 409).
- **RN-03**: Precio de libro > 0 y stock >= 0 (`CHECK` y validación DTO).
- **RN-04**: Venta se crea con renglones anidados (sin alta separada de renglones).
- **RN-05**: Venta con al menos 1 renglón y sin libros duplicados (`422`).
- **RN-06**: Precio de renglón congelado desde el libro al registrar la venta.
- **RN-07**: Total de venta calculado por el servidor (`sum(cantidad * precio_unitario)`).
- **RN-08**: Ventas inmutables (no hay PATCH de ventas).
- **RN-09**: Cliente tiene como máximo un perfil (`UNIQUE` en `perfil_cliente.cliente_id`; 409).
- **RN-10**: Paginación obligatoria con `limit` (1 a 100, defecto 20) y `offset` (desde 0; `422` si inválido).
- **RN-11**: Búsqueda por título insensible a mayúsculas con parámetros ligados.
- **RN-12**: Errores no exponen texto interno de PostgreSQL, nombres de tablas ni trazas (traducción de `IntegrityError` a mensaje propio).

---

## 8. Integraciones

- **PostgreSQL 16**: Base relacional provista en el servidor o localmente vía `DATABASE_URL` con driver `postgresql+asyncpg`.
- **Entorno**: Lectura de configuración con `python-dotenv` local y `--env-file` en Docker.
- **Servidor ASGI**: Uvicorn escuchando en `0.0.0.0:8000`.

---

## 9. Restricciones técnicas y de entrega

- **Stack**: Python 3.12, FastAPI >= 0.111, SQLModel >= 0.0.24, SQLAlchemy 2.0 async, asyncpg >= 0.30, Docker >= 20.10.
- **Estructura modular obligatoria**:
  - `app/main.py`
  - `app/core/config.py`, `app/core/database.py`
  - `app/modules/<módulo>/{models,schemas,service,router}.py`
  - Módulos mínimos: `health`, `editoriales`, `generos`, `autores`, `libros`, `clientes`, `ventas`.
  - `LibroAutor` en `libros`, `PerfilCliente` en `clientes`, `RenglonVenta` en `ventas`.
- **Archivos complementarios**: `Dockerfile`, `.dockerignore`, `requirements.txt`, `env.example`, `DEPLOY.md`, `README.md`, `test/*.http`, `evidencia/`.
- **Empaquetado final**: Archivo `Parcial_Cap1a4_<NombreDelGrupo>.zip` sin carpetas `.venv`, `__pycache__` ni `.env`.

---

## 10. Riesgos

- **Compatibilidad de Alpine Linux (musl)**: Asegurar que todas las librerías (`asyncpg`, `pydantic-core`) se instalen como wheels precompiladas sin requerir dependencias de compilación adicionales.
- **Consultas N+1 inadvertidas**: Garantizar que todas las rutas que retornan relaciones utilicen estrictamente `joinedload` (para relaciones a uno) y `selectinload` (para relaciones a muchos).
- **Traducción de IntegrityError**: Mapear correctamente excepciones de asyncpg/SQLAlchemy para devolver 409 sin filtrar datos de la base de datos.
- **Networking en Docker**: Configurar el `HEALTHCHECK` sobre `127.0.0.1` en Alpine y prever `host.docker.internal` para pruebas locales si la base corre en el host.

---

## 11. Preguntas abiertas y decisiones acordadas

- **Código base**: El proyecto se construye limpio desde cero, sin código residual.
- **Datos de grupo y README**: El usuario completará los datos personales en `README.md` y definirá el nombre de entrega final.
- **Credenciales VPS/DB**: Se dejan completamente parametrizadas en variables de entorno y `env.example` para inyectar al momento de desplegar.
