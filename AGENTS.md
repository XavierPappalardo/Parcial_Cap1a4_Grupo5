# Parcial: La librería con despliegue en el VPS — Instrucciones para Agentes

> Este archivo (y su copia sincronizada `CLAUDE.md`) es lo **PRIMERO** que todo agente y colaborador lee al entrar al repositorio.
> Generado a partir de `knowledge-base/` y las directivas del proyecto. No editar a mano sin re-sincronizar ambos archivos.

---

## Stack Tecnológico

| Capa / Componente | Tecnología | Versión mínima | Uso / Justificación |
|---|---|---|---|
| **Lenguaje** | Python | 3.12 | Tipado estricto, async/await nativo. |
| **Framework Web** | FastAPI | 0.111+ | Todos los handlers asincrónicos (`async def`), inyección con `Depends(get_session)`. |
| **ORM / Modelos** | SQLModel | 0.0.24+ | Modelos de tabla y contratos DTO (Pydantic v2). |
| **Motor & Sesiones** | SQLAlchemy | 2.0+ (async) | Conexión asincrónica, `expire_on_commit=False`, carga anticipada (`joinedload`, `selectinload`). |
| **Driver PostgreSQL** | asyncpg | 0.30+ | Conector asincrónico para PostgreSQL 16. |
| **Base de Datos** | PostgreSQL | 16 | Servidor relacional en VPS / local. |
| **Servidor ASGI** | Uvicorn | `fastapi[standard]` | Escuchando en `0.0.0.0:8000`. |
| **Entorno** | python-dotenv | 1.0+ | Carga de variables de entorno desde `.env` o `--env-file`. |
| **Contenedor** | Docker | 20.10+ | Imagen base obligatoria `python:3.12-alpine` (< 100 MB). |

Detalle completo: [knowledge-base/02_descripcion_general.md](knowledge-base/02_descripcion_general.md)

---

## Base de Conocimiento

La fuente de verdad del dominio y la arquitectura vive en `knowledge-base/`. **Leé el archivo relevante ANTES de implementar cualquier tarea.**

| Archivo | Cuándo leerlo |
|---|---|
| [01_vision_y_objetivos.md](knowledge-base/01_vision_y_objetivos.md) | Propósito del sistema, alcance v1.0 y qué queda explícitamente fuera de alcance. |
| [02_descripcion_general.md](knowledge-base/02_descripcion_general.md) | Stack técnico, arquitectura modular (`app/modules/`) y resumen de endpoints. |
| [03_actores_y_roles.md](knowledge-base/03_actores_y_roles.md) | Actores y contratos de cada endpoint. |
| [04_modelo_de_datos.md](knowledge-base/04_modelo_de_datos.md) | Tablas obligatorias, columnas, restricciones (UNIQUE/CHECK/FKs/índices), ERD y seed data. |
| [05_reglas_de_negocio.md](knowledge-base/05_reglas_de_negocio.md) | Reglas RN-01 a RN-12 y sus garantes en base de datos o DTO. |
| [06_funcionalidades.md](knowledge-base/06_funcionalidades.md) | Historias de usuario por épica y criterios de aceptación. |
| [07_flujos_principales.md](knowledge-base/07_flujos_principales.md) | Flujos E2E: lifespan, altas con FK sin `if`, ventas atómicas y lecturas sin N+1. |
| [08_arquitectura_propuesta.md](knowledge-base/08_arquitectura_propuesta.md) | Estructura de directorios modular obligatoria, manejo de errores y variables de entorno. |
| [09_decisiones_y_supuestos.md](knowledge-base/09_decisiones_y_supuestos.md) | Decisiones arquitectónicas fundamentadas (DD-01 a DD-05). |
| [10_preguntas_abiertas.md](knowledge-base/10_preguntas_abiertas.md) | Tensiones resueltas (HEALTHCHECK Alpine) y puntos abiertos. |
| [11_despliegue_y_vps.md](knowledge-base/11_despliegue_y_vps.md) | Configuración de Dockerfile, comandos `docker run`, script de seed y matriz de pruebas C y D. |

---

## Skills Disponibles

| Agente / Especialidad | Rol | Skills que carga |
|---|---|---|
| **Backend Core** | FastAPI / SQLModel / asyncpg / Modelos | `openspec-apply-change`, `python-testing-patterns` |
| **DevOps / Despliegue** | Docker Alpine / VPS / Healthchecks | `dockerfile-best-practices`, `deploy-docs` |
| **Orquestación & Calidad** | OPSX / SDD / TDD / Specs | `active-orchestrator`, `kb-creator`, `roadmap-generator`, `openspec-propose`, `openspec-archive-change` |

