@echo off
cd /d "c:\Users\jzuta\proyectos\encuestas_django"
echo Activando entorno virtual...
call venv\Scripts\activate.bat
echo.
echo Creando migraciones...
python manage.py makemigrations
echo.
echo Aplicando migraciones...
python manage.py migrate
echo.
echo Migraciones completadas!
echo Presiona cualquier tecla para continuar...
pause
