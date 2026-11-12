# syntax=docker/dockerfile:1
# Imagen del proyecto Librería API (Parcial Cap. 1-4, Ejercicio 7).
# Base obligatoria: python:3.12-alpine (~75 MB, por debajo del límite de 100 MB).
# No se usa Docker Compose ni se incluye PostgreSQL: la base la provee el servidor.

FROM python:3.12-alpine

# Sin .pyc (el usuario de la app no escribe en /app) y logs sin buffer.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# 1) Dependencias primero: si requirements.txt no cambia, esta capa sale de caché
#    y un cambio de código no reinstala nada. --no-cache-dir evita basura en la imagen.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 2) Usuario sin privilegios: si vulneran la app, no son dueños del contenedor.
#    UID/GID fijos (1000) para que el proceso sea identificable fuera de la imagen.
RUN addgroup -S -g 1000 app \
    && adduser -S -D -H -h /app -G app -u 1000 -s /sbin/nologin appuser

# 3) Código de la aplicación, ya con dueño no-root.
COPY --chown=appuser:app app ./app

USER 1000:1000

EXPOSE 8000

# 4) La propia imagen declara su salud (sin Compose). Se usa 127.0.0.1 y no
#    localhost: en Alpine, wget resuelve localhost a ::1 y uvicorn escucha en IPv4.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD ["wget", "-q", "-O", "/dev/null", "http://127.0.0.1:8000/health/ready"]

# 5) 0.0.0.0 es obligatorio dentro del contenedor: con 127.0.0.1 el puerto
#    publicado nunca respondería. La DATABASE_URL entra por --env-file, nunca
#    se hornea en la imagen.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
