@echo off
echo 启动完整测试流程...

REM 切换到项目根目录
cd ..\..\

REM 激活虚拟环境
call chat_env\Scripts\activate.bat

REM 启动服务并等待
start "服务器进程" python scripts/startup/load_model_and_run_django.py

REM 等待服务启动
echo 等待服务启动...
timeout /t 20 /nobreak

REM 测试服务状态API
echo 测试服务状态API...
python scripts/test_scripts/check_model_status.py
if %ERRORLEVEL% NEQ 0 (
    echo 服务状态检查失败，可能模型未加载或服务未启动
    goto end
)

REM 测试聊天API
echo 测试聊天API...
python scripts/test_scripts/test_chat_api.py
set chat_result=%ERRORLEVEL%

REM 测试图像分析API
echo 测试图像分析API...
python scripts/test_scripts/test_analyze_api.py
set analyze_result=%ERRORLEVEL%

REM 测试WebSocket接口
echo 测试WebSocket接口...
python scripts/test_scripts/test_websocket.py
set websocket_result=%ERRORLEVEL%

REM 汇总测试结果
echo.
echo 测试结果汇总:
echo ==========================================
if %chat_result% EQU 0 (
    echo 聊天API测试: 成功
) else (
    echo 聊天API测试: 失败
)

if %analyze_result% EQU 0 (
    echo 图像分析API测试: 成功
) else (
    echo 图像分析API测试: 失败
)

if %websocket_result% EQU 0 (
    echo WebSocket接口测试: 成功
) else (
    echo WebSocket接口测试: 失败
)
echo ==========================================

:end
REM 保持窗口打开
pause 