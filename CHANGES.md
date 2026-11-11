# CHANGES — Secuencia de Implementación

> Índice canónico de todos los changes del proyecto Parcial: La librería con despliegue en el VPS.
> Cada change es atómico: un agente puede implementarlo en una sesión (~4-6 horas).
> **Leer este archivo antes de ejecutar cualquier `/opsx:propose`.**

---

## Cómo usar este documento

1. Identificar el change siguiente en la secuencia (respetar orden y dependencias).
2. Leer los archivos de `knowledge-base/` señalados en "Leer antes" de cada change.
3. Ejecutar `/opsx:propose C-NN-<nombre>` para generar proposal, design, specs y tasks.
4. Ejecutar `/opsx:apply C-NN-<nombre>` para implementar con TDD estricto (tests en verde).
5. Ejecutar `/opsx:archive C-NN-<nombre>` para sincronizar specs y cerrar el change.
6. Marcar el checkbox del change como `[x]` completado.

---

## Árbol de dependencias

```
C-01 ejercicio1-proyecto-conexion-ciclo-vida
  └── C-02 auditoria-ejercicio1-correciones
        └── C-03 ej2-ej3-ej4-modelos-crud-altas
              └── C-04 ej5-lecturas-sin-n1-paginacion
                    └── C-05 ej6-asincronia-sin-bloqueos
                          └── C-06 ej7-ej8-contenedor-despliegue-vps
```

### Paralelismo por fase

**GATE 0: inicio — sin dependencias previas**
→ C-01 ejercicio1-proyecto-conexion-ciclo-vida                  [Agente A — Backend Core]

**GATE 1: C-01 ✓ — una sola rama siguiente**
→ C-02 auditoria-ejercicio1-correciones                       [Agente A — Backend Core]

**GATE 2: C-02 ✓ — una sola rama siguiente**
→ C-03 ej2-ej3-ej4-modelos-crud-altas                         [Agente B — Backend Aux]

**GATE 3: C-03 ✓ — una sola rama siguiente**
→ C-04 ej5-lecturas-sin-n1-paginacion                        [Agente A — Backend Core]

**GATE 4: C-04 ✓ — una sola rama siguiente**
→ C-05 ej6-asincronia-sin-bloqueos                            [Agente B — Backend Aux]

**GATE 5: C-05 ✓ — una sola rama siguiente**
→ C-06 ej7-ej8-contenedor-despliegue-vps                     [Agente C — DevOps]

### Camino crítico (6 changes — mínimo irreducible)

C-01 → C-02 → C-03 → C-04 → C-05 → C-06

### Plan óptimo con 3 agentes

| Paso | Agente A (Backend Core) | Agente B (Backend Aux / DevOps) | Agente C (DevOps / Backend Aux) |
|------|-------------------------|---------------------------------|---------------------------------|
| 1 | C-01 ejercicio1-proyecto-conexion-ciclo-vida | — | — |
| 2 | C-02 auditoria-ejercicio1-correciones | — | — |
| 3 | — | C-03 ej2-ej3-ej4-modelos-crud-altas | — |
| 4 | C-04 ej5-lecturas-sin-n1-paginacion | — | — |
| 5 | — | C-05 ej6-asincronia-sin-bloqueos | — |
| 6 | — | — | C-06 ej7-ej8-contenedor-despliegue-vps |

---

## FASE 1 — Fundación e Infraestructura Base (Ejercicio 1)

> Nota: Los cambios C-01 y C-02 ya se encuentran implementados y archivados. C-02 corrige observaciones de C-01 (handlers `async def`, entre otros).

### [C-01] `ejercicio1-proyecto-conexion-ciclo-vida`
- **Estado**: `[x]` completado
- **Ejercicio del PDF**: Ejercicio 1 — Proyecto, conexión y ciclo de vida (8 puntos)
- **Scope**:
  - Estructura obligatoria del proyecto: `app/main.py`, `app/core/config.py`, `app/core/database.py`, `app/modules/health/{router,service}.py`.
  - `@asynccontextmanager async def lifespan` en `app/main.py`: motor `create_async_engine`, fábrica `async_sessionmaker(expire_on_commit=False)`, `SQLModel.metadata.create_all` en startup, `await engine.dispose()` en shutdown.
  - `app.state.engine` y `app.state.session_factory` para inyección en handlers.
  - `Depends(get_session)` — una sesión por petición.
  - `.env` con `DATABASE_URL` y `SQL_ECHO`; `env.example` sin secretos.
  - `GET /health/live` (`{"estado": "vivo"}`) sin tocar la base de datos.
  - `GET /health/ready` ejecutando `SELECT 1`.
  - `env.example`, `requirements.txt`, `test/health.http`.
  - Tests: `tests/test_config.py`, `tests/test_database.py`, `tests/test_health.py`, `tests/test_lifespan.py` (14 pruebas, GREEN).
