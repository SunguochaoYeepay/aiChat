@echo off
echo ================================================================================
echo            Qwen-VL-Chat API 服务启动程序
echo ================================================================================
echo 此程序将预加载Qwen-VL-Chat模型并启动API服务

REM 激活虚拟环境
call chat_env\Scripts\activate.bat

REM 确定启动方式
:menu
echo.
echo 请选择启动方式:
echo [1] 标准启动 (使用原始启动脚本)
echo [2] 修复模式 (优化向量搜索和解决警告)
echo [3] 仅测试API
echo [4] 退出
echo.
set /p choice=请输入选项 (1-4): 

if "%choice%"=="1" goto standard
if "%choice%"=="2" goto fix
if "%choice%"=="3" goto test
if "%choice%"=="4" goto end

echo 无效选项，请重新选择
goto menu

:standard
echo.
echo 正在使用标准模式启动...
call scripts\startup\startup.py
goto end

:fix
echo.
echo 正在使用修复模式启动...
call scripts\fixes\fix_api_service.py
goto end

:test
echo.
echo 正在测试API...
call scripts\test_scripts\test_chat_api.py
goto end

:end
echo.
echo 程序已退出
pause 