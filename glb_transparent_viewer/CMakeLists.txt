cmake_minimum_required(VERSION 3.16)
project(GLBTransparentViewer VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find packages
find_package(OpenGL REQUIRED)
find_package(Threads REQUIRED)

# GLFW for window/context (we'll use it for OpenGL context but control Win32 window ourselves)
set(GLFW_BUILD_DOCS OFF CACHE BOOL "" FORCE)
set(GLFW_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(GLFW_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)

# GLEW for OpenGL extensions
find_package(GLEW QUIET)

# Source files
set(SOURCES
    src/main.cpp
    src/Window.cpp
    src/Renderer.cpp
    src/GLBLoader.cpp
    src/Skeleton.cpp
    src/Input.cpp
)

add_executable(${PROJECT_NAME} WIN32 ${SOURCES})

target_include_directories(${PROJECT_NAME} PRIVATE
    ${CMAKE_SOURCE_DIR}/include
    ${CMAKE_SOURCE_DIR}/third_party/tinygltf
    ${CMAKE_SOURCE_DIR}/third_party/glm
)

target_link_libraries(${PROJECT_NAME} PRIVATE
    OpenGL::GL
    OpenGL::GLU
    ${CMAKE_THREAD_LIBS_INIT}
    gdi32
    user32
    shell32
    dwmapi  # For DWM transparency effects
)

# Set subsystem to Windows (not console)
set_target_properties(${PROJECT_NAME} PROPERTIES
    LINK_FLAGS "/SUBSYSTEM:WINDOWS"
)
