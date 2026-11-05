# 04 — Modelo de Datos

## Dominios y Relaciones

El modelo de dominio abarca dos grandes áreas de negocio:
1. **Catálogo**: Editoriales, Géneros, Autores, Libros y la entidad asociativa intermedia LibroAutor.
2. **Ventas y Clientes**: Clientes, Perfiles de cliente, Ventas y Renglones de venta.

### Clasificación formal de relaciones:
- **Editorial ↔ Libro**: `Agregación`. El libro incorpora una editorial existente; la editorial comparte muchos libros (`1 a N`). Clave foránea `libro.editorial_id` con índice.
- **Género ↔ Libro**: `Agregación opcional`. El libro puede incorporar un género existente de forma optativa (`0..1 a N`). Clave foránea `libro.genero_id` (nulo permitido) con índice.
- **Libro ↔ Autor**: `Muchos a muchos con atributos propios` modelado mediante la entidad intermedia `LibroAutor` (objeto de asociación, no `link_model`). Atributos propios: `rol` y `orden`. Navegación: `libro.autorias[i].autor`.
- **Cliente ↔ PerfilCliente**: `Uno a uno`. Un cliente tiene como máximo un perfil (`1 a 0..1`). Clave foránea `perfil_cliente.cliente_id` con restricción `UNIQUE` e índice. `cliente.perfil` devuelve un objeto (o null), no una lista.
- **Cliente ↔ Venta**: `Asociación`. La venta conoce al cliente que compró, pero ninguno es parte del otro (`1 a N`). Clave foránea `venta.cliente_id` con índice.
- **Venta ↔ RenglonVenta**: `Composición`. El renglón no tiene sentido sin su venta y nace con ella (`1 a N`). Clave foránea `renglon_venta.venta_id` con índice.
- **RenglonVenta ↔ Libro**: `Asociación`. El renglón referencia a un libro existente (`N a 1`). Clave foránea `renglon_venta.libro_id` con índice.

---

## Diagrama Entidad-Relación (ERD)

```
┌──────────────┐             ┌────────────────┐             ┌──────────────┐
│  Editorial   │ 1         * │     Libro      │ *         * │    Autor     │
├──────────────┤◄────────────┤────────────────├─────────────┤──────────────┤
│ id (PK)      │             │ id (PK)        │             │ id (PK)      │
│ nombre (UQ)  │             │ isbn (UQ)      │             │ nombre       │
│ pais         │             │ titulo         │             │ nacionalidad │
└──────────────┘             │ precio         │             └──────────────┘
                             │ stock          │                     ▲
┌──────────────┐             │ editorial_id(FK)                     │ 1
│    Genero    │ 1       0..*│ genero_id (FK) │                     │
├──────────────┤◄────────────┤                │                     │
│ id (PK)      │             └───────┬────────┘                     │
│ nombre (UQ)  │                     │ 1                            │ *
└──────────────┘                     │                     ┌────────┴───────┐
                                     │                     │   LibroAutor   │
                                     │ *                   ├────────────────┤
                                     ▼                     │ libro_id (PK,FK)
                             ┌────────────────┐            │ autor_id (PK,FK)
                             │  RenglonVenta  │            │ rol (CHECK)    │
                             ├────────────────┤            │ orden (CHECK)  │
                             │ id (PK)        │            └────────────────┘
                             │ venta_id (FK)  │
                             │ libro_id (FK)  │
                             │ cantidad       │
                             │ precio_unitario│
                             └───────▲────────┘
                                     │ *
                                     │ (composición)
                                     │ 1
┌──────────────┐ 1       0..1┌───────┴────────┐
│ PerfilCliente│◄────────────┤     Venta      │
├──────────────┤             ├────────────────┤
│ id (PK)      │             │ id (PK)        │
│ cliente_id(UQ)             │ cliente_id (FK)│
│ telefono     │             │ fecha (tz)     │
│ direccion    │             │ total          │
└───────┬──────┘             └────────────────┘
        │ *                          │ *
        │ 1                          │ 1
┌───────┴──────┐                     │
│   Cliente    │◄────────────────────┘
├──────────────┤
│ id (PK)      │
│ nombre       │
│ email (UQ)   │
└──────────────┘
```

---

## Especificación detallada de tablas y restricciones

> **Regla estricta de cátedra**: Los nombres de tablas y columnas son obligatorios. Se pueden agregar columnas si hiciera falta, pero nunca quitar ni renombrar las existentes.

### 1. `editorial`
- `id`: `int` (Primary Key, autoincremental)
- `nombre`: `str` (Constraint: `UNIQUE`)
- `pais`: `str`
- **Relaciones**: `libros: list["Libro"] = Relationship(back_populates="editorial")`

### 2. `genero`
- `id`: `int` (Primary Key, autoincremental)
- `nombre`: `str` (Constraint: `UNIQUE`)
- **Relaciones**: `libros: list["Libro"] = Relationship(back_populates="genero")`

