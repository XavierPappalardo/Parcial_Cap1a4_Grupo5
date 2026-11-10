# Spec Delta

## Purpose

Garantizar que las altas de libros y ventas creen sus relaciones de forma consistente con el modelo de dominio, delegando la integridad referencial en la base y preservando reglas de negocio de venta.

## ADDED Requirements

### Requirement: Alta de libro con referencias e autorías
El sistema SHALL permitir crear un libro recibiendo identificadores de entidades existentes (`editorial_id`, `genero_id` opcional) y una lista de autorías donde cada elemento aporta `autor_id` y datos de la relación (`rol`, `orden`).

#### Scenario: Alta de libro válida con relaciones
- **WHEN** se envía un alta de libro con referencias válidas y autorías bien formadas
- **THEN** el sistema crea el libro con sus relaciones y responde 201 con la representación del recurso creado

#### Scenario: Referencia inexistente sin verificación previa
- **WHEN** el alta de libro referencia un identificador inexistente
- **THEN** el sistema no realiza una consulta previa condicional para comprobar existencia; persiste la operación y, si la base rechaza la clave foránea, responde 409 con mensaje limpio

### Requirement: Alta de venta con renglones anidados
El sistema SHALL crear una venta recibiendo `cliente_id` (asociación) y `renglones` con `libro_id` y `cantidad` (composición), registrando la venta junto con sus renglones.

#### Scenario: Venta creada con sus partes
- **WHEN** se envía una venta válida con al menos los datos requeridos de cliente y renglones
- **THEN** la venta y sus renglones quedan persistidos de forma consistente y la respuesta usa código 201

#### Scenario: Referencia inexistente en venta
- **WHEN** la venta referencia un cliente o libro inexistente
- **THEN** el sistema responde 409 ante el rechazo de integridad, con mensaje limpio

### Requirement: Reglas de negocio de renglones y total
El sistema MUST cumplir RN-04 a RN-07 al registrar ventas: crear la venta con renglones, copiar el precio unitario desde el libro en el momento del registro y calcular el total en el servidor.

#### Scenario: Precio copiado y total calculado por servidor
- **WHEN** se registra una venta válida con uno o más renglones
- **THEN** cada renglón almacena el precio unitario tomado del libro correspondiente, el total es calculado por el servidor a partir de los renglones, y la respuesta refleja esos valores

#### Scenario: Validaciones de renglones
- **WHEN** la solicitud de venta no cumple las validaciones de renglones exigidas por el contrato/reglas (por ejemplo, renglones ausentes o libros duplicados, según aplique RN-05)
- **THEN** el sistema responde 422 con error de contrato/validación
