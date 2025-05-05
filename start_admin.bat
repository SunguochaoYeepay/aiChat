@echo off
chcp 65001 > nul
title AI Helper - Admin System

echo ========================================================
echo             AI Helper - Admin System
echo ========================================================
echo.
echo Starting admin system...please wait
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
echo Starting Django admin system...
echo Admin URL: http://localhost:8000/admin/
echo.
echo Press Ctrl+C to stop the service
echo ========================================================
echo.

REM 启动Django管理系统
cd admin_system
python manage.py runserver 8000

goto end

:error
echo.
echo ========================================================
echo [ERROR] Failed to start admin system, check error messages above
echo ========================================================
echo.
pause
exit /b 1

:end
echo.
echo Service stopped
pause 