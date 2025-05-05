@echo off
echo ==========================================
echo        Qwen-VL-Chat Service Launcher
echo ==========================================
echo.

REM Set working directory
cd /d %~dp0

REM Activate virtual environment
call chat_env\Scripts\activate.bat

echo Checking CUDA availability...
python -c "import torch; print('CUDA Available:', torch.cuda.is_available())"

echo.
echo Please select startup mode:
echo [1] Quick Start (Service only, model loads on first request)
echo [2] Full Start (Preload model and start service - Recommended)
echo [3] Exit
echo.

set /p choice=Enter option (1-3): 

if "%choice%"=="1" goto quick_start
if "%choice%"=="2" goto full_start
if "%choice%"=="3" goto end

echo Invalid option, please restart script
goto end

:quick_start
echo.
echo Starting API service (Quick Mode)...
echo Note: Model will load on first request, which may be slow
echo.
cd admin_system
python manage.py runserver 0.0.0.0:8000 --settings=admin_system.minimal_settings
goto end

:full_start
echo.
echo Loading model and starting service...
echo Please wait, model loading may take several minutes
echo.

REM Start model preload script
start /b cmd /c "python scripts\model_preload.py > model_startup.log 2>&1"

echo Model loading has started in background, logs in model_startup.log
echo Starting API service...
echo.

REM Wait to allow model loading to begin
timeout /t 5 /nobreak > nul

REM Start Django service
cd admin_system
python manage.py runserver 0.0.0.0:8000 --settings=admin_system.minimal_settings

goto end

:end
echo.
if "%choice%"=="1" (
  echo Service stopped.
) else if "%choice%"=="2" (
  echo Service stopped. Model loading process may still be running.
) else (
  echo Program exited.
)
pause 