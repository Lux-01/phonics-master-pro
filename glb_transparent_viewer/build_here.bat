@echo off
REM Build Here - No directory navigation required
REM Run this from wherever the project files are

echo ============================================
echo GLB Transparent Viewer - Build Here
echo ============================================
echo.

REM Get the directory where this batch file is located
set "PROJECT_DIR=%~dp0"
set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"

echo Project directory: %PROJECT_DIR%

REM Check for Visual Studio
where cl > nul 2> nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Visual Studio C++ compiler not found!
    echo.
    echo Please open "Developer Command Prompt for VS 2022"
    echo Search Windows start menu for: "Developer Command Prompt"
    echo.
    pause
    exit /b 1
)

REM Check for GLM
if not exist "%PROJECT_DIR%\third_party\glm\glm\glm.hpp" (
    echo GLM library not found. Downloading...
    curl -L -o "%PROJECT_DIR%\glm.zip" https://github.com/g-truc/glm/releases/download/0.9.9.8/glm-0.9.9.8.zip
    
    REM Create third_party directory
    if not exist "%PROJECT_DIR%\third_party" mkdir "%PROJECT_DIR%\third_party"
    
    powershell -command "Expand-Archive -Path '%PROJECT_DIR%\glm.zip' -DestinationPath '%PROJECT_DIR%\third_party'"
    
    REM Move glm folder to correct location
    if exist "%PROJECT_DIR%\third_party\glm-0.9.9.8\glm" (
        move "%PROJECT_DIR%\third_party\glm-0.9.9.8\glm" "%PROJECT_DIR%\third_party\glm"
        rmdir /s /q "%PROJECT_DIR%\third_party\glm-0.9.9.8"
    )
    
    del "%PROJECT_DIR%\glm.zip"
    echo GLM downloaded.
)

REM Create build directory
if not exist "%PROJECT_DIR%\build" mkdir "%PROJECT_DIR%\build"

echo.
echo Compiling with Visual C++...
echo This may take a minute...
echo.

REM Compile from the project directory
cl /EHsc /O2 /W3 /nologo /c /Fo"%PROJECT_DIR%\build\\" ^
   /I "%PROJECT_DIR%\include" ^
   /I "%PROJECT_DIR%\third_party\glm" ^
   /D "NOMINMAX" ^
   /D "_CRT_SECURE_NO_WARNINGS" ^
   /D "_WINDOWS" ^
   /D "WIN32_LEAN_AND_MEAN" ^
   "%PROJECT_DIR%\src\main.cpp" ^
   "%PROJECT_DIR%\src\Window.cpp" ^
   "%PROJECT_DIR%\src\Renderer.cpp" ^
   "%PROJECT_DIR%\src\GLBLoader.cpp" ^
   "%PROJECT_DIR%\src\Skeleton.cpp" ^
   "%PROJECT_DIR%\src\Input.cpp"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ============================================
    echo COMPILATION FAILED
    echo ============================================
    echo.
    echo Make sure you're running from the folder containing:
    echo   - src\ folder with .cpp files
    echo   - include\ folder with .h files
    echo   - And this build_here.bat file
    echo.
    pause
    exit /b 1
)

echo.
echo Linking...
link /nologo /SUBSYSTEM:WINDOWS /OUT:"%PROJECT_DIR%\build\GLBTransparentViewer.exe" ^
   "%PROJECT_DIR%\build\main.obj" ^
   "%PROJECT_DIR%\build\Window.obj" ^
   "%PROJECT_DIR%\build\Renderer.obj" ^
   "%PROJECT_DIR%\build\GLBLoader.obj" ^
   "%PROJECT_DIR%\build\Skeleton.obj" ^
   "%PROJECT_DIR%\build\Input.obj" ^
   opengl32.lib glu32.lib gdi32.lib user32.lib shell32.lib dwmapi.lib

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ============================================
    echo LINKING FAILED
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
echo Executable: %PROJECT_DIR%\build\GLBTransparentViewer.exe
echo.
if exist "%PROJECT_DIR%\build\GLBTransparentViewer.exe" (
    echo File size: 
    dir "%PROJECT_DIR%\build\GLBTransparentViewer.exe" | findstr "GLBTransparentViewer.exe"
    echo.
)
echo Usage: GLBTransparentViewer.exe ^<path_to_model.glb^>
echo.
echo Controls:
echo   Left Click + Drag = Rotate camera
echo   Q / E = Zoom in/out
echo   ESC = Exit
echo.
pause
