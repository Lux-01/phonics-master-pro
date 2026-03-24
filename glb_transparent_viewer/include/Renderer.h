#pragma once

#include <gl/GL.h>
#include <gl/GLU.h>
#include <vector>
#include <memory>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>

struct Mesh {
    GLuint vao, vbo, ebo;
    int indexCount;
    glm::mat4 transform;
};

struct Joint {
    std::string name;
    glm::mat4 inverseBindMatrix;
    glm::mat4 localTransform;
    glm::mat4 globalTransform;
    int parentIndex;
    std::vector<int> children;
};

struct Skeleton {
    std::vector<Joint> joints;
    std::vector<glm::mat4> jointMatrices;
    bool hasAnimation = false;
};

class Renderer {
public:
    Renderer();
    ~Renderer();
    
    bool Initialize(int width, int height);
    void Shutdown();
    
    void SetViewport(int width, int height);
    void Clear(float r, float g, float b, float a);
    void ClearTransparent();
    
    // Camera
    void SetCamera(float posX, float posY, float posZ, 
                   float targetX, float targetY, float targetZ);
    void RotateCamera(float deltaX, float deltaY);
    void ZoomCamera(float delta);
    
    // Rendering
    void BeginFrame();
    void EndFrame();
    
    void DrawMesh(const Mesh& mesh);
    void DrawSkeleton(const Skeleton& skeleton);
    void DrawJoint(const glm::mat4& transform, float size);
    void DrawBone(const glm::vec3& start, const glm::vec3& end);
    
    // Post-processing for transparency
    void EnableTransparency();
    void DisableTransparency();
    
    // Shader management
    bool LoadShaders();
    void UseShader(GLuint program);
    
private:
    void SetupMatrices();
    
    GLuint m_shaderProgram;
    GLuint m_skeletonShader;
    
    glm::mat4 m_projection;
    glm::mat4 m_view;
    glm::mat4 m_model;
    
    // Camera state
    glm::vec3 m_cameraPos;
    glm::vec3 m_cameraTarget;
    float m_cameraDistance;
    float m_cameraYaw;
    float m_cameraPitch;
    
    int m_width, m_height;
    bool m_initialized;
};
