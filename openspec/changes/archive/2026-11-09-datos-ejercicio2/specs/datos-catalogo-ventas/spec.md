# Spec Delta

## Purpose

Define la capability de datos `datos-catalogo-ventas`: el esquema relacional obligatorio de la librería (9 tablas), sus restricciones de integridad y sus relaciones navegables, garantizado por pruebas de metadata reproducibles sin PostgreSQL.

## ADDED Requirements

### Requirement: Obligatory domain tables with exact names
The system SHALL define exactly the nine mandatory tables: `editorial`, `genero`, `autor`, `libro`, `libro_autor`, `cliente`, `perfil_cliente`, `venta`, `renglon_venta`.

#### Scenario: All tables registered in metadata
- **WHEN** every model module is imported and the metadata is inspected
- **THEN** the metadata contains exactly those nine table names, plus no unnamed extra persistent tables

### Requirement: Primary keys simple and composite
`libro_autor` SHALL have the composite primary key `(libro_id, autor_id)`; every other mandatory table SHALL have a single-column `id` primary key.

#### Scenario: Composite key on association entity
- **WHEN** `libro_autor.primary_key` is inspected
- **THEN** it covers exactly `libro_id` and `autor_id` (both also foreign keys)

### Requirement: Uniqueness restrictions
The system SHALL guarantee with database-level uniqueness: `editorial.nombre`, `genero.nombre`, `libro.isbn`, `cliente.email`, and `perfil_cliente.cliente_id` (one profile per customer).

#### Scenario: Unique constraints present
- **WHEN** metadata constraints and unique indexes are inspected
- **THEN** each listed column carries a unique constraint or unique index in its table

### Requirement: Check restrictions
The system SHALL enforce: `precio > 0`, `stock >= 0`, `orden >= 1`, `rol IN ('autor','coautor','traductor','ilustrador')`, `total >= 0`, `cantidad > 0`, `precio_unitario > 0`.

#### Scenario: Check constraints present
- **WHEN** metadata check constraints are inspected
- **THEN** each listed predicate appears as a named `CHECK` constraint of its table

### Requirement: Indexed foreign keys
Every foreign key (`libro.editorial_id`, `libro.genero_id`, `libro_autor.libro_id`, `libro_autor.autor_id`, `perfil_cliente.cliente_id`, `venta.cliente_id`, `renglon_venta.venta_id`, `renglon_venta.libro_id`) SHALL have an index.

#### Scenario: FK indexed
- **WHEN** table indexes are inspected
- **THEN** an index covers each foreign key column

### Requirement: Bidirectional domain relationships
The seven domain relationships SHALL be navigable in both directions via `back_populates`: Editorial↔Libro, Genero↔Libro (optional), Libro↔Autor (via LibroAutor), Cliente↔PerfilCliente (one-to-one), Cliente↔Venta, Venta↔RenglonVenta (composition), RenglonVenta↔Libro.

#### Scenario: Customer profile is single object
- **WHEN** the Cliente→PerfilCliente relationship is configured
- **THEN** `Cliente.perfil` uses `uselist=False`, so it resolves to one object or `None`, never a list

#### Scenario: Mappers configure cleanly
- **WHEN** `configure_mappers()` runs
- **THEN** no mapping errors are raised

### Requirement: Monetary types
Monetary columns SHALL be Python `Decimal` mapped to SQL `NUMERIC`: `libro.precio` and `renglon_venta.precio_unitario` as `NUMERIC(10,2)`, `venta.total` as `NUMERIC(12,2)`.

#### Scenario: No float money
- **WHEN** the monetary column types are inspected
- **THEN** `python_type` is `Decimal` and precision/scale match the NUMERIC definitions

### Requirement: Composition cascades
`Venta.renglones` and `Libro.autorias` SHALL configure `cascade="all, delete-orphan"` so rows are created and destroyed with their owner.

#### Scenario: Renglones live and die with the venta
- **WHEN** the relationships are inspected
- **THEN** both cascade sets contain `all, delete-orphan`

### Requirement: Clean model imports
Each model module SHALL import without circular dependency errors in a clean Python process.

#### Scenario: Isolated import of every model module
- **WHEN** each `app/modules/*/models.py` is imported in a separate subprocess
- **THEN** no ImportError or circular dependency error occurs
