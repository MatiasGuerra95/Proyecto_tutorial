# Sistema de Gestión de Trabajadores, Contratos y Empresas

Este es un sistema de gestión de trabajadores, contratos, empresas, sucursales, representantes y servicios desarrollado en **Flask** y **PostgreSQL**. Permite realizar operaciones CRUD (Crear, Leer, Actualizar y Eliminar) sobre los registros relacionados y está diseñado para manejar información clave de manera eficiente.

## Características

- **CRUD de Trabajadores**: Permite agregar, visualizar, actualizar y eliminar registros de trabajadores.
- **Gestión de Contratos**: Permite asociar contratos a trabajadores y almacenar información de inicio y término.
- **CRUD de Representantes**: Maneja representantes asociados a empresas con roles definidos.
- **CRUD de Sucursales**: Gestión de sucursales asociadas a empresas, incluyendo datos de región, comuna y representantes asignados.
- **CRUD de Servicios**: Permite crear, actualizar y gestionar servicios ofrecidos por las empresas, con fechas de inicio y término.
- **CRUD de Empresas**: Gestión de empresas, incluyendo su RUT y razón social.
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
```

### Paso 2: Configurar las Variables de Entorno

Crea un archivo `.env` en el directorio principal del proyecto y define las siguientes variables de entorno para la configuración de la base de datos y la clave secreta de Flask:

```plaintext
SECRET_KEY=tu_clave_secreta
DATABASE_URL=postgresql://usuario:contraseña@db:5432/mydb
```

### Paso 3: Construir y Ejecutar con Docker

Construye y levanta los contenedores Docker con el siguiente comando:

```bash
docker-compose up --build
```

Esto levantará tanto la aplicación Flask como la base de datos PostgreSQL.

### Paso 4: Inicializar la Base de Datos

Una vez que los contenedores estén en ejecución, inicializa las tablas en la base de datos ejecutando el siguiente comando:

```bash
docker exec -it flask_app flask init-db
```

### Paso 5: Acceder a la Aplicación

La aplicación estará disponible en [http://localhost:5000](http://localhost:5000). Puedes acceder a la interfaz web y comenzar a utilizar el sistema.

## Uso

### Crear un Nuevo Trabajador
1. En la página de inicio, haz clic en el botón "Crear Trabajador" para agregar un nuevo trabajador.
2. Completa el formulario con los datos del trabajador y presiona "Guardar".

### Listar, Actualizar y Eliminar Trabajadores
- En la página principal, verás una lista de todos los trabajadores con la opción de "Actualizar" o "Borrar" cada uno.
- Actualizar te llevará a un formulario donde podrás modificar los datos del trabajador.
- Borrar mostrará un mensaje de confirmación antes de eliminar al trabajador.

### Gestionar Contratos
1. Para añadir un contrato, selecciona "Agregar Contrato" y asocia un trabajador.
2. Completa los datos de fecha de inicio y término.

### Gestionar Representantes, Servicios, Sucursales y Empresas
- **Representantes**: Agrega representantes con roles específicos asociados a empresas.
- **Servicios**: Administra los servicios ofrecidos por las empresas.
- **Sucursales**: Crea y gestiona sucursales vinculadas a empresas y regiones.
- **Empresas**: Administra los datos de empresas, como su RUT y razón social.

## Estructura del Proyecto

```
.
├── app.py                 # Configuración principal de Flask y definición de rutas
├── models.py              # Modelos de la base de datos
├── forms.py               # Formularios de Flask-WTF
├── templates/             # Plantillas HTML para las vistas
├── static/                # Archivos estáticos (CSS, JavaScript)
├── requirements.txt       # Paquetes de Python necesarios
├── docker-compose.yml     # Configuración de Docker
└── README.md              # Este archivo
```

## Rutas Principales

| Ruta                          | Método   | Descripción                                   |
|-------------------------------|----------|-----------------------------------------------|
| `/`                           | GET      | Página de inicio y lista de trabajadores      |
| `/empresas`                   | GET/POST | Lista y gestión de empresas                  |
| `/representantes`             | GET/POST | Lista y gestión de representantes            |
| `/servicios`                  | GET/POST | Lista y gestión de servicios                 |
| `/sucursal`                   | GET/POST | Lista y gestión de sucursales                |
| `/add_trabajador`             | GET/POST | Formulario para agregar un trabajador         |
| `/update_trabajador/<id>`     | GET/POST | Actualizar un trabajador existente            |
| `/delete_trabajador/<id>`     | POST     | Eliminar un trabajador existente             |
| `/add_contrato`               | GET/POST | Formulario para agregar un contrato          |
| `/update_contrato/<id>`       | GET/POST | Actualizar un contrato existente             |
| `/delete_contrato/<id>`       | POST     | Eliminar un contrato existente               |

## Contribuciones

¡Las contribuciones son bienvenidas! Si deseas colaborar en el proyecto, crea un pull request o abre un issue en GitHub.

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.

## Créditos

Este sistema fue desarrollado como una herramienta de gestión para simplificar la administración de trabajadores, contratos y empresas. Agradecemos cualquier comentario o sugerencia para mejorar el sistema.

¡Gracias por utilizar el Sistema de Gestión de Trabajadores, Contratos y Empresas!