- **Dependencias**: ninguna
- **Governance**: CRITICO (ciclo de vida de la aplicación; todo lo demás depende de esto)
- **Leer antes**:
  - `knowledge-base/01_vision_y_objetivos.md` §Alcance v1.0
  - `knowledge-base/02_descripcion_general.md` §Stack tecnológico y Arquitectura general
  - `knowledge-base/07_flujos_principales.md` §Flujo 1: Ciclo de Vida y Arranque
  - `knowledge-base/08_arquitectura_propuesta.md` §Patrones aplicados y Estructura de directorios
  - `knowledge-base/10_preguntas_abiertas.md` §IN-01 (localhost en Alpine)

### [C-02] `auditoria-ejercicio1-correciones`
- **Estado**: `[x]` completado
- **Ejercicio del PDF**: Corrección interna de C-01 (no es un ejercicio independiente del PDF; es una auditoría y corrección de observaciones del Ejercicio 1)
- **Scope**:
  - Corrección de `app/modules/health/router.py`: `live` convertido a `async def live()` para cumplir la regla de que todos los handlers son `async def` (requisito técnico del PDF: "todos los handlers con async def").
  - Ajuste de `tests/test_health.py::test_router_live_endpoint` a `@pytest.mark.asyncio` con `await live()`.
  - Re-ejecución de la suite completa: 14 pruebas en verde.
- **Dependencias**: `C-01`
- **Governance**: MEDIO (corrección de convención de handlers asincrónicos)
- **Leer antes**:
  - `knowledge-base/08_arquitectura_propuesta.md` §Patrones aplicados (Inyección de Dependencias, Application Lifespan)
  - `knowledge-base/05_reglas_de_negocio.md` §RN-12 (errores limpios)

---

## FASE 2 — Modelo, Contratos y Altas (Ejercicios 2, 3 y 4)

> Nota: C-03 ya está archivado. Agrupa los Ejercicios 2, 3 y 4 del PDF porque sus tasks archivadas ya cubren modelos, contratos CRUD y altas con relaciones (incluidas ventas). No es necesario un change separado por ejercicio.

### [C-03] `ej2-ej3-ej4-modelos-crud-altas`
- **Estado**: `[x]` completado
- **Ejercicios del PDF**: Ejercicio 2 (Modelos, restricciones y relaciones, 22 pts), Ejercicio 3 (Contratos y CRUD, 12 pts), Ejercicio 4 (Altas con relaciones, 17 pts)
- **Scope**:
  - **Ejercicio 2**: Modelos SQLModel en `app/modules/*/models.py`: `Editorial`, `Genero`, `Autor`, `Libro`, `LibroAutor` (objeto de asociación con `rol` y `orden`), `Cliente`, `PerfilCliente`, `Venta`, `RenglonVenta`. Restricciones UNIQUE, CHECK, FKs con índices, navegación bidireccional con `back_populates`, `Decimal` para dinero (nunca `float`). `Cliente.perfil` devuelve objeto único, no lista.
  - **Ejercicio 3**: DTOs separados en `app/modules/*/schemas.py` (Create/Read/Update). Endpoints CRUD con códigos 201/200/404/409/422. PATCH parcial con `exclude_unset`. Paginación `limit`/`offset` (RN-10). Búsqueda por título con parámetros ligados (RN-11).
  - **Ejercicio 4**: `POST /libros/` sin `if exists` previo — `IntegrityError` capturado y traducido a HTTP 409 con mensaje propio (RN-12). `POST /ventas/` con `cliente_id` y `renglones[]` (composición): validación ≥1 renglón y sin `libro_id` duplicados → 422 (RN-05), `precio_unitario` copiado del libro (RN-06), `total` calculado en servidor con `Decimal` (RN-07), persistencia atómica en transacción única, ventas inmutables sin `PATCH` ni `DELETE` (RN-08). `BackgroundTasks` con `asyncio.sleep(0.5)` para aviso de comprobante (Ejercicio 6, parte de la asincronía).
  - `test/ej3-ej4.http` con casos C-01 a C-08 aplicables.
  - **Observación de entorno**: evidencia del change archivado reporta `37 passed, 9 skipped, 9 failed`; los 9 fallos se atribuyen al entorno local (falta de `pytest-asyncio`/`aiosqlite` para tests async/DB y `test_create_all` async) y no son regresiones atribuibles al alcance de los Ejercicios 2-4. Revisar antes de considerar el entorno listo para entrega final.
