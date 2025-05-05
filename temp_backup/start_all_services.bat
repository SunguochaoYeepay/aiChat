@echo off
chcp 65001 > nul
echo ==========================================
echo    Qwen-VL-Chat 服务一键启动程序
echo ==========================================
echo.

REM 设置工作目录为脚本所在目录
cd /d %~dp0

REM 激活虚拟环境
call chat_env\Scripts\activate.bat

echo 检查CUDA可用性...
python -c "import torch; print('CUDA可用:', torch.cuda.is_available())"

echo.
echo 请选择启动模式:
echo [1] 快速启动 (仅启动服务，等需要时再加载模型)
echo [2] 完整启动 (预加载模型并启动服务 - 推荐)
echo [3] 退出
echo.

set /p choice=请输入选项 (1-3): 

if "%choice%"=="1" goto quick_start
if "%choice%"=="2" goto full_start
if "%choice%"=="3" goto end

echo 无效选项，请重新运行脚本
goto end

:quick_start
echo.
echo 正在快速启动API服务...
echo 注意: 模型将在首次请求时加载，首次响应可能较慢
echo.
cd admin_system
python manage.py runserver 0.0.0.0:8000 --settings=admin_system.minimal_settings
goto end

:full_start
echo.
echo 正在加载模型并启动服务...
echo 请耐心等待，模型加载可能需要几分钟时间
echo.

REM 先启动模型加载脚本
start /b cmd /c "chcp 65001 > nul && python scripts\model_preload.py > model_startup.log 2>&1"

echo 模型加载已在后台开始，日志将记录到 model_startup.log
echo 正在启动API服务...
echo.

REM 等待几秒让模型开始加载
timeout /t 5 /nobreak > nul

REM 启动Django服务
cd admin_system
python manage.py runserver 0.0.0.0:8000 --settings=admin_system.minimal_settings

goto end

:end
echo.
if "%choice%"=="1" (
  echo 服务已关闭。
) else if "%choice%"=="2" (
  echo 服务已关闭。模型加载进程可能仍在后台运行。
) else (
  echo 程序已退出。
)
pause 