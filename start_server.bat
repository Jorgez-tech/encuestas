@echo off
cd /d "c:\Users\jzuta\proyectos\encuestas_django"
echo Activando entorno virtual...
call venv\Scripts\activate.bat
echo.
echo Reiniciando servidor Django...
echo Si hay errores de base de datos, ejecuta migrate.bat primero
echo.
echo El servidor estara disponible en: http://localhost:8000/
echo Presiona Ctrl+C para detener el servidor
echo.
python manage.py runserver 8000
