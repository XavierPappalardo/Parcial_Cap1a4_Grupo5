# Proposal

## Why

El repositorio ya cuenta con la base del Ejercicio 1 (ciclo de vida, sesión async, health) y los modelos/restricciones del Ejercicio 2, pero no expone los contratos HTTP ni las operaciones de negocio requeridas. Este cambio implementa las actividades asignadas al integrante (Ejercicios 3 y 4) para habilitar CRUD/contratos de referencia y altas con relaciones, permitiendo que el resto del equipo complete luego Ej. 5, 6 y despliegue en ramas separadas.

## What Changes

- Implementar **endpoints de referencia** del dominio (editoriales, géneros, autores, libros, clientes + perfil, ventas) con **DTOs separados** de los modelos de tabla (alta sin `id`, lectura/actualización según contrato).
- Aplicar reglas de contrato del Ej. 3: `PATCH` con `exclude_unset`; respuestas **201** (crear), **404** (recurso inexistente), **409** (rechazo de escritura por base/FK/UNIQUE, mensaje limpio RN-12), **422** (cuerpo/parámetros inválidos). Listados paginados (**RN-10**) y búsqueda de libros por título con **parámetros ligados** (**RN-11**).
- Implementar altas con relaciones del Ej. 4:
  - `POST /libros`: recibe `editorial_id`, `genero_id` (opcional) y `autores[]` con `autor_id`, `rol`, `orden`; **sin `SELECT/if` previo** de existencia; FK rechazada → **409**.
  - `POST /ventas`: recibe `cliente_id` y `renglones[]` con `libro_id`, `cantidad`; persiste venta + renglones (composición); cumple **RN-04–RN-07** (precio unitario copiado del libro al registrar, total calculado por el servidor).
- Registrar/importar modelos de dominio en el arranque de la app para que `SQLModel.metadata.create_all` los incluya en runtime (corrección de integración observada).
- Agregar pruebas/casos `.http` y/o automatizados alineados a las actividades 3–4 (alcance acotado a estas actividades; la matriz C/D completa la cierra el equipo según KB).

**Supuestos registrados (alcance):** “Endpoints de referencia” se interpreta como la superficie API de referencia del parcial definida en la KB para los recursos de dominio, con los comportamientos exigidos por Ej. 3 y 4. Fuera de este change: verificación dedicada Ej. 5 (N+1/carga anticipada en todas las lecturas como entregable formal), Ej. 6 (BackgroundTasks/comprobante), Dockerfile/DEPLOY/evidencia D, seed completo, y merge final (responsabilidad del equipo).

## Capabilities

### New Capabilities
- `api-referencia-contratos`: contratos HTTP de los recursos de referencia (DTOs separados, códigos 201/404/409/422, PATCH parcial, paginación RN-10, búsqueda segura RN-11, mapeo de rechazos de integridad a 409 limpio).
- `altas-relaciones-dominio`: creación transaccional de libro con autorías (ids + datos de relación) sin pre-check de existencia, y creación atómica de venta con renglones cumpliendo RN-04–RN-07.

### Modified Capabilities
<!-- None: no existing main specs under openspec/specs/. -->

## Impact

- **Código afectado (al aplicar):** `app/main.py` (import de modelos), nuevos/actualizados módulos `app/modules/<dominio>/` (`models.py` ya existen; se agregarán `schemas.py`, `service.py`, `router.py` y registro de routers), posible `app/core/` para manejo común de errores/RN-12.
- **APIs:** endpoints de referencia para editoriales, géneros, autores, libros, clientes/perfil y ventas (según KB/consigna de referencia).
- **Dependencias:** sin nuevas dependencias previstas (stack ya definido en `requirements.txt`).
- **Datos:** usa tablas/modelos del Ej. 2; altas componen registros en `libro`/`libro_autor` y `venta`/`renglon_venta`.
- **Riesgos:** desalineación con nombres/contratos exactos de la KB (mitigar leyendo `04/05/06/08/11` antes de implementar); traducción incompleta de `IntegrityError` (RN-12).
