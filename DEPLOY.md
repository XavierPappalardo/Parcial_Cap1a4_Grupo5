# DEPLOY.md — Imagen Docker y despliegue en el VPS

> Proyecto: **Librería API** — Programación III, Parcial Capítulos 1 a 4.
> Este documento cubre el **Ejercicio 7 (contenedor: la imagen)**. Los datos del
> **Ejercicio 8** (URL pública, fecha y hora exactas del despliegue, puerto asignado
> y evidencia real de los casos D) se completan al poner la imagen en línea.

| Dato | Valor |
|---|---|
| Imagen base | `python:3.12-alpine` (74,8 MB verificada localmente con Docker 29.9.3; 74,7 MB según la medición de la cátedra con Docker 29.2; límite: 100 MB) |
| Imagen del proyecto | `libreria` |
| Contenedor | `libreria` |
| Archivo de variables en el servidor | `~/libreria.env` (no se versiona ni se incluye en la imagen) |
| Puerto interno | `8000` |
| Puerto publicado | `<PUERTO_ASIGNADO>` — lo define la cátedra (en los ejemplos se usa `8000`) |
| URL pública | _Pendiente de completar en el Ejercicio 8_ |
| Día y hora del despliegue | _Pendiente de completar en el Ejercicio 8_ |

---

## 1. Decisiones de la imagen y su justificación

| Decisión | Implementación | Razón |
|---|---|---|
| Imagen base mínima | `FROM python:3.12-alpine` | Ocupa 74,7 MB en disco (medido con Docker 29.2); `python:3.12-slim` ocupa 180 MB y no cumple el límite de 100 MB. Alpine no trae paquetes de sistema que la aplicación no usa: cada uno es superficie de ataque. |
| Capas en orden | `COPY requirements.txt` + `pip install` **antes** de `COPY app` | Mientras las dependencias no cambien, la capa de instalación sale de caché y un cambio de código no reinstala todo. |
| Sin caché de pip | `pip install --no-cache-dir -r requirements.txt` | No deja ruedas ni temporales dentro de la imagen. |
| Usuario sin privilegios | `addgroup -S -g 1000 app && adduser -S ... -u 1000 appuser` + `USER 1000:1000` | Si vulneran la aplicación, el proceso no es dueño del contenedor. El código se copia con `--chown=appuser:app`. |
| Sin secretos | `.dockerignore` excluye `.env`, `.venv`, `.git` y `__pycache__`; el Dockerfile no contiene `DATABASE_URL` ni contraseñas | Lo que se hornea en una capa queda para siempre, aunque una capa posterior lo borre. La configuración entra al correr el contenedor con `--env-file`. |
| Escucha en `0.0.0.0` | `uvicorn app.main:app --host 0.0.0.0 --port 8000` | Dentro del contenedor, `127.0.0.1` sólo se alcanza desde el propio contenedor: el puerto publicado nunca respondería. |
| Tablas al arrancar | El `lifespan` de `app/main.py` ejecuta `SQLModel.metadata.create_all` | Una base vacía queda lista sin migraciones (fuera de alcance). `create_all` sólo crea las tablas que faltan. |
| Falla si no hay base | Sin `DATABASE_URL`, `Settings` falla y el arranque termina con error | Una aplicación que no llega a su base no debe quedar atendiendo (caso D‑05). |
| `HEALTHCHECK` en la imagen | `wget -q -O /dev/null http://127.0.0.1:8000/health/ready` | Sin Compose, la imagen declara su propia salud y `docker ps` muestra `healthy`. Se usa `127.0.0.1`, **no** `localhost`: en Alpine, `wget` resuelve `localhost` a `::1` y uvicorn escucha sólo en IPv4, con lo que el contenedor quedaría `unhealthy` aunque responda desde afuera. |
| Sin Compose | Un solo `docker run` | La base no forma parte del paquete: la provee el servidor. |

### Dockerfile completo

```dockerfile
FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN addgroup -S -g 1000 app \
    && adduser -S -D -H -h /app -G app -u 1000 -s /sbin/nologin appuser

COPY --chown=appuser:app app ./app

USER 1000:1000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD ["wget", "-q", "-O", "/dev/null", "http://127.0.0.1:8000/health/ready"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### `.dockerignore` (resumen)

Excluye `.env` y cualquier `.env.*` local, `.venv/`, `venv/`, `.git/`,
`__pycache__/`, `*.py[cod]`, `.pytest_cache/`, `tests/`, `test/`, `scripts/`,
`evidencia/`, la documentación (`knowledge-base/`, `openspec/`, `discovery/`,
`.agents/`, `.claude/`, `*.md`) y artefactos `.zip`/`.log`. Sólo entran al
contexto de build `requirements.txt` y `app/`.

---

## 2. Construcción de la imagen

Desde la raíz del repositorio (donde está el `Dockerfile`):

```bash
docker build -t libreria .
```

## 3. Ejecución del contenedor

El archivo de variables vive **en el servidor**, fuera del repositorio y de la
imagen. Se llama `libreria.env` y contiene, como mínimo:

```dotenv
# ~/libreria.env  (NO se versiona; este bloque muestra sólo la forma)
DATABASE_URL=postgresql+asyncpg://<usuario>:<password>@<host>:<puerto>/<nombre_base>
SQL_ECHO=false
```

Comando de ejecución:

```bash
docker run -d \
  --name libreria \
  -p <PUERTO_ASIGNADO>:8000 \
  --restart unless-stopped \
  --env-file ~/libreria.env \
  libreria
