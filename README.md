Proyecto Libreria API - Grupo 5

#Integrantes:
Xavier Pappalardo
Lautaro Gómez
Nicolas Ibañez
Maximiliano Reinoso
Martin Sisterna
Benjamin Arrollo

--

## Pasos para levantar el proyecto desde cero en entorno local

###1-Crear y activar el entorno virtual
Abre una terminal en la raíz del proyecto y ejecuta los siguientes comandos:

```bash
-Crear el entorno virtual
python -m venv .venv
-Activar en Windows
.venv\Scripts\activate
-Activar en macOS/Linux
source .venv/bin/activate
###2-Instalar dependencias
pip install -r requirements.txt
###3-Configurar el entorno
1-Crear archivo llamada .env en la raiz del proyecto basado en el env.example
2-Configurar la cadena de conexion a la base de datoslocal en PostgreSQL en la variable DATABASE_URL
Este deberia ser el formato:
DATABASE_URL=postgresql+asyncpg://<usuario>:<password>@localhost:5432/<nombre_base>
SQL_ECHO=true
PORT=8000
###4-Arranque del servidor
Iniciar el servidor local de FastAPI. Durante el inicio la aplicacion se conectara a PostgreSQL y creara todas las tablas de la base de datos automaticamente:
uvicorn app.main:app --reload
###5-Carga de datos iniciales
Sin cerrar la terminal anterior, abre otra terminal nueva en la raíz del proyecto, asegúrate de activar el entorno virtual nuevamente, y ejecuta el script para poblar la base de datos con los registros iniciales (editoriales, géneros, autores, libros y clientes):
python -m app.seed