> Los compact rules de cada skill los resuelve el orquestador desde `.atl/skill-registry.md` (no versionado).

---

## Roadmap de Changes

El plan de implementación y secuencia de cambios del proyecto se encuentra documentado en [CHANGES.md](CHANGES.md).

**Antes de cualquier implementación**: leer `CHANGES.md`, verificar las dependencias del change y seguir el ciclo OPSX.

---

## Reglas Duras y Restricciones de Trabajo

> Reglas globales definidas en el harness (orquestador, governance, TDD estricto, engram): el proyecto las hereda.
> Las siguientes reglas son **estrictas y vinculantes para todo agente o colaborador humano**. Romperlas se considera un defecto crítico de código o proceso.

### 1. Gobernanza de Proceso: Ciclo OPSX Obligatorio
- **NUNCA permitir ni avanzar cambios en el código fuente sin emplear el ciclo OPSX**:
  - **REGLA DE BLOQUEO**: Si un colaborador o agente intenta realizar o aplicar modificaciones directas sin pasar por el flujo formal de OpenSpec (`/opsx:propose` → `/opsx:apply` → `/opsx:archive`), **NO SE LE DEBE DEJAR AVANZAR CON SUS CAMBIOS**. Se debe frenar la ejecución inmediatamente y exigir que la funcionalidad o corrección sea especificada, planificada y ejecutada dentro de un change de OPSX activo.

### 2. Restricciones de Dominio y Datos (UTN Programación III)
- **NUNCA usar `float` para dinero o importes monetarios** → Usar siempre `Decimal` en Python y `NUMERIC(10,2)` / `NUMERIC(12,2)` en SQLModel/PostgreSQL.
- **NUNCA renombrar ni quitar tablas o columnas obligatorias** → Respetar exactamente los nombres dados en `knowledge-base/04_modelo_de_datos.md` (`editorial`, `genero`, `autor`, `libro`, `libro_autor`, `cliente`, `perfil_cliente`, `venta`, `renglon_venta`).
- **NUNCA omitir índices en claves foráneas** → Toda Foreign Key debe llevar su correspondiente índice (`index=True`) y navegación bidireccional con `Relationship(back_populates=...)`.
- **NUNCA consultar con un `if exists` previo antes de persistir una relación** → En las altas (libro, venta), persistir directamente y dejar que PostgreSQL valide la clave foránea. Si falla, capturar la excepción y responder HTTP 409.
- **NUNCA exponer texto interno de base de datos ni trazas al cliente (RN-12)** → Interceptar `IntegrityError` y retornar un mensaje propio y limpio en formato JSON con código HTTP 409.
- **NUNCA caer en consultas con carga perezosa o problema N+1** → Toda relación leída se precarga explícitamente en la consulta: `joinedload` para relaciones a uno y `selectinload` para colecciones.
- **NUNCA ejecutar operaciones bloqueantes en los handlers** → Todos los handlers deben ser `async def`. Tareas secundarias como el comprobante de venta se ejecutan vía `BackgroundTasks` (`asyncio.sleep(0.5)`).

### 3. Restricciones de Empaquetado y Seguridad
- **NUNCA usar una imagen Docker distinta a `python:3.12-alpine`** → La imagen base debe pesar menos de 100 MB.
- **NUNCA ejecutar el contenedor como `root`** → Crear un usuario sin privilegios (`appuser`) y activarlo con `USER`.
- **NUNCA incluir secretos en el repositorio, la imagen o el zip** → `DATABASE_URL` y credenciales se inyectan en tiempo de ejecución vía `--env-file`.
- **NUNCA usar `localhost` para el HEALTHCHECK en Alpine** → Usar `127.0.0.1` para evitar problemas con la resolución IPv6 de `wget`.

---

## Flujo de Trabajo

```
1. Leer la KB relevante (knowledge-base/)               → Entender dominio y reglas
2. Identificar el change en CHANGES.md                  → Respetar orden y dependencias
3. /opsx:propose <nombre-change>                       → Generar proposal, design, specs y tasks
4. /opsx:apply <nombre-change>                          → Implementar con TDD estricto
5. Verificar casos de prueba mínimos                    → .http en test/ y evidencia en VPS
6. /opsx:archive <nombre-change>                        → Sincronizar specs y cerrar change
```
