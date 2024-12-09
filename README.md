# Sistema de Gestión de Trabajadores y Contratos

Este es un sistema de gestión de trabajadores y contratos desarrollado en **Flask** y **PostgreSQL**. Permite realizar operaciones CRUD (Crear, Leer, Actualizar y Eliminar) sobre los registros de trabajadores, contratos y otros datos asociados. Este sistema está diseñado para manejar información de trabajadores, contratos, AFPs, bancos, regiones y otros detalles relevantes.

## Características

- **CRUD de Trabajadores**: Permite agregar, visualizar, actualizar y eliminar registros de trabajadores.
- **Gestión de Contratos**: Permite asociar contratos a trabajadores y almacenar información de inicio y término.
- **Catálogos de Datos**: Maneja datos auxiliares como AFPs, bancos, comunas, regiones, tipos de cuenta, previsiones de salud, entre otros.
- **Interfaz de Usuario Mejorada**: Usa Bootstrap para mejorar la usabilidad y la apariencia del sistema.
- **Confirmación de Eliminación**: Previene eliminaciones accidentales mediante confirmación.

## Tecnologías Usadas

- **Python (Flask)**: Framework para construir la aplicación web.
- **PostgreSQL**: Base de datos relacional para almacenar la información.
- **Docker**: Contenedores para facilitar la instalación y ejecución del proyecto.
- **HTML, CSS, Bootstrap**: Para la interfaz de usuario.
- **SQLAlchemy**: ORM para manejar la base de datos en Flask.

## Instalación y Configuración

### Prerrequisitos

- **Docker** y **Docker Compose** instalados en tu sistema.
- Opcionalmente, puedes ejecutar la aplicación sin Docker, en cuyo caso necesitas instalar **Python 3.x**, **PostgreSQL**, y los paquetes requeridos (ver `requirements.txt`).

### Paso 1: Clonar el Repositorio

Clona el repositorio a tu máquina local:

```bash
git clone https://github.com/tu-usuario/tu-repositorio.git
cd tu-repositorio

### Paso 2: Configurar las Variables de Entorno

Crea un archivo .env en el directorio principal del proyecto y define las siguientes variables de entorno para la configuración de la base de datos y la clave secreta de Flask:

SECRET_KEY=tu_clave_secreta
DATABASE_URL=postgresql://usuario:contraseña@db:5432/mydb

### Paso 3: Construir y Ejecutar con Docker

Construye y levanta los contenedores Docker con el siguiente comando:

docker-compose up --build

Esto levantará tanto la aplicación Flask como la base de datos PostgreSQL.

### Paso 4: Inicializar la Base de Datos

Una vez que los contenedores estén en ejecución, inicializa las tablas en la base de datos ejecutando el siguiente comando:

docker exec -it flask_app flask init-db

### Paso 5: Acceder a la Aplicación

La aplicación estará disponible en http://localhost:5000. Puedes acceder a la interfaz web y comenzar a utilizar el sistema.

Uso
Crear un Nuevo Trabajador
1. En la página de inicio, haz clic en el botón "Crear Trabajador" para agregar un nuevo trabajador.
2. Completa el formulario con los datos del trabajador y presiona "Guardar".

Listar, Actualizar y Eliminar Trabajadores
- En la página principal, verás una lista de todos los trabajadores con la opción de "Actualizar" o "Borrar" cada uno.
- Actualizar te llevará a un formulario donde podrás modificar los datos del trabajador.
- Borrar mostrará un mensaje de confirmación antes de eliminar al trabajador.

Gestionar Contratos
1. Para añadir un contrato, selecciona "Agregar Contrato" y asocia un trabajador.
2. Completa los datos de fecha de inicio y término.

Estructura del Proyecto

.
├── app.py                 # Configuración principal de Flask y definición de rutas
├── models.py              # Modelos de la base de datos
├── forms.py               # Formularios de Flask-WTF
├── templates/             # Plantillas HTML para las vistas
├── static/                # Archivos estáticos (CSS, JavaScript)
├── requirements.txt       # Paquetes de Python necesarios
├── docker-compose.yml     # Configuración de Docker
└── README.md              # Este archivo

Rutas Principales

| Ruta                          | Método | Descripción                           |
|-------------------------------|--------|---------------------------------------|
| `/`                           | GET    | Página de inicio y lista de trabajadores |
| `/add_trabajador`             | GET/POST | Formulario para agregar un trabajador |
| `/update_trabajador/<id>`     | GET/POST | Actualizar un trabajador existente |
| `/delete_trabajador/<id>`     | POST   | Eliminar un trabajador existente      |
| `/add_contrato`               | GET/POST | Formulario para agregar un contrato  |
| `/update_contrato/<id>`       | GET/POST | Actualizar un contrato existente     |
| `/delete_contrato/<id>`       | POST   | Eliminar un contrato existente       |
| `/add_afp`                    | GET/POST | Formulario para agregar una AFP      |
| `/add_banco`                  | GET/POST | Formulario para agregar un banco     |
| `/add_comuna`                 | GET/POST | Formulario para agregar una comuna   |
| `/add_region`                 | GET/POST | Formulario para agregar una región   |
| `/add_cuenta`                 | GET/POST | Formulario para agregar un tipo de cuenta |
| `/add_pais`                   | GET/POST | Formulario para agregar un país      |
| `/add_prevision`              | GET/POST | Formulario para agregar una previsión de salud |
| `/add_estado_civil`           | GET/POST | Formulario para agregar un estado civil |
| `/add_genero`                 | GET/POST | Formulario para agregar un género    |


Contribuciones
¡Las contribuciones son bienvenidas! Si deseas colaborar en el proyecto, crea un pull request o abre un issue en GitHub.

Licencia
Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.

Créditos
Este sistema fue desarrollado como una herramienta de gestión para simplificar la administración de trabajadores y contratos. Agradecemos cualquier comentario o sugerencia para mejorar el sistema.

¡Gracias por utilizar el Sistema de Gestión de Trabajadores y Contratos!


Este archivo `README.md` contiene toda la información esencial para instalar, configurar, y utilizar el sistema, junto con detalles técnicos y funcionales que facilitan la comprensión del proyecto. Puedes modificar los enlaces y nombres específicos para adaptarlo a tu propio repositorio o hacer ajustes según sea necesario.
