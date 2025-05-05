@echo off
chcp 65001 > nul
title Qwen-VL-Chat Startup Script

echo ==========================================
echo        Qwen-VL-Chat Startup Script
echo ==========================================
echo.
echo Starting the service launcher...
echo.

cd /d %~dp0
call scripts\launchers\launcher.bat

echo.
echo Thank you for using Qwen-VL-Chat service! 