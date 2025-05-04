@echo off
echo 正在启动Qwen-VL-Chat API服务...
echo.

REM 切换到项目根目录
cd ..\..

REM 激活虚拟环境并运行启动脚本
call chat_env\Scripts\activate.bat && python scripts\startup\startup.py

pause 