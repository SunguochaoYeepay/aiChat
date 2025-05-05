@echo off
chcp 65001 > nul
title AI Helper - API Service (with Model Loading)

echo ========================================================
echo         AI Helper - API Service (with Model Loading)
echo ========================================================
echo.
echo Starting API service and loading AI model...please wait
echo Note: Model loading may take a few minutes, please be patient
echo.

REM 切换到正确的目录
cd /d %~dp0
if %errorlevel% neq 0 (
  echo [ERROR] Cannot change to project root directory
  goto error
)

REM 激活虚拟环境
echo Activating virtual environment...
call chat_env\Scripts\activate.bat
if %errorlevel% neq 0 (
  echo [ERROR] Cannot activate virtual environment
  goto error
)

echo.
echo Starting API service (with model loading)...
echo API URL: http://localhost:8000/api/
echo.
echo [NOTE] First startup may take a few minutes for model loading
echo [TIP] When you see "Model test completed" message, the model is loaded
echo ========================================================
echo.

REM 切换到Django项目目录并启动API服务
cd admin_system
python -c "import sys; sys.path.append('.'); import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_system.minimal_settings'); import django; django.setup(); from core.model_service import init_model; init_model()"
echo Model loading has started, now starting API service...

REM 启动API服务
start cmd /k "title API Service && python manage.py runserver 8000 --settings=admin_system.minimal_settings"

REM 等待几秒让服务启动
echo Waiting for server to start...
timeout /t 3 /nobreak > nul

REM 返回到项目根目录
cd ..

REM 检查是否存在增强版model_loader.py脚本
if exist model_loader.py (
  echo Running enhanced model loader script...
  python model_loader.py 8000 180
) else (
  REM 使用简单的api_trigger.py作为备选
  echo Running legacy model trigger script...
  python api_trigger.py 8000 60
)

echo.
echo API service is running at http://localhost:8000/api/
echo API is now fully ready to use!
echo.
echo Press any key to exit this window (API service will continue running)...
pause
goto end

:error
echo.
echo ========================================================
echo [ERROR] Failed to start API service, check error messages above
echo ========================================================
echo.
pause
exit /b 1

:end
echo.
echo Setup complete
pause 