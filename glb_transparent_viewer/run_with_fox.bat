@echo off
REM Run the viewer with the fox model
cd /d "%~dp0"

if not exist "build\Release\GLBTransparentViewer.exe" (
    echo ERROR: Build not found!
    echo.
    echo Please run build_release.bat first to compile the project.
    pause
    exit /b 1
)

echo Launching GLB Transparent Viewer with fox.glb...
build\Release\GLBTransparentViewer.exe fox.glb

if %errorlevel% neq 0 (
    echo.
    echo Error running viewer.
    pause
)
