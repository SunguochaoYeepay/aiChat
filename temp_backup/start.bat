@echo off
chcp 65001 > nul
title Qwen-VL-Chat 主启动脚本

echo ==========================================
echo        Qwen-VL-Chat 主启动脚本
echo ==========================================
echo.
echo 正在启动服务启动器...
echo.

cd /d %~dp0
call scripts\launchers\start_launcher.bat

echo.
echo 感谢使用Qwen-VL-Chat服务！ 