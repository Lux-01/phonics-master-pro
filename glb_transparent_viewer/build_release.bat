@echo off
setlocal EnableDelayedExpansion

echo ================================================
echo Finding Visual Studio Generator
echo ================================================
echo.

REM Get available generators
echo Checking available CMake generators...
cmake --help > nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: CMake not working
    pause
    exit /b 1
)

REM Try to find Visual Studio generators
cmake --help | findstr /C:"Visual Studio" > vs_generators.txt 2>nul
if %errorlevel% neq 0 (
    echo No Visual Studio generators found
) else (
    echo Found Visual Studio generators:
    type vs_generators.txt
)
del vs_generators.txt 2>nul

echo.

cd /d "%~dp0"

if not exist "CMakeLists.txt" (
    echo ERROR: CMakeLists.txt not found!
    pause
    exit /b 1
)

if not exist "build" mkdir build

REM Try various generator formats that might exist
set FOUND=0

for %%G in (
    "Visual Studio 18 2026"
    "Visual Studio 17 2022"
    "Visual Studio 16 2019"
) do (
    if !FOUND! equ 0 (
        echo.
        echo Trying: %%G
        cmake -B build_test -S . -G %%G -A x64 > nul 2>&1
        if !errorlevel! equ 0 (
            echo SUCCESS! Found: %%G
            rmdir /S /Q build_test 2>nul
            cmake -B build -S . -G %%G -A x64
            set FOUND=1
        ) else (
            rmdir /S /Q build_test 2>nul
        )
    )
)

if !FOUND! equ 0 (
    echo.
    echo ================================================
    echo ERROR: Could not find any Visual Studio generator!
    echo ================================================
    echo.
    echo Make sure you installed Visual Studio with C++ support.
    echo Or open "Developer Command Prompt for VS 2026" and retry.
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================
echo Building Release...
echo ================================================
cmake --build build --config Release
if %errorlevel% neq 0 (
    echo.
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo ================================================
echo BUILD SUCCESSFUL!
echo ================================================
echo.
pause
