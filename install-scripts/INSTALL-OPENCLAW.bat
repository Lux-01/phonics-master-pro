@echo off
:: OpenClaw Windows Installer - Double-click this file
:: It will launch PowerShell and run the installer

echo ========================================
echo OpenClaw Windows Installer
echo ========================================
echo.
echo This will install:
echo   1. WSL2 (Windows Subsystem for Linux)
echo   2. Ubuntu 22.04
echo   3. Ollama (AI server)
echo   4. Kimi-K2.5 model (4GB)
echo   5. OpenClaw (AI gateway)
echo.
echo The installation will take 20-30 minutes.
echo.
pause

:: Check for admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ========================================
    echo ERROR: Administrator privileges required!
    echo ========================================
    echo.
    echo Please right-click this file and select:
    echo "Run as administrator"
    echo.
    pause
    exit /b 1
)

:: Run PowerShell script
PowerShell -ExecutionPolicy Bypass -Command "
    $ProgressPreference = 'Continue'
    $VerbosePreference = 'Continue'
    . '%~dp0openclaw-windows-installer.ps1' -Verbose
"

if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo Installation completed with warnings.
    echo See error messages above.
    echo ========================================
) else (
    echo.
    echo ========================================
    echo Installation successful!
    echo ========================================
)

pause
