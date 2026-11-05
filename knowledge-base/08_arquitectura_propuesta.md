# 08 — Arquitectura Propuesta

## Patrones aplicados

| Patrón | Dónde se aplica | Justificación |
|---|---|---|
| **Modular por Funcionalidad (`Package by Feature`)** | Estructura en `app/modules/<módulo>/` | Alta cohesión y bajo acoplamiento: cada dominio encapsula sus modelos, esquemas, servicios y rutas. |
| **DTO (Data Transfer Object)** | `schemas.py` en cada módulo | Separa estrictamente el contrato de entrada/salida de la representación en base de datos. Evita exponer claves primarias o campos internos y permite formateo preciso. |
| **Inyección de Dependencias** | `Depends(get_session)` | FastAPI gestiona el ciclo de vida de la sesión por cada petición HTTP, garantizando su cierre seguro. |
| **Application Lifespan** | `@asynccontextmanager` en `app/main.py` | Inicialización centralizada de recursos asincrónicos (motor, fábrica de sesiones) y liberación limpia al apagar. |
| **Carga Anticipada (`Eager Loading`)** | Consultas en `service.py` con `joinedload` y `selectinload` | Elimina de raíz el problema de rendimiento N+1 en lecturas relacionales. |
| **Non-blocking Concurrency & Background Tasks** | Handlers asincrónicos y `BackgroundTasks` | Garantiza que operaciones como el aviso de comprobante se ejecuten fuera del ciclo de respuesta HTTP sin congelar el hilo ASGI. |

---

## Estructura de directorios obligatoria

```
parcial2-programacion3-grupo5-2PRO1/
├── app/
│   ├── main.py                     # Instancia FastAPI, lifespan, middlewares, inclusión de routers
│   ├── core/
│   │   ├── config.py               # Settings (Pydantic BaseSettings), lectura de DATABASE_URL y SQL_ECHO
│   │   └── database.py             # Engine async, sessionmaker, dependencia get_session
│   └── modules/
│       ├── health/                 # Módulo de salud (/health/live, /health/ready)
│       │   ├── router.py
│       │   └── service.py
│       ├── editoriales/            # Módulo de editoriales
│       │   ├── models.py
│       │   ├── schemas.py
│       │   ├── service.py
│       │   └── router.py
│       ├── generos/                # Módulo de géneros
│       │   ├── models.py
│       │   ├── schemas.py
│       │   ├── service.py
│       │   └── router.py
│       ├── autores/                # Módulo de autores
│       │   ├── models.py
│       │   ├── schemas.py
│       │   ├── service.py
│       │   └── router.py
│       ├── libros/                 # Módulo de libros (incluye LibroAutor)
│       │   ├── models.py           # Libro y LibroAutor
│       │   ├── schemas.py
│       │   ├── service.py
│       │   └── router.py
│       ├── clientes/               # Módulo de clientes (incluye PerfilCliente)
│       │   ├── models.py           # Cliente y PerfilCliente
│       │   ├── schemas.py
│       │   ├── service.py
│       │   └── router.py
│       └── ventas/                 # Módulo de ventas (incluye RenglonVenta)
│           ├── models.py           # Venta y RenglonVenta
│           ├── schemas.py
│           ├── service.py
│           └── router.py
├── test/                           # Archivos .http de prueba (casos C-01 a C-08)
│   ├── health.http
│   ├── editoriales.http
│   ├── generos.http
│   ├── autores.http
│   ├── libros.http
│   ├── clientes.http
│   └── ventas.http
├── evidencia/                      # Capturas y logs de ejecución de pruebas (casos D-01 a D-07)
├── Dockerfile                      # Imagen basada en python:3.12-alpine
├── .dockerignore                   # Exclusión de secretos (.env, .venv, .git, __pycache__)
├── requirements.txt                # Dependencias fijadas
├── env.example                     # Plantilla de variables de entorno sin secretos
├── DEPLOY.md                       # Documentación del despliegue en VPS
└── README.md                       # Instrucciones de levantado local y datos del grupo
```

---

## Seguridad y Manejo de Errores

1. **Gestión de Secretos**:
   - Queda terminantemente prohibido quemar contraseñas o URLs de base de datos en el código fuente, en el `Dockerfile` o en el repositorio Git.
   - En local se usa archivo `.env` (ignorado en `.gitignore`).
   - En el contenedor se inyectan mediante la bandera `--env-file` de Docker al ejecutar `docker run`.
2. **Contenedor sin Privilegios**:
   - El `Dockerfile` crea un usuario del sistema (`appuser` / `UID != 0`) y activa `USER appuser`. La aplicación nunca se ejecuta como `root`.
3. **Manejo de Excepciones de Base de Datos (RN-12)**:
   - Captura centralizada de `IntegrityError` (de `sqlalchemy.exc` o derivado de `asyncpg`).
   - Si se detecta violación de unicidad (`unique_violation`) o clave foránea inexistente (`foreign_key_violation`), se traduce a una respuesta controlada HTTP 409:
     ```json
     {
       "detail": "Conflicto de integridad: el recurso ya existe o referencia una entidad inexistente."
     }
     ```
   - Nunca se retornan trazas de traceback, nombres de índices ni la query SQL fallida al cliente.

---

## Variables de entorno

| Variable | Descripción | Valor por defecto / Ejemplo | Sensible |
|---|---|---|---|
| `DATABASE_URL` | URL de conexión asincrónica hacia PostgreSQL con driver asyncpg. | `postgresql+asyncpg://usuario:password@host:5432/nombre_base` | **SÍ** |
| `SQL_ECHO` | Booleano para activar el volcado de sentencias SQL a la consola (útil para verificar N+1). | `false` (o `true` para diagnóstico) | NO |
| `PORT` | Puerto en el que Uvicorn escucha dentro o fuera del contenedor. | `8000` | NO |
