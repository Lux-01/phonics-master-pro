@echo off
REM Setup script for GLB Transparent Viewer dependencies

echo Setting up dependencies for GLB Transparent Viewer...

if not exist third_party mkdir third_party
cd third_party

REM Download GLM (OpenGL Mathematics)
echo Downloading GLM...
if not exist glm (
    curl -L -o glm.zip https://github.com/g-truc/glm/releases/download/0.9.9.8/glm-0.9.9.8.zip
    powershell -command "Expand-Archive -Path 'glm.zip' -DestinationPath '.'"
    move glm-0.9.9.8\glm glm
    rmdir /s /q glm-0.9.9.8
    del glm.zip
)

REM Download tinygltf
echo Downloading tinygltf...
if not exist tinygltf (
    mkdir tinygltf
    curl -L -o tinygltf/tiny_gltf.h https://raw.githubusercontent.com/syoyo/tinygltf/release/tiny_gltf.h
    curl -L -o tinygltf/stb_image.h https://raw.githubusercontent.com/syoyo/tinygltf/release/stb_image.h
    curl -L -o tinygltf/stb_image_write.h https://raw.githubusercontent.com/syoyo/tinygltf/release/stb_image_write.h
)

echo Dependencies setup complete!
echo.
echo Now run: cmake -B build -S . -G "Visual Studio 17 2022" -A x64
echo Then: cmake --build build --config Release
pause