# GLB Transparent Viewer v1.0 - Project Summary

## Overview
A native Windows application that displays .glb 3D models in a transparent window, allowing the model to appear to float on the desktop. Interactive skeleton manipulation included.

## Key Features (v1.0)

### ✅ Implemented
1. **Transparent Window**
   - Win32 layered window with per-pixel alpha
   - Acrylic/Mica effects on Windows 10/11
   - Adjustable transparency
   - Click-through mode (TAB key)
   - Always-on-top support

2. **OpenGL Renderer**
   - OpenGL 2.1 compatible (fixed function pipeline)
   - Alpha blending for transparency
   - Camera rotation/zoom
   - Skeleton visualization

3. **GLB Loading**
   - Framework ready for tinygltf integration
   - Basic skeleton extraction
   - Simple mesh placeholder

4. **Skeleton Interaction**
   - Joint selection (0-9 keys)
   - Joint rotation/translation API
   - Visual joint/bone rendering
   - Hierarchy visualization

5. **Input System**
   - Mouse drag for camera
   - Keyboard shortcuts
   - Zoom (Q/E keys)
   - Toggle visibility (S/M keys)

## Project Structure

```
glb_transparent_viewer/
├── CMakeLists.txt              # CMake build configuration
├── setup_deps.bat              # Downloads GLM + tinygltf
├── build.bat                   # One-click build script
├── run_test.bat               # Quick launch script
├── README.md                   # User documentation
├── PROJECT_SUMMARY.md         # This file
├── include/
│   ├── Window.h               # Transparent window class
│   ├── Renderer.h             # OpenGL renderer
│   ├── GLBLoader.h            # GLB file loader
│   ├── Skeleton.h             # Skeleton controller
│   └── Input.h                # Input handling
└── src/
    ├── main.cpp               # Entry point + main loop
    ├── Window.cpp             # Win32 window implementation
    ├── Renderer.cpp           # OpenGL rendering
    ├── GLBLoader.cpp          # glTF loading (stub implemented)
    ├── Skeleton.cpp           # Skeleton manipulation
    └── Input.cpp              # Input processing
```

## Build Instructions

### Prerequisites
- Windows 10/11 (64-bit)
- Visual Studio 2022 with C++ support, OR CMake 3.16+

### Quick Start

```powershell
# Clone/download the project
cd glb_transparent_viewer

# Run setup (downloads GLM and tinygltf)
setup_deps.bat

# Build
build.bat

# Run with a model
run_test.bat path/to/your/model.glb
```

### Manual Build (CMake)

```powershell
# Install dependencies first
setup_deps.bat

# Generate project files
cmake -B build -S . -G "Visual Studio 17 2022" -A x64

# Build
cmake --build build --config Release

# Run
.\build\Release\GLBTransparentViewer.exe model.glb
```

## Controls

| Key | Action |
|-----|--------|
| Left Click + Drag | Rotate camera around model |
| Q / E | Zoom in / out |
| 0 | Reset skeleton pose |
| 1-9 | Select skeleton joint by index |
| S | Toggle skeleton visibility |
| M | Toggle mesh visibility |
| A | Play animation |
| SPACE | Stop/pause animation |
| TAB | Toggle click-through mode (pass clicks to desktop) |
| ESC | Exit |

## Technical Implementation

### Transparent Window
- Uses `WS_EX_LAYERED` window style for per-pixel alpha
- DWM API enables acrylic/mica effects
- `SetLayeredWindowAttributes()` controls overall transparency
- Toggle `WS_EX_TRANSPARENT` for click-through mode

### GLB Loading
- Framework for tinygltf integration (header-only library)
- Supports glTF 2.0 format
- Extracts meshes, skeletons, and animations
- Generates OpenGL VAOs/VBOs for geometry

### Skeleton System
- Joint hierarchy with local/global transforms
- Inverse bind pose matrices for skinning
- Visual rendering of joints (green cubes) and bones (cyan lines)
- Simple manipulation API for posing

### Rendering
- Fixed-function OpenGL pipeline (v1 compatibility)
- Transparent viewport background
- Blending enabled for proper alpha composition
- Basic Phong-style shading

## Version 1.0 Limitations

### Not Yet Implemented
- [ ] Full glTF material support (PBR shaders)
- [ ] Texture loading and rendering
- [ ] Animation playback (infrastructure there, needs completion)
- [ ] Ray-casting for joint selection via mouse
- [ ] Full mesh rendering (currently uses placeholders)
- [ ] Joint IK (inverse kinematics)

### Requires 3rd Party Libs
- GLM: Mathematics library
- tinygltf: glTF loader (header-only)

Both auto-downloaded by `setup_deps.bat`.

## Architecture Highlights

### No Browser/Web Tech
- Pure Win32 API for windowing
- OpenGL for rendering (not WebGL)
- Native C++ codebase

### Modular Design
```cpp
Window       - Win32 transparent window
Renderer     - OpenGL rendering context
GLBLoader    - File loading + skeleton extraction
Skeleton     - Joint manipulation
Input        - Mouse/keyboard handling
```

### Extensible
- Easy to add full PBR shaders
- Animation system ready for completion
- Support for multiple models (not hardcoded)

## Roadmap

### v1.1 (Materials + Textures)
- [ ] Load and display textures
- [ ] PBR material shader
- [ ] Normal maps
- [ ] Emissive materials

### v1.2 (Animation)
- [ ] Full animation playback
- [ ] Animation blending
- [ ] Timeline scrubbing

### v1.3 (Tools)
- [ ] Joint picker with raycasting
- [ ] Pose saving/loading
- [ ] Animation recording
- [ ] Screenshot export

### v2.0 (Advanced)
- [ ] Multiple model support
- [ ] Shader editor
- [ ] Physics simulation
- [ ] VR/AR passthrough

## Use Cases

1. **Desktop Avatar** - Load Mixamo character, pose for desktop companion
2. **Animation Preview** - Quick glTF animation viewer
3. **Reference Model** - Keep 3D model visible while working
4. **Vtubing** - Potential base for avatar integration
5. **3D Sculpting Ref** - Load reference model on screen

## License
MIT - Free to use, modify, distribute.