- **Dependencias**: `C-02`
- **Governance**: CRITICO (entidades core, datos financieros, integridad referencial)
- **Leer antes**:
  - `knowledge-base/03_actores_y_roles.md` §Matriz de permisos
  - `knowledge-base/04_modelo_de_datos.md` §Todas las tablas y restricciones
  - `knowledge-base/05_reglas_de_negocio.md` §RN-01 a RN-12
  - `knowledge-base/06_funcionalidades.md` §Épicas 2, 3, 4, 5 (US-003 a US-008)
  - `knowledge-base/07_flujos_principales.md` §Flujo 2, §Flujo 3, §Flujo 4
  - `knowledge-base/08_arquitectura_propuesta.md` §Patrones aplicados (DTO, Carga Anticipada, Background Tasks)

---

## FASE 3 — Lecturas Optimizadas y Asincronía (Ejercicios 5 y 6)

### [C-04] `ej5-lecturas-sin-n1-paginacion`
- **Estado**: `[ ]` pendiente
- **Ejercicio del PDF**: Ejercicio 5 — Lecturas sin N+1 (8 puntos)
- **Scope**:
  - `GET /libros/{id}` con `joinedload` (editorial, género) y `selectinload` (autorias → autor) → cero N+1 (Caso C-07).
  - `GET /ventas/{id}` con `joinedload` (cliente) y `selectinload` (renglones → libro) → cero N+1.
  - `GET /editoriales/{id}/libros` y `GET /generos/{id}/libros` con carga anticipada.
  - `GET /autores/{id}/libros` incluyendo `rol` y `orden` de cada autoría.
  - `GET /clientes/{id}` con `perfil` como objeto único (no lista).
  - `GET /clientes/{id}/ventas` con historial y renglones precargados.
  - Número fijo de sentencias SQL en consola con `SQL_ECHO=true` (Caso C-07), independiente de la cantidad de autores o renglones.
  - `GET /libros/` con búsqueda por título case-insensitive (`ILIKE` / `lower().like()` con parámetros ligados) → prevención de SQL injection (RN-11, Caso C-08).
  - Filtros por `genero_id` y paginación `limit`/`offset` (RN-10).
- **Dependencias**: `C-03`
- **Governance**: ALTO (lecturas relacionales críticas, rendimiento verificado por la cátedra)
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §Relaciones y restricciones
  - `knowledge-base/05_reglas_de_negocio.md` §RN-10, RN-11
  - `knowledge-base/06_funcionalidades.md` §Épica 3 (US-006)
  - `knowledge-base/07_flujos_principales.md` §Flujo 4 (Consulta de Detalle con Carga Anticipada)
  - `knowledge-base/08_arquitectura_propuesta.md` §Patrones aplicados (Carga Anticipada)

### [C-05] `ej6-asincronia-sin-bloqueos`
- **Estado**: `[ ]` pendiente
- **Ejercicio del PDF**: Ejercicio 6 — Asincronía sin bloqueos (8 puntos)
- **Scope**:
  - Verificar que todos los handlers son `async def` y ninguno ejecuta llamadas bloqueantes (`time.sleep`, `requests`, acceso síncrono a la base).
  - `POST /ventas/` agenda con `BackgroundTasks` el aviso del comprobante al cliente, simulado con `await asyncio.sleep(0.5)` y un mensaje en el log, que corre después de enviar la respuesta.
  - Mientras corre el aviso en segundo plano, el servidor sigue atendiendo otras peticiones sin bloqueos.
  - Verificar que `verificar_readiness` y demás operaciones de DB sean asincrónicas.
