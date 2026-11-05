# 10 — Preguntas Abiertas

## Inconsistencias o tensiones técnicas analizadas

### IN-01 — Redirección de localhost en Alpine para el HEALTHCHECK
- **Tensión**: En Alpine Linux no viene instalado `curl` por defecto. Al usar `wget` contra `http://localhost:8000/health/live`, `wget` resuelve primero `localhost` a `::1` (IPv6), mientras que Uvicorn con `--host 0.0.0.0` escucha exclusivamente en IPv4.
- **Impacto**: Docker reportaría el contenedor como `unhealthy` aunque el servidor esté funcionando y respondiendo desde afuera.
- **Resolución adoptada**: El comando `HEALTHCHECK` del `Dockerfile` debe usar explícitamente la dirección IPv4 literal:  
  `wget -qO- http://127.0.0.1:8000/health/live || exit 1`

---

## Preguntas abiertas (priorizadas)

| Prioridad | Pregunta | Bloquea | Decisor | Estado |
|---|---|---|---|---|
| **Media** | ¿Qué credenciales y puerto específico asignará la cátedra en el VPS para el grupo? | Despliegue final en el servidor remoto | Cátedra / Usuario | Pendiente de entrega por la cátedra (parametrizado vía `.env`) |
| **Baja** | ¿Cuál es la nómina completa de integrantes del grupo para colocar en el `README.md`? | Entrega final del `.zip` | Usuario | El usuario confirmó que completará estos datos personalmente |
| **Baja** | ¿Se proveerá un script CLI para la carga de datos iniciales o se ejecuta vía endpoint / archivo SQL? | Caso D-03 / inicialización | Equipo de desarrollo | Resuelto: se creará un script Python ejecutable con `docker exec libreria python -m app.seed` |
