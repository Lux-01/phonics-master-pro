@echo off
REM GLB Transparent Viewer - Visual Studio Project Setup
REM Run this on Windows to automatically set up the VS project

echo ================================================
echo GLB Transparent Viewer - VS Project Setup
echo ================================================

REM Check for Visual Studio
where cl >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Visual Studio not found in PATH
    echo Please run this from "Developer Command Prompt for VS 2022"
    pause
    exit /b 1
)

REM Create project structure
if not exist "GLBTransparentViewer" mkdir "GLBTransparentViewer"
cd "GLBTransparentViewer"

REM Create directories
mkdir src
mkdir include
mkdir third_party

REM Copy source files
echo Copying source files...
for %%f in (..\src\*.cpp) do copy "%%f" "src\" >nul
for %%f in (..\include\*.h) do copy "%%f" "include\" >nul

REM Create CMakeLists.txt for easy building
echo Creating build files...
(
echo cmake_minimum_required(VERSION 3.16)
echo project(GLBTransparentViewer VERSION 1.0 LANGUAGES CXX)
echo.
echo set(CMAKE_CXX_STANDARD 17)
echo set(CMAKE_CXX_STANDARD_REQUIRED ON)
echo.
echo # Source files
echo file(GLOB SOURCES "src/*.cpp")
echo file(GLOB HEADERS "include/*.h")
echo.
echo add_executable($PROJECT_NAME ${SOURCES} ${HEADERS})
echo.
echo # Include directories
echo target_include_directories($PROJECT_NAME PRIVATE)
echo     include
echo     ${CMAKE_SOURCE_DIR}/third_party/glm
echo ^)
echo.
echo # Preprocessor definitions
echo target_compile_definitions($PROJECT_NAME PRIVATE)
echo     _WINDOWS
echo     NOMINMAX
echo     _CRT_SECURE_NO_WARNINGS
echo ^)
echo.
echo # Link libraries
echo target_link_libraries($PROJECT_NAME)
echo     opengl32
echo     glu32
echo     gdi32
echo     user32
echo     shell32
echo     dwmapi
echo ^)
echo.
echo # Windows subsystem (no console)
echo set_target_properties($PROJECT_NAME PROPERTIES)
echo     WIN32_EXECUTABLE TRUE
echo ^)
) > CMakeLists.txt

REM Download GLM if not present
if not exist "third_party\glm" (
    echo Downloading GLM library...
    curl -L "https://github.com/g-truc/glm/releases/download/0.9.9.8/glm-0.9.9.8.zip" -o glm.zip
    powershell -Command "Expand-Archive -Path glm.zip -DestinationPath third_party -Force"
    move "third_party\glm-0.9.9.8" "third_party\glm"
    del glm.zip
)

echo.
echo ================================================
echo Setup complete!
echo.
echo To build the project:
echo   1. Open CMake GUI and select this folder
echo   OR
echo   2. Run: cmake -B build -S . -G "Visual Studio 17 2022" -A x64
echo      Run: cmake --build build --config Release
echo   OR
echo   3. Open in Visual Studio 2022:
echo      File -^> Open -^> CMake...
echo          Select this folder: %CD%
echo ================================================
pause
