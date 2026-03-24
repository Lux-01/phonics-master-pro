#pragma once

#include <windows.h>
#include <dwmapi.h>
#include <string>
#include <functional>

// Windows 10/11 acrylic blur constants
#ifndef DWMWA_USE_IMMERSIVE_DARK_MODE
#define DWMWA_USE_IMMERSIVE_DARK_MODE 20
#endif

#ifndef DWMWA_WINDOW_CORNER_PREFERENCE
#define DWMWA_WINDOW_CORNER_PREFERENCE 33
#endif

#pragma comment(lib, "dwmapi.lib")

class Window {
public:
    Window(int width, int height, const std::wstring& title);
    ~Window();

    bool Create();
    void Show();
    void Hide();
    void Destroy();
    
    // Main message loop
    void ProcessMessages();
    bool ShouldClose() const { return m_shouldClose; }
    
    // Window properties
    void SetTransparency(int alpha);  // 0-255
    void SetClickThrough(bool enable);
    void SetAlwaysOnTop(bool enable);
    void SetWindowPos(int x, int y);
    void SetWindowSize(int width, int height);
    
    // Windows 10/11 acrylic/mica effect
    void EnableAcrylicEffect();
    void EnableMicaEffect();
    
    // GL context
    HWND GetHandle() const { return m_hwnd; }
    HDC GetDC() const { return m_hdc; }
    HGLRC GetGLContext() const { return m_hglrc; }
    
    // Input callbacks
    void SetMouseMoveCallback(std::function<void(int, int)> callback);
    void SetMouseClickCallback(std::function<void(int, int, bool)> callback);
    void SetKeyCallback(std::function<void(int, bool)> callback);
    
    // Getters
    int GetWidth() const { return m_width; }
    int GetHeight() const { return m_height; }
    bool IsClickThrough() const { return m_clickThrough; }

private:
    static LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam);
    bool CreateGLContext();
    void DestroyGLContext();
    
    HWND m_hwnd;
    HDC m_hdc;
    HGLRC m_hglrc;
    
    int m_width, m_height;
    std::wstring m_title;
    bool m_shouldClose;
    bool m_clickThrough;
    
    // Callbacks
    std::function<void(int, int)> m_mouseMoveCallback;
    std::function<void(int, int, bool)> m_mouseClickCallback;
    std::function<void(int, bool)> m_keyCallback;
    
    static Window* s_instance;
};
