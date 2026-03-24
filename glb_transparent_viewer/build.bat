@echo off
REM Build script for GLB Transparent Viewer

echo ============================================
echo GLB Transparent Viewer - Build Script
echo ============================================
echo.

REM Check for dependencies
if not exist "third_party\glm" (
    echo ERROR: GLM not found! Running setup...
    call setup_deps.bat
)

if not exist build mkdir build
cd build

echo Configuring with CMake...
cmake .. -G "Visual Studio 17 2022" -A x64

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: CMake configuration failed!
    pause
    exit /b 1
)

echo.
echo Building Release configuration...
cmake --build . --config Release

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ============================================
echo Build successful!
echo ============================================
echo.
echo To run: .\Release\GLBTransparentViewer.exe ^<path_to_model.glb^>
echo.

pause