```

- `-p <PUERTO_ASIGNADO>:8000` publica **sólo** la aplicación, en el puerto que
  asigna la cátedra. El puerto interno no se cambia.
- `--restart unless-stopped` vuelve a levantar el contenedor si el servidor se
  reinicia o si la base todavía no respondía al arrancar.
- `--env-file ~/libreria.env` entrega `DATABASE_URL` (con driver
  `postgresql+asyncpg`) y `SQL_ECHO=false`, que evita escribir cada consulta en
  el registro de producción.

### Si PostgreSQL corre directamente en el host del VPS

Dentro de un contenedor, `localhost` es el propio contenedor. Si la base está en
el servidor, usar `host.docker.internal` en `DATABASE_URL` y agregar:

```bash
--add-host=host.docker.internal:host-gateway
```

Si la cátedra entrega otra dirección de base, se usa esa.

---

## 4. Verificación de la imagen y del contenedor

### D‑01 · Tamaño de la imagen base

```bash
docker images --format 'table {{.Repository}}:{{.Tag}}\t{{.Size}}' python
# python:3.12-alpine   74.8MB      <-- debe ser menor a 100 MB
```

También se puede comprobar en bytes:

```bash
docker image inspect python:3.12-alpine --format '{{.Size}}'
```

### D‑02 · Build, run y estado `healthy`

```bash
docker build -t libreria .
docker run -d \
  --name libreria \
  -p <PUERTO_ASIGNADO>:8000 \
  --restart unless-stopped \
  --env-file ~/libreria.env \
  libreria
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
# libreria   Up 1 minute (healthy)   0.0.0.0:<PUERTO_ASIGNADO>->8000/tcp
docker logs libreria
# ... Uvicorn running on http://0.0.0.0:8000 ...
# ... Application startup complete.        <-- el lifespan terminó: create_all ya corrió
```

El estado pasa a `healthy` cuando el `HEALTHCHECK` obtiene `200` de
`GET /health/ready`. El `--start-period=20s` le da margen a `create_all` en una
base vacía.

Verificación puntual del healthcheck desde dentro (Alpine no trae `curl`):

```bash
docker exec libreria wget -qO- http://127.0.0.1:8000/health/live
# {"estado":"vivo"}
```

### D‑06 · Usuario del proceso

```bash
docker exec libreria id
# uid=1000(appuser) gid=1000(app) groups=1000(app)
```

El UID debe ser distinto de `0`.

### Verificación local de la imagen (registro)

Prueba realizada el 12/11/2026 con Docker Desktop 4.99.0 / Engine 29.9.3 en
Windows, sobre la imagen `libreria:latest` construida con este Dockerfile:

| Comprobación | Resultado |
|---|---|
| `docker build -t libreria .` | OK, sin compilador ni paquetes de sistema extra |
| Tamaño de `python:3.12-alpine` | 74,8 MB (< 100 MB) |
| Tamaño de `libreria:latest` | 258 MB (esperado: la base es la única limitada) |
| `docker run --rm --entrypoint id libreria` | `uid=1000(appuser) gid=1000(app) groups=1000(app)` |
| `docker run` sin `DATABASE_URL` | Termina con error (`Application startup failed. Exiting.`, exit 3); no queda sirviendo |
| `docker run` con PostgreSQL 16 temporal | Contenedor `(healthy)` |
| `GET /health/live` | `200 {"estado":"vivo"}` |
| `GET /health/ready` | `200 {"estado":"listo","database":"conectada"}` |
| Tablas creadas al arrancar | 9 tablas (`editorial`, `genero`, `autor`, `libro`, `libro_autor`, `cliente`, `perfil_cliente`, `venta`, `renglon_venta`) |
| `POST /editoriales/` | `201` y lectura posterior `200` |

Esta verificación es local y no reemplaza los casos D que la consigna pide
capturar sobre el proyecto desplegado en el VPS. La evidencia definitiva
(D‑01 a D‑07) se guarda en `evidencia/` al completar el Ejercicio 8.

---

## 5. Cambios al proyecto para que corra en el contenedor

La lógica de la aplicación **no cambió**. Se agregaron únicamente:

1. `Dockerfile`.
2. `.dockerignore`.

No fue necesario corregir rutas de salud ni el arranque: `GET /health/live`
responde `{"estado":"vivo"}` sin tocar la base y `GET /health/ready` ejecuta
`SELECT 1`. Los modelos se importan desde `app/main.py` (a través de los
routers), por lo que `create_all` ve todas las tablas al arrancar.

Ajustes propios del empaquetado, ninguno funcional:

- `PYTHONDONTWRITEBYTECODE=1`: el usuario `appuser` no escribe `__pycache__` en
  `/app`.
- `PYTHONUNBUFFERED=1`: los logs de uvicorn aparecen en `docker logs` en el
  momento, sin buffering.
- `--start-period=20s` en el `HEALTHCHECK`: evita marcar `unhealthy` mientras
  la aplicación crea el esquema en una base vacía.

---

## 6. Actualización de la aplicación

Los datos no viven en el contenedor, sino en PostgreSQL del servidor, así que
reemplazar la imagen no los pierde.

```bash
# 1. Construir la imagen nueva (mismo tag)
docker build -t libreria .

# 2. Eliminar el contenedor anterior
docker rm -f libreria

# 3. Volver a correrlo con el mismo comando
docker run -d \
  --name libreria \
  -p <PUERTO_ASIGNADO>:8000 \
  --restart unless-stopped \
  --env-file ~/libreria.env \
  libreria
```

`create_all` sólo crea las tablas que faltan; las existentes y sus datos quedan
intactos.

---

## 7. Pendiente para el Ejercicio 8

Al desplegar en el VPS hay que completar en este archivo:

- URL pública y puerto asignado.
- Día y hora del despliegue.
- Confirmación de si la imagen se construyó en el servidor o se transportó.
- Salidas reales de D‑01 a D‑07 en `evidencia/`, incluida la carga de datos
  iniciales con `docker exec libreria …`.
