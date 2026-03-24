@echo off
REM Diagnostic tool to help find the right VS setup

echo ================================================
echo Visual Studio Detection Tool
echo ================================================
echo.

REM Check environment variables
echo Environment Variables:
echo   VS2022INSTALLDIR=%VS2022INSTALLDIR%
echo   VS170COMNTOOLS=%VS170COMNTOOLS%
echo   VSINSTALLDIR=%VSINSTALLDIR%
echo   VisualStudioVersion=%VisualStudioVersion%
echo.

REM Check for CMake
echo CMake Check:
cmake --version > nul 2>&1
if %errorlevel% neq 0 (
    echo   CMake NOT found in PATH
) else (
    echo   CMake found!
    cmake --version
)
echo.

REM Check for VS Where tool
echo VSWhere check:
if exist "%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe" (
    echo   VSWhere found!
    echo.
    "%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe" -all -products *
) else (
    echo   VSWhere not found at standard location
)
echo.

REM Check cl.exe
echo Compiler Check:
where cl > nul 2>&1
if %errorlevel% neq 0 (
    echo   cl.exe (MSVC) NOT found
    echo.
    echo ================================================
    echo IMPORTANT: You need to run this from
    echo   "Developer Command Prompt for VS 2026"
    echo   (Search in Start menu for "Developer")
    echo ================================================
) else (
    echo   cl.exe found
    cl 2>&1 | findstr "Microsoft"
)
echo.

REM List CMake generators
echo.
echo Available CMake Generators:
echo ================================================
cmake --help | findstr Visual

pause
