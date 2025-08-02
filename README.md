# Encuestas Django

Este proyecto es una aplicación web de encuestas desarrollada con Django. Permite crear preguntas, votar y ver resultados, con un panel de administración profesional.

## Características
- Listado de preguntas y votación en la web
- Resultados en tiempo real
- Panel de administración seguro
- Base de datos SQLite

## Instalación
1. Clona el repositorio:
   ```bash
   git clone <URL-del-repositorio>
   cd encuestas_django
   ```
2. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # En Windows
   ```
3. Instala dependencias:
   ```bash
   pip install django
   ```
4. Aplica migraciones:
   ```bash
   python manage.py migrate
   ```
5. Crea un superusuario:
   ```bash
   python manage.py createsuperuser
   ```
6. Inicia el servidor:
   ```bash
   python manage.py runserver
   ```

## Uso
- Accede a la app: http://127.0.0.1:8000/polls/
- Panel admin: http://127.0.0.1:8000/admin/

## Estructura principal
- `manage.py`: Comandos administrativos
- `encuestas/`: Configuración y núcleo del proyecto
- `polls/`: Aplicación de encuestas
- `static/` y `templates/`: Archivos estáticos y plantillas
- `encuestas_db.sqlite3`: Base de datos

## Licencia
Este proyecto está bajo la licencia MIT. Consulta el archivo LICENSE para más detalles.

## Mejoras futuras
- Autenticación de usuarios para votar
- Exportar resultados
- Mejoras en la interfaz