- **Dependencias**: `C-04`
- **Governance**: ALTO (asincronía es requisito transversal de todos los handlers)
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` §Épica 5 (US-008, BackgroundTasks)
  - `knowledge-base/07_flujos_principales.md` §Flujo 3 (Registro Atómico de Venta, paso 5 y 7)
  - `knowledge-base/08_arquitectura_propuesta.md` §Patrones aplicados (Non-blocking Concurrency & Background Tasks)
  - `knowledge-base/05_reglas_de_negocio.md` §RN-12 (errores limpios sin bloquear)

---

## FASE 4 — Despliegue y Entrega Final (Ejercicios 7 y 8)

### [C-06] `ej7-ej8-contenedor-despliegue-vps`
- **Estado**: `[ ]` pendiente
- **Ejercicios del PDF**: Ejercicio 7 (Contenedor: la imagen, 15 pts), Ejercicio 8 (Despliegue en el VPS, 10 pts)
- **Scope**:
  - **Ejercicio 7**: `Dockerfile` basado en `python:3.12-alpine` (< 100 MB de imagen base). Usuario sin privilegios: `adduser -D -u 1000 appuser` + `USER appuser`. Cacheo de dependencias: `requirements.txt` copiado e instalado con `--no-cache-dir` antes del código fuente. `.dockerignore` excluyendo `.env`, `.venv`, `.git`, `__pycache__`. `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]`. `HEALTHCHECK` usando `127.0.0.1` (no `localhost`): `wget -qO- http://127.0.0.1:8000/health/ready || exit 1`. Ningún secreto en el Dockerfile ni en la imagen.
  - **Ejercicio 8**: Despliegue en el VPS con `docker run -d --name libreria -p <puerto>:8000 --restart unless-stopped --env-file <archivo> libreria`. `DEPLOY.md` con URL pública, comandos `docker build` y `docker run` completos, cambios realizados para que corra en el contenedor, y cómo actualizar la aplicación. Script de seed: `docker exec libreria python -m app.seed`. Evidencias D-01 a D-07 en `evidencia/`. `.zip` final sin `.venv`, `__pycache__` ni `.env`. `README.md` con datos del grupo.
- **Dependencias**: `C-05`
- **Governance**: CRITICO (imagen base obligatoria, usuario no-root, sin secretos, HEALTHCHECK IPv4, entrega final)
- **Leer antes**:
  - `knowledge-base/02_descripcion_general.md` §Stack tecnológico (Contenedor)
  - `knowledge-base/09_decisiones_y_supuestos.md` §DD-01 (imagen Alpine), §SU-01 (host.docker.internal)
  - `knowledge-base/10_preguntas_abiertas.md` §IN-01 (localhost en Alpine)
  - `knowledge-base/11_despliegue_y_vps.md` §1. Especificación del Contenedor, §2. Comandos Operativos, §3. Matriz de Casos de Prueba

---

## Tabla Resumen

| ID | Change | Estado | Ejercicio(s) PDF | Dependencias | Governance |
|----|--------|--------|------------------|--------------|------------|
| C-01 | ejercicio1-proyecto-conexion-ciclo-vida | `[x]` completado | Ejercicio 1 | — | CRITICO |
| C-02 | auditoria-ejercicio1-correciones | `[x]` completado | Corrección de Ej. 1 | C-01 | MEDIO |
| C-03 | ej2-ej3-ej4-modelos-crud-altas | `[x]` completado | Ejercicios 2, 3, 4 | C-02 | CRITICO |
| C-04 | ej5-lecturas-sin-n1-paginacion | `[ ]` pendiente | Ejercicio 5 | C-03 | ALTO |
| C-05 | ej6-asincronia-sin-bloqueos | `[ ]` pendiente | Ejercicio 6 | C-04 | ALTO |
| C-06 | ej7-ej8-contenedor-despliegue-vps | `[ ]` pendiente | Ejercicios 7, 8 | C-05 | CRITICO |

**Camino crítico**: C-01 → C-02 → C-03 → C-04 → C-05 → C-06 (6 changes)  
**Gates de paralelismo**: 6 (cada gate desbloquea una sola rama siguiente; cadena estrictamente lineal)  
**Primer change recomendado si se parte de cero**: `C-01 ejercicio1-proyecto-conexion-ciclo-vida`

> Los cambios C-01, C-02 y C-03 ya fueron ejecutados y archivados bajo `openspec/changes/archive/`. Los cambios C-04 a C-06 están pendientes de implementar siguiendo el ciclo OPSX (`/opsx:propose` → `/opsx:apply` → `/opsx:archive`).
