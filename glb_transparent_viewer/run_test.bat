@echo off
REM Quick launcher for testing

echo GLB Transparent Viewer - Test Launcher
echo =======================================
echo.

if not exist "build\Release\GLBTransparentViewer.exe" (
    echo ERROR: Executable not found!
    echo Please build first: run build.bat
    pause
    exit /b 1
)

if not exist "test_models" mkdir test_models

if exist "%~1" (
    echo Loading model: %~1
    .\build\Release\GLBTransparentViewer.exe "%~1"
) else if exist "test_models\*.glb" (
    for %%f in (test_models\*.glb) do (
        echo Loading test model: %%f
        .\build\Release\GLBTransparentViewer.exe "%%f"
        goto :done
    )
) else (
    echo No model specified and no test models found!
    echo.
    echo Usage: run_test.bat ^<path_to_model.glb^>
    echo.
    echo Controls:
    echo   Mouse drag: Rotate camera
    echo   Q/E: Zoom
    echo   S: Toggle skeleton
    echo   M: Toggle mesh
    echo   0-9: Select joints
    echo   TAB: Toggle click-through
    echo   ESC: Exit
    .
)

:done