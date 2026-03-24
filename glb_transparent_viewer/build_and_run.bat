@echo off
REM Build and run in one step
cd /d "%~dp0"

call build_release.bat
if %errorlevel% equ 0 (
    echo.
    echo Running viewer with fox model...
    build\Release\GLBTransparentViewer.exe avatar\fox.glb
)
