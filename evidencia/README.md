# Evidencia — Ejercicio 7 (contenedor)

En esta carpeta se guardan las salidas de consola de los casos **D** que
corresponden a la imagen y al contenedor. Reemplazar cada archivo de ejemplo por
la salida real, copiada de la terminal (sin editar a mano).

| Archivo | Caso | Comando | Resultado esperado |
|---|---|---|---|
| `D-01-docker-images.txt` | D‑01 | `docker images` (o el `--format` de abajo) | `python:3.12-alpine` < 100 MB y la imagen `libreria` construida a partir de ella |
| `D-02-build-run-ps.txt` | D‑02 | `docker build`, `docker run`, `docker ps`, `docker logs` | Contenedor `(healthy)` y arranque completo con el esquema creado |
| `D-05-sin-database-url.txt` | D‑05 | `docker run` sin `--env-file` | El contenedor termina con error; no queda sirviendo |
| `D-06-usuario-root.txt` | D‑06 | `docker exec libreria id` | UID distinto de 0 (`uid=1000(appuser)`) |

## Comandos para capturar

```bash
# D-01
docker images --format 'table {{.Repository}}:{{.Tag}}\t{{.Size}}'
docker image inspect python:3.12-alpine --format '{{.Size}} bytes'

# D-02
docker build -t libreria .
docker run -d --name libreria -p <PUERTO_ASIGNADO>:8000 \
  --restart unless-stopped --env-file ~/libreria.env libreria
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
docker logs libreria

# D-05  (sin --env-file: debe fallar y terminar)
docker run --rm --name libreria-sin-env -p 8001:8000 libreria
echo "exit code: $?"

# D-06
docker exec libreria id
```

> El estado `healthy` puede tardar hasta ~50 s: `--start-period=20s` más el
> primer intervalo de 30 s del `HEALTHCHECK`. Verificar con:
> `docker inspect --format '{{.State.Health.Status}}' libreria`.
