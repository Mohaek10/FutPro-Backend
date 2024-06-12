# FutPro - Proyecto de TFG

## Introducción

FutPro es una aplicación web diseñada para gestionar un mercado de jugadores de fútbol. Permite a los usuarios comprar, vender y gestionar sus equipos virtuales. La plataforma ofrece funcionalidades tanto para usuarios regulares como para administradores, facilitando la gestión de jugadores, equipos, transacciones y monedas virtuales (FutCoins).

## Herramientas Utilizadas

### Backend (Django)
- **Django REST Framework**: Para la creación de APIs robustas y seguras.
- **PostgreSQL**: Base de datos relacional.
- **Docker**: Para la contenerización y despliegue de la aplicación.
- **Adminer**: Herramienta de gestión de bases de datos accesible a través de Docker.

## Requisitos Previos
- Docker
- Docker Compose
- Git

## Ejecución de la API

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/Mohaek10/FutPro-Backend.git
2. Iniciar el docker desde la raíz del proyecto:
   ```bash
   docker-compose up --build
3. Realizar las migraciones de la base de datos:
   ```bash
   docker exec futpro-backend-web-1 bash -c "python manage.py makemigrations"
   docker exec futpro-backend-web-1 bash -c "python manage.py migrate"
4. Cargar los datos iniciales:
   ```bash
    docker exec futpro-backend-web-1 bash -c "python manage.py loaddata ./database/users.json"
    docker exec futpro-backend-web-1 bash -c "python manage.py loaddata ./database/data.json"
    docker exec futpro-backend-web-1 bash -c "python manage.py loaddata ./database/ventas.json"
5. Crear un superusuario:
   ```bash
   docker exec -it futpro-backend-web-1 bash -c "python manage.py createsuperuser"
6. Verificar que la API está funcionando correctamente:
   - Acceder a la URL: http://localhost:8000/api/jugadores/
   - Acceder al panel de administración: http://localhost:8000/admin/

## Librerias Utilizadas

- asgiref: Es un paquete que contiene la especificación ASGI y utilidades para desarrollar servidores y aplicaciones ASGI.
- cffi: Es una librería que proporciona una interfaz para llamar a funciones de C desde Python.
- cryptography: Es una librería que proporciona herramientas criptográficas para Python.
- Django: Es un framework web de alto nivel que fomenta el desarrollo rápido y limpio. 
- django-cors-headers: Es una librería que proporciona una gestión de cabeceras CORS para Django.
- django-filter: Es una librería que proporciona una forma sencilla de filtrar los resultados de una consulta basada en los parámetros de solicitud.
- djangorestframework: Es un potente y flexible kit de herramientas para construir APIs web.
- djangorestframework-simplejwt: Es una librería que proporciona una implementación simple de JSON Web Tokens para Django REST framework.
- pillow: Es una librería que proporciona una implementación de la API de imágenes de Python.
- psycopg2-binary: Es un adaptador de base de datos PostgreSQL para Python.
- PyJWT: Es una librería que proporciona una implementación de JSON Web Tokens para Python.

### Arquitectura del Proyecto
- **.envs**: Variables de entorno.
- **.venv**: Entorno virtual de Python.
- **cartas_app**: Gestión de cartas.
- **database**: Datos de pruebas e inicio.
- **futpro**: Configuración principal del proyecto.
- **media**: Archivos multimedia.
- **plantillas_app**: Plantillas HTML.
- **sobres_app**: Gestión de sobres.
- **user_app**: Gestión de usuarios y autenticación.
- **ventas_app**: Gestión de ventas.
- **Archivos adicionales**: .gitignore, comandos.txt, docker-compose.yml, Dockerfile, manage.py, pytest.ini, requirements.txt.

### Autor
Mohamed El Kasmi