# GLB Transparent Viewer v1.0

A native Windows application for viewing .glb 3D models with transparent window support.

## Features

- **Transparent window** - Model appears to float on your desktop
- **Native Windows app** - No browser, no Electron, pure Win32 + OpenGL
- **GLB/.gltf support** - Full binary glTF 2.0 format support
- **Skeleton interaction** - Click joints to select, manipulate poses
- **Animation playback** - Play/pause/loop embedded animations
- **Click-through mode** - Pass clicks through to desktop when enabled (TAB key)

## Controls

| Key | Action |
|-----|--------|
| Left Click + Drag | Rotate camera around model |
| Q / E | Zoom in / out |
| 1-9 | Select skeleton joint (1=root, then hierarchy) |
| 0 | Reset skeleton to bind pose |
| S | Toggle skeleton visibility |
| M | Toggle mesh visibility |
| A | Play animation |
| SPACE | Stop/pause animation |
| TAB | Toggle click-through mode |
| ESC | Exit |

## Requirements

- Windows 10/11 (64-bit)
- OpenGL 3.0+ capable GPU
- Visual Studio 2019+ or MinGW/GCC

## Building

### Using Visual Studio with CMake

```powershell
# Clone into project directory
cd glb_transparent_viewer

# Create build directory
mkdir build
cd build

# Configure
cmake .. -G "Visual Studio 17 2022" -A x64

# Build
cmake --build . --config Release
```

### Using MinGW

```bash
mkdir build && cd build
cmake .. -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release
mingw32-make -j4
```

## Usage

```bash
GLBTransparentViewer.exe path/to/model.glb
```

## Project Structure

```
glb_transparent_viewer/
├── CMakeLists.txt          # Build configuration
├── README.md               # This file
├── include/
│   ├── Window.h           # Transparent window class
│   ├── Renderer.h         # OpenGL renderer
│   ├── GLBLoader.h        # GLB file loader
│   ├── Skeleton.h         # Skeleton manipulation
│   └── Input.h            # Input handling
├── src/
│   ├── main.cpp           # Entry point
│   ├── Window.cpp         # Win32 window impl
│   ├── Renderer.cpp       # OpenGL rendering
│   ├── GLBLoader.cpp      # glTF/glb parsing
│   ├── Skeleton.cpp       # Skeleton interaction
│   └── Input.cpp          # Input processing
├── third_party/           # External deps
│   ├── tinygltf/         # glTF loader
│   └── glm/              # Math library
└── shaders/              # GLSL shaders
```

## Dependencies

- **tinygltf** - Header-only glTF 2.0 loader
- **glm** - OpenGL Mathematics library  
- **OpenGL** - System library (Windows has built-in support)

## Version 1.0 Known Limitations

- No full material support (PBR shaders not implemented yet)
- Skeleton manipulation is basic (rotation around local axes)
- No texture support yet
- Click-through detection uses simple bounding sphere per joint

## Roadmap

- [ ] v1.1 - Add PBR material support
- [ ] v1.1 - Add texture loading
- [ ] v1.2 - Inverse kinematics for posing
- [ ] v1.2 - Animation blending
- [ ] v1.3 - Multiple model loading
- [ ] v1.3 - Save/restore poses

## License

MIT License - Create to integrate 3D avatars with desktop environments.
