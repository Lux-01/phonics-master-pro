#include "Window.h"
#include <gl/GL.h>
#include <iostream>

Window* Window::s_instance = nullptr;

Window::Window(int width, int height, const std::wstring& title)
    : m_hwnd(nullptr), m_hdc(nullptr), m_hglrc(nullptr)
    , m_width(width), m_height(height), m_title(title)
    , m_shouldClose(false), m_clickThrough(false) {
    s_instance = this;
}

Window::~Window() {
    Destroy();
    s_instance = nullptr;
}

bool Window::Create() {
    // Register window class
    WNDCLASSEXW wc = {};
    wc.cbSize = sizeof(WNDCLASSEXW);
    wc.lpfnWndProc = WindowProc;
    wc.hInstance = GetModuleHandle(nullptr);
    wc.lpszClassName = L"GLBTransparentViewerClass";
    wc.hCursor = LoadCursor(nullptr, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)GetStockObject(NULL_BRUSH);  // Transparent background
    
    if (!RegisterClassExW(&wc)) {
        return false;
    }

    // Calculate window size for client area
    RECT rect = { 0, 0, m_width, m_height };
    AdjustWindowRectEx(&rect, WS_OVERLAPPEDWINDOW, FALSE, WS_EX_LAYERED);

    // Create window with layered style for transparency
    m_hwnd = CreateWindowExW(
        WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_COMPOSITED,
        L"GLBTransparentViewerClass",
        m_title.c_str(),
        WS_POPUP | WS_VISIBLE | WS_BORDER | WS_CAPTION | WS_SYSMENU | WS_THICKFRAME,
        CW_USEDEFAULT, CW_USEDEFAULT,
        rect.right - rect.left, rect.bottom - rect.top,
        nullptr, nullptr,
        GetModuleHandle(nullptr),
        nullptr
    );

    if (!m_hwnd) {
        return false;
    }

    // Get device context
    m_hdc = GetDC(m_hwnd);

    // Create OpenGL context
    if (!CreateGLContext()) {
        return false;
    }

    // Set initial transparency
    SetTransparency(230);

    return true;
}

bool Window::CreateGLContext() {
    PIXELFORMATDESCRIPTOR pfd = {};
    pfd.nSize = sizeof(PIXELFORMATDESCRIPTOR);
    pfd.nVersion = 1;
    pfd.dwFlags = PFD_DRAW_TO_WINDOW | PFD_SUPPORT_OPENGL | PFD_DOUBLEBUFFER;
    pfd.iPixelType = PFD_TYPE_RGBA;
    pfd.cColorBits = 32;
    pfd.cAlphaBits = 8;  // Alpha channel for transparency
    pfd.cDepthBits = 24;
    pfd.cStencilBits = 8;
    pfd.iLayerType = PFD_MAIN_PLANE;

    int format = ChoosePixelFormat(m_hdc, &pfd);
    if (!format) {
        return false;
    }

    if (!SetPixelFormat(m_hdc, format, &pfd)) {
        return false;
    }

    m_hglrc = wglCreateContext(m_hdc);
    if (!m_hglrc) {
        return false;
    }

    if (!wglMakeCurrent(m_hdc, m_hglrc)) {
        return false;
    }

    // Enable vsync (if available)
    typedef BOOL (WINAPI *PFNWGLSWAPINTERVALPROC)(int);
    PFNWGLSWAPINTERVALPROC wglSwapIntervalEXT = 
        (PFNWGLSWAPINTERVALPROC)wglGetProcAddress("wglSwapIntervalEXT");
    if (wglSwapIntervalEXT) {
        wglSwapIntervalEXT(1);
    }

    return true;
}

void Window::DestroyGLContext() {
    if (m_hglrc) {
        wglMakeCurrent(nullptr, nullptr);
        wglDeleteContext(m_hglrc);
        m_hglrc = nullptr;
    }
    if (m_hdc) {
        ReleaseDC(m_hwnd, m_hdc);
        m_hdc = nullptr;
    }
}

void Window::Show() {
    ShowWindow(m_hwnd, SW_SHOW);
    UpdateWindow(m_hwnd);
}

void Window::Hide() {
    ShowWindow(m_hwnd, SW_HIDE);
}

void Window::Destroy() {
    DestroyGLContext();
    if (m_hwnd) {
        DestroyWindow(m_hwnd);
        m_hwnd = nullptr;
    }
    UnregisterClassW(L"GLBTransparentViewerClass", GetModuleHandle(nullptr));
}

