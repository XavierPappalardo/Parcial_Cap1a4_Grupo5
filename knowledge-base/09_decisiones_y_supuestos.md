# 09 — Decisiones y Supuestos

## Decisiones documentadas

### DD-01 — Uso de `python:3.12-alpine` para la imagen Docker
- **Decisión**: Utilizar estrictamente `python:3.12-alpine` como imagen base en el `Dockerfile`.
- **Contexto**: La consigna fija un límite estricto de 100 MB para la imagen base descargada en el VPS. `python:3.12-slim` pesa ~180 MB y queda descalificada; `python:3.12-alpine` pesa ~75 MB.
- **Alternativas consideradas**: `python:3.12-slim` (descartada por exceso de tamaño).
- **Justificación**: Cumple el requisito de tamaño mínimo, reduce la superficie de ataque y se verificó que `asyncpg` y `pydantic-core` proveen wheels compatibles con musl sin requerir herramientas de compilación (`gcc`, `make`).
- **Trade-offs**: Manejo de red en Alpine (wget resuelve `localhost` a `::1` IPv6; se resuelve configurando `HEALTHCHECK` explícitamente a `127.0.0.1`).

### DD-02 — Modelo de Autoría como Objeto de Asociación (`LibroAutor`)
- **Decisión**: Modelar la relación muchos a muchos entre `Libro` y `Autor` mediante una clase propia intermedia `LibroAutor`, en lugar de un `link_model` implícito.
- **Contexto**: La relación N:N posee atributos propios significativos: el `rol` del autor en esa obra y su `orden` en la portada.
- **Alternativas consideradas**: `link_model` estándar de SQLModel (descartado porque oculta atributos propios de la relación).
- **Justificación**: Permite almacenar, validar (`CHECK rol IN (...)`, `CHECK orden >= 1`) y consultar estos atributos explícitamente navegando `libro.autorias[i].autor`.

### DD-03 — Carga Anticipada con Estrategias Mixtas (`joinedload` y `selectinload`)
- **Decisión**: Emplear `joinedload` para relaciones a uno (editorial, género, cliente) y `selectinload` para colecciones a muchos (autorías, renglones).
- **Contexto**: La consigna prohíbe terminantemente la carga perezosa (`lazy loading`) y exige que el número de consultas emitidas sea fijo e independiente del volumen de datos (Caso C-07).
- **Justificación**: `joinedload` aprovecha un `LEFT OUTER JOIN` en una sola consulta para entidades 1:1 y N:1, mientras que `selectinload` realiza una segunda consulta indexada con `WHERE id IN (...)` para colecciones, evitando el producto cartesiano masivo de datos.

### DD-04 — Persistencia sin Consultas Previas (`Sin IF de existencia`)
- **Decisión**: En las operaciones de creación (altas de libros y ventas), no consultar con `SELECT` previo si los IDs relacionados existen; persistir directamente y delegar en la base de datos la validación de claves foráneas.
- **Contexto**: Consigna Ejercicio 4: *"En el alta del libro ningún if consulta antes si un id existe: se escribe, y si la base rechaza la clave foránea, se responde 409"*.
- **Justificación**: Ahorra viajes de red innecesarios a la base de datos, previene condiciones de carrera (`check-then-act`) y delega la integridad referencial en quien tiene la verdad absoluta: PostgreSQL.

### DD-05 — Exclusión de Docker Compose y Alembic
- **Decisión**: Prescindir de Docker Compose y de migraciones Alembic.
- **Contexto**: Consigna Ejercicio 1 y 7: el despliegue es en una sola imagen con `docker run`, apuntando a una base PostgreSQL que ya reside en el servidor.
- **Justificación**: El esquema de tablas se genera de forma determinística en el arranque mediante `SQLModel.metadata.create_all`, respetando la consigna que excluye migraciones para este parcial.

---

## Supuestos inferidos

### SU-01 — Entorno de Red Local para Contenedor
- **Supuesto**: Cuando se pruebe la imagen Docker localmente contra un PostgreSQL corriendo en la máquina host, la URL de conexión deberá apuntar a `host.docker.internal` en lugar de `localhost`.
- **Origen**: Sección explicativa de la consigna sobre Docker networking.
- **Riesgo si es falso**: El contenedor arrojaría `Connection refused` al intentar conectar con PostgreSQL local.
- **Cómo validar**: Validar con `--add-host=host.docker.internal:host-gateway` en el comando `docker run` en sistemas Linux/Windows.

### SU-02 — Concurrencia de la Notificación en Segundo Plano
- **Supuesto**: La tarea de aviso en segundo plano es puramente demostrativa (`await asyncio.sleep(0.5)` + log) y no requiere envío real de correos SMTP en este parcial.
- **Origen**: Ejercicio 6 de la consigna.
- **Riesgo si es falso**: Requeriría dependencias y credenciales de un servidor SMTP o servicio de correos externo.
- **Cómo validar**: Se verifica mediante el log de Docker que el mensaje se escriba después de la línea de respuesta HTTP (Caso D-07).
