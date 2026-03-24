#pragma once

#include <windows.h>
#include <functional>

enum class MouseButton {
    Left,
    Right,
    Middle
};

class Input {
public:
    Input();
    ~Input();

    // Update internal state - call each frame
    void Update();

    // Mouse state
    bool IsMouseButtonDown(MouseButton button) const;
    bool IsMouseButtonPressed(MouseButton button) const;
    bool IsMouseButtonReleased(MouseButton button) const;
    void GetMousePosition(int& x, int& y) const;
    void GetMouseDelta(int& dx, int& dy) const;
    int GetMouseWheelDelta() const;

    // Keyboard state
    bool IsKeyDown(int vkCode) const;
    bool IsKeyPressed(int vkCode) const;
    bool IsKeyReleased(int vkCode) const;

    // Set callbacks
    void SetMouseMoveCallback(std::function<void(int, int)> callback);
    void SetMouseButtonCallback(std::function<void(MouseButton, bool)> callback);
    void SetKeyCallback(std::function<void(int, bool)> callback);
    void SetMouseWheelCallback(std::function<void(int)> callback);

    // Process raw Windows messages
    void ProcessMessage(UINT msg, WPARAM wParam, LPARAM lParam);

private:
    // Current state
    bool m_mouseButtons[3] = { false, false, false };
    bool m_prevMouseButtons[3] = { false, false, false };
    int m_mouseX, m_mouseY;
    int m_prevMouseX, m_prevMouseY;
    int m_mouseWheelDelta;

    BYTE m_keys[256];
    BYTE m_prevKeys[256];

    // Callbacks
    std::function<void(int, int)> m_mouseMoveCallback;
    std::function<void(MouseButton, bool)> m_mouseButtonCallback;
    std::function<void(int, bool)> m_keyCallback;
    std::function<void(int)> m_mouseWheelCallback;
};
