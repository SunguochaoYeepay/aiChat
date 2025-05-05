@echo off
chcp 65001 > nul
title Qwen-VL-Chat Launcher

:menu
cls
echo ==========================================
echo        Qwen-VL-Chat Service Launcher
echo ==========================================
echo.
echo Please select a startup script:
echo.
echo [1] start_all_services.bat  (Recommended, Chinese UI, All-in-one)
echo [2] start_simple.bat        (Recommended, English UI, All-in-one)
echo [3] fix_and_start.bat       (Fix mode, Solves model loading issues)
echo [4] start_and_load.bat      (Background service startup)
echo [5] start_api_service.bat   (Multiple API startup options)
echo [6] start_service.bat       (Simple startup)
echo.
echo [0] Exit
echo.

set /p choice=Enter option (0-6): 

if "%choice%"=="1" goto start_all
if "%choice%"=="2" goto start_simple
if "%choice%"=="3" goto fix_start
if "%choice%"=="4" goto start_load
if "%choice%"=="5" goto api_service
if "%choice%"=="6" goto simple_service
if "%choice%"=="0" goto end

echo Invalid option, please try again
timeout /t 2 > nul
goto menu

:start_all
echo.
echo Starting start_all_services.bat...
call start_all_services.bat
goto end

:start_simple
echo.
echo Starting start_simple.bat...
call start_simple.bat
goto end

:fix_start
echo.
echo Starting fix_and_start.bat...
call fix_and_start.bat
goto end

:start_load
echo.
echo Starting start_and_load.bat...
call start_and_load.bat
goto end

:api_service
echo.
echo Starting start_api_service.bat...
call start_api_service.bat
goto end

:simple_service
echo.
echo Starting start_service.bat...
call start_service.bat
goto end

:end
echo.
echo Thank you for using the launcher
if "%choice%"=="0" (
  exit
) else (
  echo Service has been closed or startup script has ended
  echo Press any key to return to the launcher menu...
  pause > nul
  goto menu
) 