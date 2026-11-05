# 11 — Despliegue en el VPS y Casos de Prueba

Este documento complementario detalla la configuración del contenedor Docker, los comandos operativos de ejecución y la matriz de casos de prueba exigidos por la cátedra.

---

## 1. Especificación del Contenedor Docker

- **Imagen Base**: `python:3.12-alpine` (estrictamente verificada < 100 MB).
- **Seguridad**:
  - Creación de usuario sin privilegios:
    ```dockerfile
    RUN adduser -D -u 1000 appuser
    USER appuser
    ```
  - Cacheo eficiente de dependencias: se copia e instala `requirements.txt` con `--no-cache-dir` antes de copiar el código fuente.
  - Ningún secreto ni archivo `.env` dentro de la imagen (`.dockerignore`).
- **Comando de inicio**:
  ```dockerfile
  CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
  ```
- **HEALTHCHECK en Dockerfile**:
  ```dockerfile
  HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -qO- http://127.0.0.1:8000/health/ready || exit 1
  ```

---

## 2. Comandos Operativos de Despliegue

### Construcción de la imagen:
```bash
docker build -t libreria .
```

### Ejecución en el VPS:
```bash
docker run -d \
  --name libreria \
  -p <puerto>:8000 \
  --restart unless-stopped \
  --env-file <archivo-de-variables> \
  libreria
```

### Carga de datos iniciales en el contenedor:
```bash
docker exec libreria python -m app.seed
```

---

## 3. Matriz de Casos de Prueba

### Pruebas de API (`test/*.http`)
- **C-01**: Parámetro de ruta no entero (ej. `/libros/abc`) → `422`, sin ejecutar el handler.
- **C-02**: ISBN o email repetido → `409` con mensaje propio.
- **C-03**: Segundo perfil para el mismo cliente (`POST /clientes/{id}/perfil`) → `409`.
- **C-04**: Libro con editorial o autor inexistente → `409` con mensaje propio.
- **C-05**: Venta con libro o cliente inexistente → `409`.
- **C-06**: Venta válida con dos renglones → `201`, renglones creados, precios copiados y total calculado.
- **C-07**: Detalle de libro y venta → Cantidad fija de consultas en consola con `SQL_ECHO=true`.
- **C-08**: Búsqueda por título con `' OR '1'='1` → `200` con lista vacía (sin inyección).

### Pruebas y Evidencias de Despliegue (`evidencia/`)
- **D-01**: `docker images` demostrando `python:3.12-alpine` < 100 MB.
- **D-02**: Servidor limpio: `docker build` + `docker run` + `docker ps` en estado `healthy` y logs con tablas creadas.
- **D-03**: Prueba desde afuera del VPS en URL pública: `GET /health/ready`, `GET /libros/` y `POST /ventas/` (C-06).
- **D-04**: Reinicio del contenedor (`docker rm -f libreria` y relanzamiento): datos persisten en la DB del servidor y `create_all` no rompe nada.
- **D-05**: Ejecución sin `DATABASE_URL`: el contenedor falla y se detiene (no queda sirviendo sin base).
- **D-06**: `docker exec libreria id`: usuario no es root (UID != 0).
- **D-07**: Verificación de log: el aviso en segundo plano de `POST /ventas/` aparece después de la línea de respuesta HTTP.
