@echo off
cd /d "%~dp0"

echo ================================================
echo Finding Visual Studio Generator
echo ================================================
echo.

if not exist "CMakeLists.txt" (
    echo ERROR: CMakeLists.txt not found in %CD%
    pause
    exit /b 1
)

REM List available generators
echo Available Generators:
echo ---------------------
cmake --help | findstr "Visual Studio"
echo.

REM Try generators - test with temp dir first
set /a COUNT=0

for %%G in (
    "Visual Studio 18 2026"
    "Visual Studio 17 2022" 
    "Visual Studio 16 2019"
    "Visual Studio 15 2017"
    "Visual Studio 14 2015"
    "Visual Studio 12 2013"
) do (
    set /a COUNT+=1
    echo [!COUNT!] Trying %%G...
    
    REM Quick test configuration
    cmake -B test_build -S . -G %%G -A x64 ^> test_output.txt 2^>^&1
    if !errorlevel! equ 0 (
        echo     SUCCESS!
        rmdir /S /Q test_build 2>nul
        del test_output.txt
        goto :configure_with %%G
    ) else (
        rmdir /S /Q test_build 2>nul
        del test_output.txt
    )
)

echo.
echo ERROR: No working generator found!
echo.
echo Try running this from "Developer Command Prompt for VS 2026"
echo (Search Start menu for "Developer")
echo.
pause
exit /b 1

:configure_with
set "WORKING_GEN=%~1"
echo.
echo Using generator: %WORKING_GEN%
echo.

if exist build rmdir /S /Q build
mkdir build

cmake -B build -S . -G %WORKING_GEN% -A x64
if %errorlevel% neq 0 (
    echo Configuration failed!
    pause
    exit /b 1
)

echo.
echo Building...
cmake --build build --config Release --parallel
if %errorlevel% neq 0 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo ================================================
echo BUILD SUCCESSFUL!
echo ================================================
echo.
echo Executable: %CD%\build\Release\GLBTransparentViewer.exe
echo.
pause