### 3. `autor`
- `id`: `int` (Primary Key, autoincremental)
- `nombre`: `str`
- `nacionalidad`: `str`
- **Relaciones**: `autorias: list["LibroAutor"] = Relationship(back_populates="autor")`

### 4. `libro`
- `id`: `int` (Primary Key, autoincremental)
- `isbn`: `str` (Constraint: `UNIQUE`)
- `titulo`: `str`
- `precio`: `Decimal` / `NUMERIC(10,2)` (Constraint: `CHECK (precio > 0)`)
- `stock`: `int` (Constraint: `CHECK (stock >= 0)`)
- `editorial_id`: `int` (Foreign Key a `editorial.id`, `index=True`)
- `genero_id`: `Optional[int]` (Foreign Key a `genero.id`, nullable, `index=True`)
- **Relaciones**:
  - `editorial: Editorial = Relationship(back_populates="libros")`
  - `genero: Optional[Genero] = Relationship(back_populates="libros")`
  - `autorias: list["LibroAutor"] = Relationship(back_populates="libro", sa_relationship_kwargs={"cascade": "all, delete-orphan"})`
  - `renglones: list["RenglonVenta"] = Relationship(back_populates="libro")`

### 5. `libro_autor` (Entidad intermedia)
- `libro_id`: `int` (PK, Foreign Key a `libro.id`, `index=True`)
- `autor_id`: `int` (PK, Foreign Key a `autor.id`, `index=True`)
- `rol`: `str` (Constraint: `CHECK (rol IN ('autor', 'coautor', 'traductor', 'ilustrador'))`)
- `orden`: `int` (Constraint: `CHECK (orden >= 1)`)
- **Relaciones**:
  - `libro: Libro = Relationship(back_populates="autorias")`
  - `autor: Autor = Relationship(back_populates="autorias")`

### 6. `cliente`
- `id`: `int` (Primary Key, autoincremental)
- `nombre`: `str`
- `email`: `str` (Constraint: `UNIQUE`)
- **Relaciones**:
  - `perfil: Optional["PerfilCliente"] = Relationship(back_populates="cliente")` (Objeto único, no lista)
  - `ventas: list["Venta"] = Relationship(back_populates="cliente")`

### 7. `perfil_cliente`
- `id`: `int` (Primary Key, autoincremental)
- `cliente_id`: `int` (Foreign Key a `cliente.id`, `UNIQUE`, `index=True`)
- `telefono`: `str`
- `direccion`: `str`
- **Relaciones**:
  - `cliente: Cliente = Relationship(back_populates="perfil")`

### 8. `venta`
- `id`: `int` (Primary Key, autoincremental)
- `cliente_id`: `int` (Foreign Key a `cliente.id`, `index=True`)
- `fecha`: `datetime` con timezone (`sa_column=Column(DateTime(timezone=True))`)
- `total`: `Decimal` / `NUMERIC(12,2)` (Constraint: `CHECK (total >= 0)`)
- **Relaciones**:
  - `cliente: Cliente = Relationship(back_populates="ventas")`
  - `renglones: list["RenglonVenta"] = Relationship(back_populates="venta", sa_relationship_kwargs={"cascade": "all, delete-orphan"})`

### 9. `renglon_venta`
- `id`: `int` (Primary Key, autoincremental)
- `venta_id`: `int` (Foreign Key a `venta.id`, `index=True`)
- `libro_id`: `int` (Foreign Key a `libro.id`, `index=True`)
- `cantidad`: `int` (Constraint: `CHECK (cantidad > 0)`)
- `precio_unitario`: `Decimal` / `NUMERIC(10,2)` (Constraint: `CHECK (precio_unitario > 0)`)
- **Relaciones**:
  - `venta: Venta = Relationship(back_populates="renglones")`
  - `libro: Libro = Relationship(back_populates="renglones")`

---

## Seed Data inicial

Para las pruebas del parcial (casos C-06, C-07 y verificación en VPS D-03), el sistema incluye un comando o script de inicialización (`seed_data`) con:
- Al menos 2 editoriales (ej. *Sudamericana*, *Alfaguara*).
- Al menos 2 géneros (ej. *Novela*, *Ensayo*).
- Al menos 4 autores (ej. *Julio Cortázar*, *Adolfo Bioy Casares*, *Silvina Ocampo*, *Ricardo Piglia*).
- Libros con relaciones:
  - Libro 1: "Rayuela" (Editorial Sudamericana, Género Novela, Autor Cortázar como autor único orden 1, precio 25000.00, stock 10).
  - Libro 4: "Respiración artificial" (Editorial Sudamericana, Autor Piglia, precio 27000.00, stock 8).
  - Libro con coautoría: "Los que aman, odian" (Bioy Casares orden 1 coautor, Silvina Ocampo orden 2 coautor, precio 21000.00, stock 4).
- Al menos 2 clientes:
  - Cliente 1 con perfil creado.
  - Cliente 2: "Tomás Ríos" (`tomas@example.com`) sin perfil inicial.