void Window::ProcessMessages() {
    MSG msg;
    while (PeekMessage(&msg, nullptr, 0, 0, PM_REMOVE)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
}

void Window::SetTransparency(int alpha) {
    // Use SetLayeredWindowAttributes for per-pixel alpha
    SetLayeredWindowAttributes(m_hwnd, RGB(0, 0, 0), alpha, LWA_ALPHA);
}

void Window::SetClickThrough(bool enable) {
    m_clickThrough = enable;
    
    LONG exStyle = GetWindowLong(m_hwnd, GWL_EXSTYLE);
    if (enable) {
        SetWindowLong(m_hwnd, GWL_EXSTYLE, exStyle | WS_EX_TRANSPARENT);
    } else {
        SetWindowLong(m_hwnd, GWL_EXSTYLE, exStyle & ~WS_EX_TRANSPARENT);
    }
    
    SetWindowPos(m_hwnd, nullptr, 0, 0, 0, 0,
        SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED);
}

void Window::SetAlwaysOnTop(bool enable) {
    SetWindowPos(m_hwnd, enable ? HWND_TOPMOST : HWND_NOTOPMOST,
        0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE);
}

void Window::SetWindowPos(int x, int y) {
    SetWindowPos(m_hwnd, nullptr, x, y, 0, 0, SWP_NOSIZE | SWP_NOZORDER);
}

void Window::SetWindowSize(int width, int height) {
    m_width = width;
    m_height = height;
    RECT rect = { 0, 0, width, height };
    AdjustWindowRectEx(&rect, WS_OVERLAPPEDWINDOW, FALSE, WS_EX_LAYERED);
    SetWindowPos(m_hwnd, nullptr, 0, 0, 
        rect.right - rect.left, rect.bottom - rect.top,
        SWP_NOMOVE | SWP_NOZORDER);
}

void Window::EnableAcrylicEffect() {
    // Windows 10/11 acrylic effect using DWM
    BOOL enable = TRUE;
    DwmSetWindowAttribute(m_hwnd, DWMWA_USE_HOST_BACKDROP_BRUSH, &enable, sizeof(enable));
    
    // Enable immersive dark mode for the window chrome
    BOOL darkMode = TRUE;
    DwmSetWindowAttribute(m_hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, &darkMode, sizeof(darkMode));
    
    // Prefer rounded corners (Windows 11)
    int cornerPreference = 2;  // DWMWCP_ROUND
    DwmSetWindowAttribute(m_hwnd, DWMWA_WINDOW_CORNER_PREFERENCE, 
        &cornerPreference, sizeof(cornerPreference));
}

void Window::EnableMicaEffect() {
    // Mica effect for Windows 11 - requires undocumented constants
    // DWMWA_MICA_EFFECT = 1029
    #ifndef DWMWA_MICA_EFFECT
    #define DWMWA_MICA_EFFECT 1029
    #endif
    
    BOOL enable = TRUE;
    DwmSetWindowAttribute(m_hwnd, DWMWA_MICA_EFFECT, &enable, sizeof(enable));
}

LRESULT CALLBACK Window::WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam) {
    Window* window = s_instance;
    
    switch (uMsg) {
        case WM_CREATE:
            return 0;
            
        case WM_DESTROY:
            if (window) window->m_shouldClose = true;
            PostQuitMessage(0);
            return 0;
            
        case WM_CLOSE:
            if (window) window->m_shouldClose = true;
            return 0;
            
        case WM_SIZE:
            if (window) {
                window->m_width = LOWORD(lParam);
                window->m_height = HIWORD(lParam);
            }
            return 0;
            
        case WM_MOUSEMOVE: {
            if (window && window->m_mouseMoveCallback) {
                int x = GET_X_LPARAM(lParam);
                int y = GET_Y_LPARAM(lParam);
                window->m_mouseMoveCallback(x, y);
            }
            return 0;
        }
        
        case WM_LBUTTONDOWN:
        case WM_LBUTTONUP: {
            if (window && window->m_mouseClickCallback) {
                int x = GET_X_LPARAM(lParam);
                int y = GET_Y_LPARAM(lParam);
                window->m_mouseClickCallback(x, y, uMsg == WM_LBUTTONDOWN);
            }
            return 0;
        }
        
        case WM_KEYDOWN:
        case WM_KEYUP: {
            if (window && window->m_keyCallback) {
                window->m_keyCallback((int)wParam, uMsg == WM_KEYDOWN);
            }
            return 0;
        }
        
        case WM_ERASEBKGND:
            return 1;  // Prevent background erasing
            
        default:
            return DefWindowProc(hwnd, uMsg, wParam, lParam);
    }
}

void Window::SetMouseMoveCallback(std::function<void(int, int)> callback) {
    m_mouseMoveCallback = callback;
}

void Window::SetMouseClickCallback(std::function<void(int, int, bool)> callback) {
    m_mouseClickCallback = callback;
}

void Window::SetKeyCallback(std::function<void(int, bool)> callback) {
    m_keyCallback = callback;
}