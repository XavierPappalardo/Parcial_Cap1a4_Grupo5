# 06 — Funcionalidades

Las funcionalidades del sistema están estructuradas en historias de usuario organizadas por módulo/ejercicio.

---

## Épica 1: Ciclo de Vida, Salud y Conexión (Ejercicio 1)

### US-001 — Healthcheck de Liveness
**Como** orquestador de contenedores o evaluador  
**Quiero** consultar `GET /health/live`  
**Para** verificar inmediatamente que el proceso del servidor ASGI está respondiendo sin interactuar con la base de datos.

- **Criterios de Aceptación**:
  - Responde código HTTP 200 con JSON `{"estado": "vivo"}`.
  - No ejecuta ninguna consulta ni abre sesión hacia PostgreSQL.

### US-002 — Healthcheck de Readiness y Verificación de DB
**Como** Docker HEALTHCHECK o administrador de infraestructura  
**Quiero** consultar `GET /health/ready`  
**Para** certificar que la aplicación está lista para atender tráfico y que la conexión asincrónica con PostgreSQL es operativa.

- **Criterios de Aceptación**:
  - Ejecuta la sentencia asincrónica `SELECT 1` sobre la sesión de base de datos.
  - Responde HTTP 200 si la base responde. Si la base no está disponible, falla con código 500 o error de conexión.

---

## Épica 2: Catálogo de Autores, Editoriales y Géneros (Ejercicios 2 y 3)

### US-003 — Gestión de Editoriales y Géneros
**Como** personal de la librería  
**Quiero** registrar y listar editoriales y géneros  
**Para** clasificarlos y vincularlos a los libros del catálogo.

- **Criterios de Aceptación**:
  - `POST /editoriales/` valida nombre único (responde 201 o 409).
  - `POST /generos/` valida nombre único (responde 201 o 409).
  - Paginación implementada en listados de editoriales con `limit` (1-100) y `offset` (>=0).
  - Endpoints `GET /editoriales/{id}/libros` y `GET /generos/{id}/libros` retornan los libros correspondientes o 404 si el id no existe.

### US-004 — Gestión de Autores y sus Libros
**Como** personal de la librería  
**Quiero** dar de alta autores y consultar su bibliografía  
**Para** mantener el registro de autorías con sus respectivos roles y orden.

- **Criterios de Aceptación**:
  - `POST /autores/` crea un autor con nombre y nacionalidad (responde 201).
  - `GET /autores/{id}/libros` retorna la lista de libros en los que participó el autor, incluyendo el `rol` ('autor', 'coautor', 'traductor', 'ilustrador') y el `orden` numérico.

---

## Épica 3: Libros y Altas con Relaciones (Ejercicios 3, 4 y 5)

### US-005 — Alta de Libro con Relaciones Múltiples
**Como** personal de la librería  
**Quiero** registrar un nuevo libro asociando IDs de editorial, género y una lista de autores con rol y orden  
**Para** que el libro quede completamente catalogado en una sola transacción.

- **Criterios de Aceptación**:
  - DTO de entrada recibe `isbn`, `titulo`, `precio`, `stock`, `editorial_id`, `genero_id` (opcional) y `autores: list[AutorLibroItem]`.
  - El sistema **no hace SELECT previo** para verificar si la editorial o los autores existen: inserta directamente en la base y delega la integridad en las FKs.
  - Si la base rechaza una clave foránea por id inexistente, la aplicación responde HTTP 409 con mensaje limpio (RN-12).
  - Si el ISBN ya existe, responde HTTP 409.
  - La respuesta exitosa (201) devuelve el detalle completo del libro con sus relaciones anidadas.

### US-006 — Búsqueda y Lectura de Libros sin N+1
**Como** cliente o vendedor  
**Quiero** buscar libros por título y consultar el detalle de un libro  
**Para** conocer toda la información sin degradar el rendimiento de la base de datos.

- **Criterios de Aceptación**:
  - `GET /libros/?titulo=...` realiza búsqueda case-insensitive con parámetros ligados (RN-11), sanitizando inyecciones SQL (Caso C-08).
  - Paginación obligatoria según RN-10.
  - `GET /libros/{id}` carga anticipadamente la editorial y género con `joinedload`, y las autorías/autores con `selectinload`.
  - El número de sentencias SQL emitidas a la consola es fijo e independiente de la cantidad de autores vinculados (Caso C-07).

---

## Épica 4: Clientes y Perfiles (Ejercicios 2 y 3)

### US-007 — Registro de Cliente y Perfil 1 a 1
**Como** cliente  
**Quiero** registrarme con mi email y opcionalmente cargar mi dirección y teléfono  
**Para** recibir compras en mi domicilio.

- **Criterios de Aceptación**:
  - `POST /clientes/` crea cliente con email único (201 / 409).
  - `GET /clientes/{id}` devuelve el cliente con su atributo `perfil` como objeto único (o `null`), **nunca como lista**.
  - `POST /clientes/{id}/perfil` crea el perfil del cliente. Si ya poseía un perfil previo, se rechaza con HTTP 409 (RN-09, Caso C-03).

---

## Épica 5: Ventas y Comprobantes en Segundo Plano (Ejercicios 4, 5 y 6)

### US-008 — Registro Atómico de Venta y Aviso en Background
**Como** operador de la librería  
**Quiero** emitir una venta enviando el id del cliente y la lista de renglones (libro_id y cantidad)  
**Para** registrar la operación de forma consistente y notificar al cliente sin bloquear la respuesta.

- **Criterios de Aceptación**:
  - El cuerpo de `POST /ventas/` incluye `cliente_id` y `renglones: list[RenglonItem]`. No viajan fecha, precio unitario ni total.
  - Valida que haya al menos 1 renglón y que no haya `libro_id` repetidos (HTTP 422, RN-05).
  - Consulta el precio de cada libro en la DB y lo copia a `precio_unitario` (RN-06).
  - Calcula el `total` sumando los subtotales (RN-07).
  - Si el cliente o alguno de los libros no existe, la base de datos rechaza la FK y el servicio devuelve HTTP 409 (Caso C-05).
  - Persiste atómicamente la venta y los renglones (composición).
  - Agenda en `BackgroundTasks` la tarea asincrónica de notificación simulada (`await asyncio.sleep(0.5)` y log posterior a la respuesta).
  - Responde HTTP 201 con la venta, el cliente y los renglones (incluyendo títulos, precios y subtotales).
