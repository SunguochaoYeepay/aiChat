@echo off
echo 启动测试流程...

REM 切换到项目根目录
cd ..\..\

REM 激活虚拟环境
call chat_env\Scripts\activate.bat

REM 启动服务并等待
start "服务器进程" python scripts/startup/load_model_and_run_django.py

REM 等待服务启动
echo 等待服务启动...
timeout /t 20 /nobreak

REM 测试API
echo 测试API...
python scripts/test_scripts/test_chat_api.py

REM 检查测试结果
if %ERRORLEVEL% EQU 0 (
    echo 测试成功！
) else (
    echo 测试失败，错误码: %ERRORLEVEL%
)

REM 保持窗口打开
pause 