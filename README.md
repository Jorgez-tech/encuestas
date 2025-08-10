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

## Despliegue Estático (Demo)

Este proyecto incluye un despliegue automático a **GitHub Pages** que sirve una versión estática de la página de inicio.

-   **URL de la Demo:** [https://jorgez-tech.github.io/encuestas/](https://jorgez-tech.github.io/encuestas/)

**Limitaciones de la Demo:**
Debido a que GitHub Pages solo sirve contenido estático, esta versión es una **demostración visual sin funcionalidad de backend**. Las características que dependen de Django (como ver el listado de encuestas, votar o acceder al panel de administración) no están activas en esta URL.

Para experimentar la aplicación completa, por favor, sigue las instrucciones de instalación y ejecútala en un entorno local.
