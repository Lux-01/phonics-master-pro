#include "Renderer.h"
#include <cmath>

Renderer::Renderer()
    : m_shaderProgram(0), m_skeletonShader(0)
    , m_cameraDistance(5.0f), m_cameraYaw(0.0f), m_cameraPitch(30.0f)
    , m_width(1024), m_height(768), m_initialized(false) {
}

Renderer::~Renderer() {
    Shutdown();
}

bool Renderer::Initialize(int width, int height) {
    m_width = width;
    m_height = height;

    // Enable OpenGL features
    glEnable(GL_DEPTH_TEST);
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

    // Enable alpha channel output for transparency
    glEnable(GL_ALPHA_TEST);
    glAlphaFunc(GL_GREATER, 0.0f);

    // Set viewport
    SetViewport(width, height);

    // Load default shaders
    if (!LoadShaders()) {
        return false;
    }

    m_initialized = true;
    return true;
}

void Renderer::Shutdown() {
    // Cleanup would go here
    m_initialized = false;
}

void Renderer::SetViewport(int width, int height) {
    m_width = width;
    m_height = height;
    glViewport(0, 0, width, height);
    SetupMatrices();
}

void Renderer::SetupMatrices() {
    // Setup projection matrix
    float aspect = (float)m_width / (float)m_height;
    m_projection = glm::perspective(glm::radians(45.0f), aspect, 0.1f, 1000.0f);

    // Update view matrix based on camera
    float yawRad = glm::radians(m_cameraYaw);
    float pitchRad = glm::radians(m_cameraPitch);

    m_cameraPos.x = m_cameraTarget.x + m_cameraDistance * cosf(pitchRad) * sinf(yawRad);
    m_cameraPos.y = m_cameraTarget.y + m_cameraDistance * sinf(pitchRad);
    m_cameraPos.z = m_cameraTarget.z + m_cameraDistance * cosf(pitchRad) * cosf(yawRad);

    m_view = glm::lookAt(m_cameraPos, m_cameraTarget, glm::vec3(0, 1, 0));
}

void Renderer::SetCamera(float posX, float posY, float posZ, float targetX, float targetY, float targetZ) {
    m_cameraPos = glm::vec3(posX, posY, posZ);
    m_cameraTarget = glm::vec3(targetX, targetY, targetZ);

    // Calculate distance
    glm::vec3 diff = m_cameraPos - m_cameraTarget;
    m_cameraDistance = glm::length(diff);

    // Calculate angles
    m_cameraYaw = glm::degrees(atan2f(diff.x, diff.z));
    m_cameraPitch = glm::degrees(asinf(diff.y / m_cameraDistance));

    SetupMatrices();
}

void Renderer::RotateCamera(float deltaX, float deltaY) {
    m_cameraYaw += deltaX;
    m_cameraPitch -= deltaY;

    // Clamp pitch to prevent flipping
    if (m_cameraPitch > 89.0f) m_cameraPitch = 89.0f;
    if (m_cameraPitch < -89.0f) m_cameraPitch = -89.0f;

    SetupMatrices();
}

void Renderer::ZoomCamera(float delta) {
    m_cameraDistance -= delta;
    if (m_cameraDistance < 0.1f) m_cameraDistance = 0.1f;
    if (m_cameraDistance > 1000.0f) m_cameraDistance = 1000.0f;
    SetupMatrices();
}

void Renderer::Clear(float r, float g, float b, float a) {
    glClearColor(r, g, b, a);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
}

void Renderer::ClearTransparent() {
    // Additional setup for transparent rendering
    glClearColor(0.0f, 0.0f, 0.0f, 0.0f);
    glClear(GL_COLOR_BUFFER_BIT);
}

void Renderer::BeginFrame() {
    // Reset to default shader
    UseShader(m_shaderProgram);

    // Set up matrices in shader (simplified - would use uniform blocks in real implementation)
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    float aspect = (float)m_width / (float)m_height;
    gluPerspective(45.0, aspect, 0.1, 1000.0);

    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();
    gluLookAt(m_cameraPos.x, m_cameraPos.y, m_cameraPos.z,
              m_cameraTarget.x, m_cameraTarget.y, m_cameraTarget.z,
              0, 1, 0);
}

void Renderer::EndFrame() {
    // Cleanup per-frame state
}

void Renderer::DrawMesh(const Mesh& mesh) {
    glPushMatrix();
    glMultMatrixf(glm::value_ptr(mesh.transform));

    // Use immediate mode drawing for version 1 (would use VBOs in production)
    glBegin(GL_TRIANGLES);
    // Simplified - real implementation would use vertex arrays
    glColor4f(0.7f, 0.7f, 0.7f, 0.9f);
    glVertex3f(0, 0, 0);
    glVertex3f(1, 0, 0);
    glVertex3f(0, 1, 0);
    glEnd();

    glPopMatrix();
}

void Renderer::DrawSkeleton(const Skeleton& skeleton) {
    glDisable(GL_DEPTH_TEST);
    glLineWidth(2.0f);

    for (size_t i = 0; i < skeleton.joints.size(); ++i) {
        const auto& joint = skeleton.joints[i];

        // Draw joint as small cube
        DrawJoint(joint.globalTransform, 0.05f);

        // Draw bone to parent
        if (joint.parentIndex >= 0) {
            const auto& parent = skeleton.joints[joint.parentIndex];
            glm::vec3 start(parent.globalTransform[3]);
            glm::vec3 end(joint.globalTransform[3]);
            DrawBone(start, end);
        }
    }

    glEnable(GL_DEPTH_TEST);
}

void Renderer::DrawJoint(const glm::mat4& transform, float size) {
    glm::vec3 pos(transform[3]);

    glPushMatrix();
    glTranslatef(pos.x, pos.y, pos.z);
    glScalef(size, size, size);

    glColor4f(0.0f, 1.0f, 0.0f, 0.8f);

    // Draw cube
    glBegin(GL_QUADS);
    // Front face
    glVertex3f(-1, -1, 1); glVertex3f(1, -1, 1);
    glVertex3f(1, 1, 1); glVertex3f(-1, 1, 1);
    // Back face
    glVertex3f(-1, -1, -1); glVertex3f(-1, 1, -1);
    glVertex3f(1, 1, -1); glVertex3f(1, -1, -1);
    glEnd();

    glPopMatrix();
}

void Renderer::DrawBone(const glm::vec3& start, const glm::vec3& end) {
    glBegin(GL_LINES);
    glColor4f(0.0f, 0.8f, 1.0f, 0.7f);
    glVertex3f(start.x, start.y, start.z);
    glVertex3f(end.x, end.y, end.z);
    glEnd();
}

bool Renderer::LoadShaders() {
    // Simplified for version 1 - using fixed function pipeline
    // Real implementation would load GLSL shaders
    m_shaderProgram = 1; // Placeholder
    return true;
}

void Renderer::UseShader(GLuint program) {
    if (program > 0) {
        // Would call glUseProgram(program) in real implementation
    }
}

void Renderer::EnableTransparency() {
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
}

void Renderer::DisableTransparency() {
    glDisable(GL_BLEND);
}
