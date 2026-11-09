# Tasks

## 1. Registro de modelos en la aplicación

- [x] 1.1 Importar los 6 módulos de modelos en `app/main.py` antes del `create_all` del lifespan.

## 2. Verificación integral de la integración

- [x] 2.1 Suite completa de ambos ejercicios en verde (`pytest -q`).
- [x] 2.2 Creación física de las 9 tablas obligatorias al arrancar (tests del lifespan con TestClient).
- [x] 2.3 Rutas de health registradas y sesión inyectada por petición (tests HTTPexistentes).
