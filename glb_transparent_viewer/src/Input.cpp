#include "Input.h"
#include <cstring>

Input::Input()
    : m_mouseX(0), m_mouseY(0)
    , m_prevMouseX(0), m_prevMouseY(0)
    , m_mouseWheelDelta(0) {
    std::memset(m_keys, 0, sizeof(m_keys));
    std::memset(m_prevKeys, 0, sizeof(m_prevKeys));
    std::memset(m_mouseButtons, 0, sizeof(m_mouseButtons));
    std::memset(m_prevMouseButtons, 0, sizeof(m_prevMouseButtons));
}

Input::~Input()
{
}

void Input::Update() {
    // Save previous state
    std::memcpy(m_prevKeys, m_keys, sizeof(m_keys));
    std::memcpy(m_prevMouseButtons, m_mouseButtons, sizeof(m_mouseButtons));

    m_prevMouseX = m_mouseX;
    m_prevMouseY = m_mouseY;
    m_mouseWheelDelta = 0;

    // Get current keyboard state
    GetKeyboardState(m_keys);

    // Mouse buttons are handled in ProcessMessage
}

bool Input::IsMouseButtonDown(MouseButton button) const {
    int index = static_cast<int>(button);
    if (index < 0 || index >= 3) return false;
    return m_mouseButtons[index];
}

bool Input::IsMouseButtonPressed(MouseButton button) const {
    int index = static_cast<int>(button);
    if (index < 0 || index >= 3) return false;
    return m_mouseButtons[index] && !m_prevMouseButtons[index];
}

bool Input::IsMouseButtonReleased(MouseButton button) const {
    int index = static_cast<int>(button);
    if (index < 0 || index >= 3) return false;
    return !m_mouseButtons[index] && m_prevMouseButtons[index];
}

void Input::GetMousePosition(int& x, int& y) const {
    x = m_mouseX;
    y = m_mouseY;
}

void Input::GetMouseDelta(int& dx, int& dy) const {
    dx = m_mouseX - m_prevMouseX;
    dy = m_mouseY - m_prevMouseY;
}

int Input::GetMouseWheelDelta() const {
    return m_mouseWheelDelta;
}

bool Input::IsKeyDown(int vkCode) const {
    return (m_keys[vkCode] & 0x80) != 0;
}

bool Input::IsKeyPressed(int vkCode) const {
    return (m_keys[vkCode] & 0x80) && !(m_prevKeys[vkCode] & 0x80);
}

bool Input::IsKeyReleased(int vkCode) const {
    return !(m_keys[vkCode] & 0x80) && (m_prevKeys[vkCode] & 0x80);
}

void Input::SetMouseMoveCallback(std::function<void(int, int)> callback) {
    m_mouseMoveCallback = callback;
}

void Input::SetMouseButtonCallback(std::function<void(MouseButton, bool)> callback) {
    m_mouseButtonCallback = callback;
}

void Input::SetKeyCallback(std::function<void(int, bool)> callback) {
    m_keyCallback = callback;
}

void Input::SetMouseWheelCallback(std::function<void(int)> callback) {
    m_mouseWheelCallback = callback;
}

void Input::ProcessMessage(UINT msg, WPARAM wParam, LPARAM lParam) {
    switch (msg) {
        case WM_MOUSEMOVE: {
            int x = LOWORD(lParam);
            int y = HIWORD(lParam);
            m_mouseX = x;
            m_mouseY = y;
            if (m_mouseMoveCallback) {
                m_mouseMoveCallback(x, y);
            }
            break;
        }

        case WM_LBUTTONDOWN:
            m_mouseButtons[static_cast<int>(MouseButton::Left)] = true;
            if (m_mouseButtonCallback) {
                m_mouseButtonCallback(MouseButton::Left, true);
            }
            break;

        case WM_LBUTTONUP:
            m_mouseButtons[static_cast<int>(MouseButton::Left)] = false;
            if (m_mouseButtonCallback) {
                m_mouseButtonCallback(MouseButton::Left, false);
            }
            break;

        case WM_RBUTTONDOWN:
            m_mouseButtons[static_cast<int>(MouseButton::Right)] = true;
            if (m_mouseButtonCallback) {
                m_mouseButtonCallback(MouseButton::Right, true);
            }
            break;

        case WM_RBUTTONUP:
            m_mouseButtons[static_cast<int>(MouseButton::Right)] = false;
            if (m_mouseButtonCallback) {
                m_mouseButtonCallback(MouseButton::Right, false);
            }
            break;

        case WM_MBUTTONDOWN:
            m_mouseButtons[static_cast<int>(MouseButton::Middle)] = true;
            if (m_mouseButtonCallback) {
                m_mouseButtonCallback(MouseButton::Middle, true);
            }
            break;

        case WM_MBUTTONUP:
            m_mouseButtons[static_cast<int>(MouseButton::Middle)] = false;
            if (m_mouseButtonCallback) {
                m_mouseButtonCallback(MouseButton::Middle, false);
            }
            break;

        case WM_MOUSEWHEEL: {
            m_mouseWheelDelta = GET_WHEEL_DELTA_WPARAM(wParam) / WHEEL_DELTA;
            if (m_mouseWheelCallback) {
                m_mouseWheelCallback(m_mouseWheelDelta);
            }
            break;
        }

        case WM_KEYDOWN: {
            m_keys[wParam] = 0x80;
            if (m_keyCallback) {
                m_keyCallback(static_cast<int>(wParam), true);
            }
            break;
        }

        case WM_KEYUP: {
            m_keys[wParam] = 0;
            if (m_keyCallback) {
                m_keyCallback(static_cast<int>(wParam), false);
            }
            break;
        }
    }
}
