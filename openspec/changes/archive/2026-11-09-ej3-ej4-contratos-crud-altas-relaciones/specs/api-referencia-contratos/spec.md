# Spec Delta

## Purpose

Define los contratos HTTP observables de los endpoints de referencia del dominio para que clientes y evaluadores interactúen con DTOs claros, códigos de estado coherentes y operaciones seguras.

## ADDED Requirements

### Requirement: DTOs separados de modelos de tabla
El sistema SHALL exponer contratos de entrada/salida separados de los modelos de tabla. Los contratos de alta no incluirán el identificador asignado por la persistencia.

#### Scenario: Alta sin identificador en el cuerpo
- **WHEN** un cliente envía un cuerpo de creación para un recurso de referencia
- **THEN** el contrato de entrada no requiere ni depende de un `id` proporcionado por el cliente para crear el recurso

### Requirement: Actualización parcial con campos enviados
El sistema SHALL aplicar en operaciones de actualización parcial únicamente los campos presentes en la solicitud, preservando los valores no enviados.

#### Scenario: PATCH omite campos
- **WHEN** un cliente envía un `PATCH` con un subconjunto de campos actualizables
- **THEN** solo esos campos cambian y el resto del recurso permanece sin modificación

### Requirement: Códigos de estado semánticos
El sistema MUST responder con códigos coherentes al resultado de la operación: creación exitosa con 201, recurso inexistente con 404, rechazo de escritura por la base con 409 y contrato/cuerpo/parámetros inválidos con 422.

#### Scenario: Creación exitosa
- **WHEN** una solicitud de creación válida se procesa correctamente
- **THEN** la respuesta usa código 201 e incluye la representación del recurso creado

#### Scenario: Recurso inexistente
- **WHEN** se solicita operar sobre un recurso que no existe
- **THEN** la respuesta usa código 404

#### Scenario: Rechazo de escritura por integridad
- **WHEN** la base rechaza una escritura (por ejemplo, unicidad o clave foránea) durante una operación válida a nivel de contrato
- **THEN** la respuesta usa código 409 con un mensaje propio y limpio, sin exponer texto interno de base de datos ni trazas

#### Scenario: Contrato inválido
- **WHEN** el cuerpo o los parámetros no cumplen el contrato esperado
- **THEN** la respuesta usa código 422 sin ejecutar lógica de negocio incompatible con el contrato

### Requirement: Paginación de listados
El sistema SHALL paginar los listados de referencia mediante parámetros `limit` y `offset` conforme a RN-10.

#### Scenario: Listado paginado
- **WHEN** un cliente consulta un listado con `limit` y `offset` válidos
- **THEN** la respuesta devuelve un subconjunto acotado y predecible según esos parámetros

### Requirement: Búsqueda de libros por título con parámetros ligados
El sistema MUST implementar la búsqueda de libros por título de forma case-insensitive usando parámetros ligados (RN-11), evitando inyección por concatenación de entrada.

#### Scenario: Búsqueda normal
- **WHEN** un cliente busca libros por un fragmento de título válido
- **THEN** la respuesta incluye coincidencias case-insensitive paginadas

#### Scenario: Entrada con patrón de inyección
- **WHEN** el parámetro de búsqueda contiene un patrón malicioso (por ejemplo, `' OR '1'='1`)
- **THEN** la consulta se ejecuta con parámetros ligados y la respuesta no filtra datos indebidos (resultado vacío o coincidencias reales, nunca ejecución inyectada)
