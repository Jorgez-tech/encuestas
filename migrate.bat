@echo off
echo ========================================
echo    SCRIPT DE MIGRACIONES DJANGO
echo ========================================
echo.
echo NOTA: Asegurate de tener un entorno virtual activado
echo      con Django instalado antes de ejecutar este script.
echo.
echo Creando migraciones...
python manage.py makemigrations
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron crear las migraciones
    pause
    exit /b %errorlevel%
)
echo.
echo Aplicando migraciones...
python manage.py migrate
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron aplicar las migraciones
    pause
    exit /b %errorlevel%
)
echo.
echo ✅ Migraciones completadas exitosamente!
echo.
pause
