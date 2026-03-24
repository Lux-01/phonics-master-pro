@echo off
REM QuickBuild - No CMake Required
REM This script builds using Visual Studio's CL compiler directly

echo ============================================
echo GLB Transparent Viewer - Quick Build
echo ============================================
echo.

REM Check for Visual Studio
where cl > nul 2> nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Visual Studio C++ compiler not found in PATH
    echo.
    echo Please run this from a "Developer Command Prompt for VS 2022"
    echo or "x64 Native Tools Command Prompt"
    echo.
    echo If Visual Studio is not installed:
    echo 1. Download Visual Studio Community from:
    echo    https://visualstudio.microsoft.com/vs/community/
    echo 2. Install "Desktop development with C++" workload
    echo 3. Open "Developer Command Prompt for VS 2022"
    echo 4. Run this script again
    echo.
    pause
    exit /b 1
)

REM Check for GLM
if not exist "third_party\glm\glm\glm.hpp" (
    echo GLM library not found. Downloading...
    curl -L -o glm.zip https://github.com/g-truc/glm/releases/download/0.9.9.8/glm-0.9.9.8.zip
    powershell -command "Expand-Archive -Path 'glm.zip' -DestinationPath 'third_party'"
    move third_party\glm-0.9.9.8\glm third_party\glm
    rmdir /s /q third_party\glm-0.9.9.8
    del glm.zip
    echo GLM downloaded.
)

if not exist "build" mkdir build
cd build

echo.
echo Compiling...
cl /EHsc /O2 /W3 /nologo ^
   /I "..\include" ^
   /I "..\third_party\glm" ^
   /D "NOMINMAX" ^
   /D "_CRT_SECURE_NO_WARNINGS" ^
   /D "_WINDOWS" ^
   /D "WIN32_LEAN_AND_MEAN" ^
   ..\src\main.cpp ^
   ..\src\Window.cpp ^
   ..\src\Renderer.cpp ^
   ..\src\GLBLoader.cpp ^
   ..\src\Skeleton.cpp ^
   ..\src\Input.cpp ^
   /link ^
   opengl32.lib glu32.lib gdi32.lib user32.lib shell32.lib dwmapi.lib ^
   /SUBSYSTEM:WINDOWS ^
   /OUT:GLBTransparentViewer.exe

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ============================================
    echo BUILD FAILED
    echo ============================================
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo BUILD SUCCESSFUL!
echo ============================================
echo.
echo Executable: build\GLBTransparentViewer.exe
echo.
echo Usage: GLBTransparentViewer.exe ^<path_to_model.glb^>
echo.
echo To test, place a .glb file in the build folder and run:
echo    GLBTransparentViewer.exe model.glb
echo.
pause
