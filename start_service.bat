@echo off
chcp 65001 >nul
echo ========================================
echo    AI图像分析服务 - GPU模式启动脚本
echo ========================================
echo.

echo 正在启动AI图像分析服务...
echo.

:: 使用绝对路径
cd /d D:\AI-DEV\design-helper\admin_system
python manage.py runserver

echo.
echo 服务已停止，按任意键退出...
pause > nul 