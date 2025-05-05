@echo off
chcp 65001 > nul
title Qwen-VL-Chat 启动器

:menu
cls
echo ==========================================
echo        Qwen-VL-Chat 服务启动器
echo ==========================================
echo.
echo 请选择要使用的启动脚本:
echo.
echo [1] start_all_services.bat  (推荐，中文界面，一键启动)
echo [2] start_simple.bat        (推荐，英文界面，一键启动)
echo [3] fix_and_start.bat       (修复模式，解决模型加载问题)
echo [4] start_and_load.bat      (后台启动服务)
echo [5] start_api_service.bat   (多选项API启动)
echo [6] start_service.bat       (简单启动)
echo.
echo [0] 退出
echo.

set /p choice=请输入选项 (0-6): 

if "%choice%"=="1" goto start_all
if "%choice%"=="2" goto start_simple
if "%choice%"=="3" goto fix_start
if "%choice%"=="4" goto start_load
if "%choice%"=="5" goto api_service
if "%choice%"=="6" goto simple_service
if "%choice%"=="0" goto end

echo 无效选项，请重新选择
timeout /t 2 > nul
goto menu

:start_all
echo.
echo 正在启动 start_all_services.bat...
call start_all_services.bat
goto end

:start_simple
echo.
echo 正在启动 start_simple.bat...
call start_simple.bat
goto end

:fix_start
echo.
echo 正在启动 fix_and_start.bat...
call fix_and_start.bat
goto end

:start_load
echo.
echo 正在启动 start_and_load.bat...
call start_and_load.bat
goto end

:api_service
echo.
echo 正在启动 start_api_service.bat...
call start_api_service.bat
goto end

:simple_service
echo.
echo 正在启动 start_service.bat...
call start_service.bat
goto end

:end
echo.
echo 感谢使用启动器
if "%choice%"=="0" (
  exit
) else (
  echo 服务已关闭或启动脚本已结束
  echo 按任意键返回启动器菜单...
  pause > nul
  goto menu
) 