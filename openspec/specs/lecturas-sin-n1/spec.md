# Lecturas Sin N1 Specification

## Purpose

Garantizar que las lecturas de detalle y catálogo carguen sus relaciones de forma anticipada (cero N+1), emitiendo un número fijo de sentencias SQL independiente de la cantidad de entidades relacionadas, y que la búsqueda de libros y los listados paginados cumplan las reglas de negocio de búsqueda segura y paginación.

## Requirements

### Requirement: Lectura de libro por id con carga anticipada

El sistema SHALL retornar el libro solicitado cargando anticipadamente editorial y género con joinedload, y las autorías con sus autores mediante selectinload, sin disparar consultas perezosas adicionales.

#### Scenario: Libro encontrado con relaciones cargadas

- **WHEN** se consulta GET /libros/{id} de un libro existente
- **THEN** la respuesta incluye el libro con editorial, género y lista de autorías (cada una con su autor) y se emite un número fijo de sentencias SQL independiente de la cantidad de autores

#### Scenario: Libro inexistente

- **WHEN** se consulta GET /libros/{id} con un id que no existe
- **THEN** el sistema responde 404

### Requirement: Lectura de venta por id con carga anticipada

El sistema SHALL retornar la venta solicitada cargando anticipadamente al cliente con joinedload y los renglones con sus libros mediante selectinload.

#### Scenario: Venta encontrada con relaciones cargadas

- **WHEN** se consulta GET /ventas/{id} de una venta existente
- **THEN** la respuesta incluye la venta con cliente y lista de renglones (cada uno con su libro) sin consultas perezosas adicionales

#### Scenario: Venta inexistente

- **WHEN** se consulta GET /ventas/{id} con un id que no existe
- **THEN** el sistema responde 404

### Requirement: Listado de libros de una editorial

El sistema SHALL retornar los libros de una editorial dada cargando anticipadamente sus relaciones.

#### Scenario: Editorial con libros

- **WHEN** se consulta GET /editoriales/{id}/libros de una editorial existente
- **THEN** la respuesta incluye los libros de esa editorial con sus relaciones cargadas

#### Scenario: Editorial inexistente

- **WHEN** se consulta GET /editoriales/{id}/libros con un id que no existe
- **THEN** el sistema responde 404

### Requirement: Listado de libros de un género

El sistema SHALL retornar los libros de un género dado cargando anticipadamente sus relaciones.

#### Scenario: Género con libros

- **WHEN** se consulta GET /generos/{id}/libros de un género existente
- **THEN** la respuesta incluye los libros de ese género con sus relaciones cargadas

#### Scenario: Género inexistente

- **WHEN** se consulta GET /generos/{id}/libros con un id que no existe
- **THEN** el sistema responde 404

### Requirement: Listado de libros de un autor con rol y orden

El sistema SHALL retornar los libros de un autor dado incluyendo el rol y el orden de cada autoría.

#### Scenario: Autor con libros y autorías

- **WHEN** se consulta GET /autores/{id}/libros de un autor existente
- **THEN** la respuesta incluye los libros en los que participó el autor, cada uno con el rol y el orden de la autoría correspondiente

#### Scenario: Autor inexistente

- **WHEN** se consulta GET /autores/{id}/libros con un id que no existe
- **THEN** el sistema responde 404

### Requirement: Lectura de cliente con perfil como objeto único

El sistema SHALL retornar el cliente solicitado con su atributo perfil como un objeto único (o null), nunca como una lista.

#### Scenario: Cliente con perfil

- **WHEN** se consulta GET /clientes/{id} de un cliente existente con perfil
- **THEN** la respuesta incluye el cliente con perfil como objeto único

#### Scenario: Cliente sin perfil

- **WHEN** se consulta GET /clientes/{id} de un cliente existente sin perfil
- **THEN** la respuesta incluye el cliente con perfil nulo

#### Scenario: Cliente inexistente

- **WHEN** se consulta GET /clientes/{id} con un id que no existe
- **THEN** el sistema responde 404

### Requirement: Historial de ventas de un cliente con renglones precargados

El sistema SHALL retornar las ventas de un cliente dado con sus renglones y libros precargados.

#### Scenario: Cliente con ventas

- **WHEN** se consulta GET /clientes/{id}/ventas de un cliente existente
- **THEN** la respuesta incluye el historial de ventas con renglones precargados sin consultas N+1

#### Scenario: Cliente sin ventas

- **WHEN** se consulta GET /clientes/{id}/ventas de un cliente existente sin ventas
- **THEN** la respuesta devuelve una lista vacía

#### Scenario: Cliente inexistente

- **WHEN** se consulta GET /clientes/{id}/ventas con un id que no existe
- **THEN** el sistema responde 404

### Requirement: Número fijo de sentencias SQL (sin N+1)

El sistema SHALL emitir un número fijo y mínimo de sentencias SQL para cada lectura detallada, independiente de la cantidad de entidades relacionadas, verificable con SQL_ECHO=true.

#### Scenario: Lectura de libro sin N+1

- **WHEN** se consulta GET /libros/{id} con SQL_ECHO=true
- **THEN** la consola muestra un número fijo de sentencias SQL sin consultas secundarias por cada autor relacionado

#### Scenario: Lectura de venta sin N+1

- **WHEN** se consulta GET /ventas/{id} con SQL_ECHO=true
- **THEN** la consola muestra un número fijo de sentencias SQL sin consultas secundarias por cada renglón
