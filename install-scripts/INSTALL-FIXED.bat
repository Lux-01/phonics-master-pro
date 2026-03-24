@echo off
:: OpenClaw Installer v1.1 - FIXED
:: Fixes: Path conversion, interactive WSL handling, pre-flight checks

echo ========================================
echo OpenClaw Installer v1.1 (Fixed)
echo ========================================
echo.

:: Check admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Administrator privileges required!
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

:: Run fixed PowerShell script
PowerShell -ExecutionPolicy Bypass -Command "
    . '%~dp0openclaw-installer-FIXED.ps1'
"

pause
