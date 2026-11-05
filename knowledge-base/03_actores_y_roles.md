# 03 — Actores y Roles

## Actores del sistema

| Actor | Descripción | Cómo interactúa con el sistema |
|---|---|---|
| **Operador de Librería** | Encargado o empleado de la librería responsable de mantener el catálogo y cobrar. | Invoca los endpoints de catálogo (`POST/PATCH /libros`, `POST /autores`, etc.) y crea ventas (`POST /ventas`). |
| **Cliente de la Librería** | Comprador registrado en el sistema que puede poseer datos de contacto adicionales. | No accede directamente con credenciales; es registrado y consultado por el sistema mediante `/clientes` y `/clientes/{id}/perfil`. |
| **Cátedra / Evaluador Automatizado** | Suite de pruebas de la cátedra de Programación III (UTN). | Envía peticiones HTTP automatizadas (.http, curl, wget) contra la API en local y en el VPS para verificar contratos, códigos HTTP, health y ausencia de N+1. |

## Matriz de permisos (Simulada / Operativa)

> **Nota importante de alcance**: La cátedra excluyó explícitamente los mecanismos de autenticación y autorización (Capítulo 5). No hay tokens JWT ni cabeceras `Authorization`. Todas las rutas son accesibles públicamente a nivel de transporte HTTP, pero responden a contratos funcionales específicos según la operación.

| Módulo / Recurso | Operación | Endpoint | Requisitos de Contrato |
|---|---|---|---|
| **Health** | Leer estado en vivo | `GET /health/live` | Sin cuerpo. Devuelve `{"estado": "vivo"}` (200). |
| **Health** | Leer estado DB | `GET /health/ready` | Sin cuerpo. Ejecuta `SELECT 1` y devuelve estado (200). |
| **Editoriales** | Crear | `POST /editoriales/` | DTO `EditorialCreate`. Valida `nombre` único (201 / 409). |
| **Editoriales** | Listar / Detalle | `GET /editoriales/`, `GET /{id}` | Soporta paginación (`limit`, `offset`). |
| **Editoriales** | Actualizar | `PATCH /editoriales/{id}` | DTO `EditorialUpdate` parcial (`exclude_unset`). |
| **Editoriales** | Libros asociados | `GET /editoriales/{id}/libros` | Retorna colección de libros de la editorial (200 / 404). |
| **Géneros** | Crear / Listar | `POST /generos/`, `GET /generos/` | Valida `nombre` único (201 / 409). |
| **Géneros** | Libros asociados | `GET /generos/{id}/libros` | Retorna libros vinculados a dicho género. |
| **Autores** | Crear / Detalle / PATCH | `POST /autores/`, `GET /{id}`, `PATCH /{id}` | CRUD estándar. |
| **Autores** | Libros de autor | `GET /autores/{id}/libros` | Retorna libros donde participó incluyendo su rol y orden. |
| **Libros** | Crear con relaciones | `POST /libros/` | DTO `LibroCreate` con `editorial_id`, `genero_id` y lista de `autores` (rol, orden). Valida ISBN único y rechaza FKs inexistentes (409). |
| **Libros** | Listar con filtros | `GET /libros/` | Filtros por `titulo` (case-insensitive con parámetros ligados) y `genero_id`. Paginación `limit`/`offset`. |
| **Libros** | Detalle completo | `GET /libros/{id}` | Carga anticipada de editorial, género y autorías/autores (200 / 404). |
| **Libros** | Actualizar parcial | `PATCH /libros/{id}` | DTO `LibroUpdate` parcial. |
| **Clientes** | Crear | `POST /clientes/` | DTO `ClienteCreate`. Valida `email` único (201 / 409). |
| **Clientes** | Detalle con perfil | `GET /clientes/{id}` | Devuelve el cliente con su objeto `perfil` embebido (no lista). |
| **Clientes** | Actualizar | `PATCH /clientes/{id}` | Actualización parcial de nombre o email. |
| **Clientes** | Crear perfil | `POST /clientes/{id}/perfil` | Crea perfil único. Si ya tenía uno, responde 409 (RN-09). |
| **Clientes** | Ventas del cliente | `GET /clientes/{id}/ventas` | Historial de compras del cliente. |
| **Ventas** | Crear venta | `POST /ventas/` | DTO `VentaCreate` con `cliente_id` y `renglones` (libro_id y cantidad). Congela precios, calcula total y agenda background task. |
| **Ventas** | Listar / Detalle | `GET /ventas/`, `GET /{id}` | Detalle con cliente y renglones con carga anticipada (200 / 404). |

## Rutas públicas
Al no contar con módulo de autenticación para esta entrega, **todas las rutas expuestas son públicas**, garantizándose la seguridad y consistencia a nivel de validación estricta de esquemas Pydantic y restricciones en la base de datos relacional.
