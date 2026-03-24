#include <windows.h>
#include <iostream>
#include <memory>
#include <string>
#include "Window.h"
#include "Renderer.h"
#include "GLBLoader.h"
#include "Skeleton.h"
#include "Input.h"

// Global instances for callbacks
std::unique_ptr<Window> g_window;
std::unique_ptr<Renderer> g_renderer;
std::unique_ptr<GLBLoader> g_loader;
std::unique_ptr<LoadedModel> g_model;
std::unique_ptr<Input> g_input;

// Mouse interaction state
bool g_isDragg = false;
int g_lastMouseX = 0;
int g_lastMouseY = 0;
int g_selectedJoint = -1;
bool g_showSkeleton = true;
bool g_showMesh = true;
float g_animationSpeed = 1.0f;

void Update(float deltaTime) {
    if (g_model && g_model->hasAnimations) {
        g_loader->UpdateAnimation(*g_model, deltaTime * g_animationSpeed);
    }
}

void Render() {
    if (!g_window || !g_renderer) return;

    // Clear with transparent background
    g_renderer->Clear(0.0f, 0.0f, 0.0f, 0.0f);
    g_renderer->ClearTransparent();

    g_renderer->BeginFrame();

    // Draw the 3D model
    if (g_model) {
        if (g_showMesh) {
            for (const auto& mesh : g_model->meshes) {
                g_renderer->DrawMesh(mesh);
            }
        }

        // Draw skeleton overlay
        if (g_showSkeleton && g_model->skeleton.joints.size() > 0) {
            g_renderer->DrawSkeleton(g_model->skeleton);
        }
    }

    g_renderer->EndFrame();
}

void HandleMouseMove(int x, int y) {
    if (g_isDragg && g_renderer) {
        int deltaX = x - g_lastMouseX;
        int deltaY = y - g_lastMouseY;
        g_renderer->RotateCamera(deltaX * 0.5f, deltaY * 0.5f);
        g_lastMouseX = x;
        g_lastMouseY = y;
    }
}

void HandleMouseClick(int x, int y, bool isDown) {
    g_isDragg = isDown;
    g_lastMouseX = x;
    g_lastMouseY = y;

    // If we have a model and click, try to select a joint
    if (isDown && g_model && g_showSkeleton) {
        // TODO: Ray-sphere intersection to select joints
    }
}

void HandleKey(int key, bool isDown) {
    if (!isDown) return;

    switch (key) {
        case VK_ESCAPE:
            g_window->Destroy();
            break;
        case 'Q':
            if (g_cameraDist > 0.5f) g_renderer->ZoomCamera(-0.5f);
            break;
        case 'E':
            g_renderer->ZoomCamera(0.5f);
            break;
        case 'S':
            g_showSkeleton = !g_showSkeleton;
            break;
        case 'M':
            g_showMesh = !g_showMesh;
            break;
        case 'A':
            if (g_model) g_loader->PlayAnimation(*g_model, true);
            break;
        case VK_SPACE:
            if (g_model) {
                if (g_model->hasAnimations) {
                    g_loader->StopAnimation(*g_model);
                } else {
                    g_loader->PlayAnimation(*g_model);
                }
            }
            break;
        case VK_TAB:
            // Toggle click-through mode
            g_window->SetClickThrough(!g_window->IsClickThrough());
            break;
        case '0':
            if (g_model) g_loader->ResetSkeleton(*g_model);
            break;
    }

    // Number keys for joint selection (1-9)
    if (key >= '1' && key <= '9' && g_model) {
        int jointIndex = key - '1';
        if (jointIndex < g_loader->GetJointCount(*g_model)) {
            g_selectedJoint = jointIndex;
            const auto& name = g_loader->GetJointName(*g_model, g_selectedJoint);
            OutputDebugStringA(("Selected joint: " + name + "\n").c_str());
        }
    }
}

void SetupInputCallbacks() {
    g_window->SetMouseMoveCallback(HandleMouseMove);
    g_window->SetMouseClickCallback(HandleMouseClick);
    g_window->SetKeyCallback(HandleKey);
}

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    // Parse command line for file path
    std::string glbPath;
    if (__argc > 1) {
        glbPath = __argv[1];
    } else {
        MessageBoxA(NULL, 
            "Usage: GLBTransparentViewer.exe <path_to_model.glb>\n\n"
            "Controls:\n"
            "Left Click + Drag: Rotate camera\n"
            "Q/E: Zoom in/out\n"
            "S: Toggle skeleton\n"
            "M: Toggle mesh\n"
            "0: Reset skeleton\n"
            "1-9: Select joint\n"
            "TAB: Toggle click-through mode\n"
            "ESC: Exit",
            "GLB Transparent Viewer v1.0",
            MB_OK | MB_ICONINFORMATION);
        return 0;
    }

    try {
        // Create window
        g_window = std::make_unique<Window>(1024, 768, L"GLB Transparent Viewer");
        if (!g_window->Create()) {
            MessageBoxA(NULL, "Failed to create window", "Error", MB_OK | MB_ICONERROR);
            return 1;
        }

        // Enable transparency effects
        g_window->EnableAcrylicEffect();
        g_window->SetTransparency(200);  // Semi-transparent

        // Create renderer
        g_renderer = std::make_unique<Renderer>();
        if (!g_renderer->Initialize(1024, 768)) {
            MessageBoxA(NULL, "Failed to initialize renderer", "Error", MB_OK | MB_ICONERROR);
            return 1;
        }

        // Load GLB file
        g_loader = std::make_unique<GLBLoader>();
        g_model = g_loader->LoadGLB(glbPath);

        if (!g_model) {
            MessageBoxA(NULL, ("Failed to load: " + glbPath).c_str(), "Error", MB_OK | MB_ICONERROR);
            return 1;
        }

        // Set initial camera looking at model center
        if (!g_model->meshes.empty()) {
            glm::vec3 center = g_model->center;
            float radius glm::length(g_model->boundsMax - g_model->boundsMin) / 2.0f;
            g_renderer->SetCamera(center.x, center.y, center.z + radius * 3, center.x, center.y, center.z);
        }

        // Setup input handling
        SetupInputCallbacks();

        // Show the window
        g_window->Show();

        // Main loop
        LARGE_INTEGER frequency, lastTime;
        QueryPerformanceFrequency(&frequency);
        QueryPerformanceCounter(&lastTime);

        while (!g_window->ShouldClose()) {
            g_window->ProcessMessages();

            // Calculate delta time
            LARGE_INTEGER currentTime;
            QueryPerformanceCounter(&currentTime);
            float deltaTime = (currentTime.QuadPart - lastTime.QuadPart) / (float)frequency.QuadPart;
            lastTime = currentTime;

            // Update logic
            Update(deltaTime);

            // Render
            Render();

            // Swap buffers
            SwapBuffers(g_window->GetDC());

            // Cap to ~60 FPS
            Sleep(16);
        }

    } catch (const std::exception& e) {
        MessageBoxA(NULL, e.what(), "Exception", MB_OK | MB_ICONERROR);
        return 1;
    }

    return 0;
}
