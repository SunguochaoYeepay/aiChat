@echo off
echo 正在启动API服务修复脚本...

REM 切换到项目根目录
cd ..\..\

REM 激活虚拟环境
call chat_env\Scripts\activate.bat

REM 运行修复脚本
python scripts\fixes\fix_api_service.py

REM 如果脚本失败，暂停以查看错误信息
if %ERRORLEVEL% NEQ 0 (
    echo 脚本执行出错，请查看上方错误信息
    pause
) 