@echo off
echo ========================================
echo     SERVIDOR DE DESARROLLO DJANGO
echo ========================================
echo.
echo NOTA: Asegurate de tener un entorno virtual activado
echo      con Django instalado antes de ejecutar este script.
echo.
echo Iniciando servidor Django...
echo Si hay errores de base de datos, ejecuta migrate.bat primero
echo.
echo 🌐 El servidor estara disponible en: http://localhost:8000/
echo 📱 Panel admin en: http://localhost:8000/admin/
echo 🗳️  Encuestas en: http://localhost:8000/polls/
echo.
echo Presiona Ctrl+C para detener el servidor
echo.
python manage.py runserver 8000
