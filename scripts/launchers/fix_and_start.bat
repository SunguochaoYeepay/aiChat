@echo off
echo ==========================================
echo    Direct Start Service with Model
echo ==========================================
echo.

REM Set working directory
cd /d %~dp0

REM Activate virtual environment
call chat_env\Scripts\activate.bat

echo Starting integrated service...
echo.

REM Navigate to Django project
cd admin_system

REM Use the known working method
python manage.py shell -c "from core.model_service import init_model; init_model()" && python manage.py runserver 0.0.0.0:8000

echo Service stopped.
pause 