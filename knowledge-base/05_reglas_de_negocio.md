# 05 — Reglas de Negocio

El sistema implementa 12 reglas de negocio obligatorias (RN-01 a RN-12) estipuladas por la cátedra, con su correspondiente garante arquitectónico y código HTTP esperado.

---

## Dominio: Catálogo y Libros (RN-CAT)

### RN-01 — Unicidad de ISBN
- **Enunciado**: El ISBN de un libro es único en todo el catálogo.
- **Garante esperado**: Restricción `UNIQUE` en la columna `libro.isbn` de la base de datos.
- **Respuesta de error**: HTTP 409 (Conflict) con mensaje propio de la aplicación al detectar violación de unicidad.

### RN-03 — Integridad de Precio y Stock de Libros
- **Enunciado**: El precio de un libro debe ser estrictamente mayor que cero y el stock nunca puede ser negativo.
- **Garante esperado**: 
  - Restricciones en base de datos: `CHECK (precio > 0)` y `CHECK (stock >= 0)`.
  - Validación previa a nivel DTO en Pydantic (`Field(gt=0)` para precio y `Field(ge=0)` para stock).
- **Respuesta de error**: HTTP 422 si falla en el contrato del DTO; HTTP 409 si es rechazado por la base de datos.

### RN-11 — Búsqueda de Libros por Título Insensible a Mayúsculas
- **Enunciado**: El listado de libros se puede filtrar por coincidencia parcial del título, sin distinguir mayúsculas ni minúsculas.
- **Garante esperado**: Consulta SQL con operador `ILIKE` o `lower(libro.titulo).like(...)` utilizando **parámetros ligados** (bind parameters de SQLAlchemy). Jamás concatenación o armado con strings directos (prevención estricta de SQL Injection).

---

## Dominio: Clientes y Perfiles (RN-CLI)

### RN-02 — Unicidad de Email de Cliente
- **Enunciado**: El correo electrónico de un cliente es único en el sistema.
- **Garante esperado**: Restricción `UNIQUE` en la columna `cliente.email` de la base de datos.
- **Respuesta de error**: HTTP 409 con mensaje legible propio.

### RN-09 — Cardinalidad 1 a 1 de Perfil de Cliente
- **Enunciado**: Un cliente tiene como máximo un único perfil asociado.
- **Garante esperado**: Restricción `UNIQUE` en la clave foránea `perfil_cliente.cliente_id`.
- **Respuesta de error**: Si se intenta crear un segundo perfil para el mismo cliente mediante `POST /clientes/{id}/perfil`, la base rechaza la inserción por unicidad y se responde HTTP 409.

---

## Dominio: Ventas y Renglones (RN-VEN)

### RN-04 — Alta Atómica de Ventas y Composición de Renglones
- **Enunciado**: Una venta se crea conjuntamente con todos sus renglones. Los datos de cada renglón viajan anidados dentro del cuerpo del alta de la venta (`POST /ventas/`), y no existe un endpoint ni mecanismo de alta de renglones por separado.
- **Garante esperado**: DTO anidado (`VentaCreate` con lista `renglones`). Los renglones se instancian y asocian a `venta.renglones` dentro de la misma transacción.

### RN-05 — Validación de Renglones en Venta
- **Enunciado**: Una venta debe tener al menos un renglón, y un mismo libro no puede aparecer repetido en dos renglones distintos de la misma venta.
- **Garante esperado**: Validación a nivel de DTO (`@model_validator` o validadores de Pydantic).
- **Respuesta de error**: HTTP 422 (Unprocessable Entity) si la lista está vacía o si existen `libro_id` duplicados en el cuerpo.

### RN-06 — Congelamiento Histórico de Precio Unitario
- **Enunciado**: El precio unitario de cada renglón se copia del precio actual del libro en la base de datos al momento de registrar la venta y queda fijado de forma inmutable, sin cambiar aunque el precio del libro aumente o disminuya en el futuro.
- **Garante esperado**: El precio no viaja en el DTO de entrada. El servicio consulta el libro en la base de datos, extrae su `precio` y lo asigna a `renglon.precio_unitario`.

### RN-07 — Cálculo del Total de Venta en Servidor
- **Enunciado**: El total de la venta lo calcula el servidor sumando el producto de `cantidad * precio_unitario` de cada uno de sus renglones.
- **Garante esperado**: El total nunca viaja en el DTO del cliente; es calculado en el backend con precisión exacta utilizando tipos `Decimal`.

### RN-08 — Inmutabilidad de Ventas
- **Enunciado**: Las ventas no se modifican ni se eliminan una vez asentadas: representan el registro inmutable de un hecho histórico.
- **Garante esperado**: No existe endpoint `PATCH` ni `DELETE` para el recurso `/ventas/`.

---

## Dominio: Transversal y API (RN-GEN)

### RN-10 — Paginación Estándar de Listados
- **Enunciado**: Todo listado de colección se pagina obligatoriamente con `limit` (rango permitido de 1 a 100, valor por defecto: 20) y `offset` (número entero mayor o igual a 0, valor por defecto: 0).
- **Garante esperado**: Parámetros tipados con `Query(default=20, ge=1, le=100)` y `Query(default=0, ge=0)`.
- **Respuesta de error**: HTTP 422 si los parámetros exceden o no cumplen los rangos.

### RN-12 — Ocultamiento de Detalles Internos en Respuestas de Error
- **Enunciado**: Ninguna respuesta de error hacia el cliente puede contener texto interno de la base de datos (nombres de tablas, nombres de constraints, sintaxis SQL o trazas de excepción de PostgreSQL/asyncpg).
- **Garante esperado**: Interceptor o traducción explícita de `IntegrityError` de SQLAlchemy/asyncpg en la capa de servicios o manejador global de excepciones, devolviendo un mensaje claro y propio en formato JSON con código HTTP 409.
