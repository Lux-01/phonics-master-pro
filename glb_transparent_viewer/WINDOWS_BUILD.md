# GLB Transparent Viewer - Windows Build Guide

## Option 1: Visual Studio Solution (No CMake Required)

### Prerequisites
1. **Visual Studio 2022** (Community edition is free)
   - Download: https://visualstudio.microsoft.com/vs/community/
   - During install, select **"Desktop development with C++"** workload

2. **GLM Library** (OpenGL Mathematics)
   - Download: https://github.com/g-truc/glm/releases
   - Extract to: `C:\Libraries\glm` (or anywhere you prefer)

### Step-by-Step Build

1. **Create a new Empty C++ Project**
   - Open Visual Studio
   - File → New → Project → Empty Project
   - Name: `GLBTransparentViewer`
   - Location: Choose your preferred folder

2. **Add Source Files**
   Right-click on project → Add → Existing Item... → Add all files from `src/` folder:
   - main.cpp
   - Window.cpp
   - Renderer.cpp
   - GLBLoader.cpp
   - Skeleton.cpp
   - Input.cpp

3. **Add Include Directories**
   Right-click project → Properties → C/C++ → General → Additional Include Directories:
   ```
   $(ProjectDir)\include;C:\Libraries\glm;%(AdditionalIncludeDirectories)
   ```
   (Adjust path to where you extracted GLM)

4. **Link Required Libraries**
   Right-click project → Properties → Linker → Input → Additional Dependencies:
   ```
   opengl32.lib;glu32.lib;gdi32.lib;user32.lib;shell32.lib;dwmapi.lib;%(AdditionalDependencies)
   ```

5. **Set Windows Subsystem**
   Right-click project → Properties → Linker → System → Subsystem:
   ```
   Windows (/SUBSYSTEM:WINDOWS)
   ```

6. **Add Preprocessor Definition**
   Right-click project → Properties → C/C++ → Preprocessor → Preprocessor Definitions:
   ```
   _WINDOWS;NOMINMAX;_CRT_SECURE_NO_WARNINGS;%(PreprocessorDefinitions)
   ```

7. **Build!**
   - Build → Build Solution (Ctrl+Shift+B)
   - Executable will be in `Debug\` or `Release\` folder

---

## Option 2: Install CMake

If you prefer using CMake:

1. **Download CMake**
   - https://cmake.org/download/
   - Choose "Windows x64 Installer"
   - During install, select **"Add CMake to the system PATH"**

2. **Restart your terminal/command prompt**

3. **Verify CMake is installed**
   ```cmd
   cmake --version
   ```

4. **Run the build script again**
   ```cmd
   build.bat
   ```

---

## Option 3: Simple Batch Build (MinGW)

If you have MinGW installed:

```batch
@echo off
g++ -std=c++17 -O2 -o GLBTransparentViewer.exe ^
    src\main.cpp src\Window.cpp src\Renderer.cpp src\GLBLoader.cpp src\Skeleton.cpp src\Input.cpp ^
    -I include -I C:\Libraries\glm ^
    -lopengl32 -lglu32 -lgdi32 -luser32 -lshell32 -ldwmapi ^
    -mwindows
```

---

## Quick Checklist

- [ ] Visual Studio 2022 installed with C++ workload
- [ ] GLM library downloaded and extracted
- [ ] All source files added to project
- [ ] Include paths set correctly
- [ ] Required libraries linked (opengl32, gdi32, dwmapi, etc.)
- [ ] Windows subsystem selected (not Console)

---

## Troubleshooting

**"Cannot open include file: 'glm/glm.hpp'"**
→ Check your Additional Include Directories path to GLM

**"Unresolved external symbol" errors**
→ Make sure all required libraries are in Additional Dependencies

**"Entry point not found" or console window appears**
→ Check that Subsystem is set to Windows, not Console

**GL/glew.h not found**
→ This project uses standard OpenGL headers, not GLEW. Make sure you're not including GLEW headers.

---

## Dependencies Reference

### Static/System Libraries (already on Windows):
- `opengl32.lib` - OpenGL
- `glu32.lib` - GLU utilities
- `gdi32.lib` - GDI graphics
- `user32.lib` - User32 (windowing)
- `shell32.lib` - Shell API
- `dwmapi.lib` - Desktop Window Manager (for transparency)

### Download Required:
- **GLM**: https://github.com/g-truc/glm/releases

### Not Required (included in headers):
This version uses stub implementations for glTF loading. For full glTF support, you'd need tinygltf but it's not required to compile.

---

**Need help?** Check the source code - it's designed to compile with minimal dependencies!
