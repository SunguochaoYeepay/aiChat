@echo off
chcp 65001 > nul
title Backup Old Scripts

echo ========================================================
echo          Backing Up Deprecated Script Files
echo ========================================================
echo.
echo This script will move all old startup scripts to a backup folder
echo but keep our new start_admin.bat and start_api.bat in place.
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause > nul

REM 创建备份目录
echo Creating backup directory...
mkdir temp_backup_scripts 2>nul
if %errorlevel% neq 0 (
  echo [NOTE] Backup directory already exists
) else (
  echo [OK] Created backup directory: temp_backup_scripts
)

REM 备份当前的主启动脚本
echo.
echo Backing up current main scripts...
copy start_admin.bat temp_backup_scripts\start_admin.backup.bat >nul
copy start_api.bat temp_backup_scripts\start_api.backup.bat >nul
echo [OK] Current main scripts backed up

REM 移动所有其他启动脚本到备份目录
echo.
echo Moving old startup scripts to backup directory...

REM 注意使用通配符但排除新脚本
for %%F in (start*.bat) do (
  if not "%%F"=="start_admin.bat" if not "%%F"=="start_api.bat" if not "%%F"=="backup_scripts.bat" (
    move %%F temp_backup_scripts\ >nul
    echo - Moved: %%F
  )
)

REM 移动其他辅助启动脚本
move launcher.bat temp_backup_scripts\ 2>nul
if %errorlevel% equ 0 echo - Moved: launcher.bat

move start_launcher.bat temp_backup_scripts\ 2>nul
if %errorlevel% equ 0 echo - Moved: start_launcher.bat

move fix*.bat temp_backup_scripts\ 2>nul
if %errorlevel% equ 0 echo - Moved: fix*.bat

echo.
echo ========================================================
echo              Backup Process Completed
echo ========================================================
echo.
echo The following files remain in the root directory:
echo - start_admin.bat
echo - start_api.bat
echo - backup_scripts.bat
echo.
echo All other startup scripts have been moved to: temp_backup_scripts
echo.
echo Press any key to exit...
pause > nul 