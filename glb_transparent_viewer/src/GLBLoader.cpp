#include "GLBLoader.h"
#include "Renderer.h"
#include <iostream>
#include <fstream>
#include <vector>
#include <cstring>

// Minimal glTF structures for loading
namespace tinygltf {
    struct Model {
        std::vector<Mesh> meshes;
        // ... other data
    };
    struct Mesh {
        std::string name;
    };
}

// Stub tinygltf implementation for compilation
// In real version, you'd include the actual tiny_gltf.h library

tinygltf::Model* LoadGLTFStub(const std::string& path) {
    // This is a placeholder - real implementation would use tinygltf
    return new tinygltf::Model();
}

GLBLoader::GLBLoader() {
}

GLBLoader::~GLBLoader() {
}

std::unique_ptr<LoadedModel> GLBLoader::LoadGLB(const std::string& filepath) {
    // Read file
    std::ifstream file(filepath, std::ios::binary | std::ios::ate);
    if (!file.is_open()) {
        return nullptr;
    }

    std::streamsize size = file.tellg();
    file.seekg(0, std::ios::beg);

    std::vector<uint8_t> buffer(size);
    if (!file.read(reinterpret_cast<char*>(buffer.data()), size)) {
        return nullptr;
    }

    return LoadGLBFromMemory(buffer);
}

std::unique_ptr<LoadedModel> GLBLoader::LoadGLBFromMemory(const std::vector<uint8_t>& data) {
    auto model = std::make_unique<LoadedModel>();

    // TODO: Parse actual glTF format
    // For stub, we create a simple demo model

    model->name = "Imported Model";
    model->center = glm::vec3(0.0f);
    model->boundsMin = glm::vec3(-1.0f);
    model->boundsMax = glm::vec3(1.0f);

    // Create a simple mesh placeholder
    Mesh dummyMesh;
    dummyMesh.vao = 0;
    dummyMesh.vbo = 0;
    dummyMesh.ebo = 0;
    dummyMesh.indexCount = 0;
    dummyMesh.transform = glm::mat4(1.0f);
    model->meshes.push_back(dummyMesh);

    // Create a simple skeleton for demonstration
    // Root joint
    Joint root;
    root.name = "Root";
    root.parentIndex = -1;
    root.localTransform = glm::mat4(1.0f);
    root.globalTransform = glm::mat4(1.0f);
    root.inverseBindMatrix = glm::mat4(1.0f);
    model->skeleton.joints.push_back(root);

    // Add some child joints
    for (int i = 0; i < 3; ++i) {
        Joint child;
        child.name = "Joint_" + std::to_string(i + 1);
        child.parentIndex = 0;
        glm::mat4 trans = glm::translate(glm::mat4(1.0f), glm::vec3(i * 0.5f, 1.0f, 0.0f));
        child.localTransform = trans;
        child.globalTransform = trans;
        child.inverseBindMatrix = glm::inverse(trans);

        model->skeleton.joints.front().children.push_back(i + 1);
        model->skeleton.joints.push_back(child);
    }

    BuildJointHierarchy(model->skeleton);

    model->hasAnimations = false;
    model->animationCount = 0;

    return model;
}

void GLBLoader::BuildJointHierarchy(Skeleton& skeleton) {
    // Calculate global transforms
    for (auto& joint : skeleton.joints) {
        if (joint.parentIndex >= 0) {
            auto& parent = skeleton.joints[joint.parentIndex];
            joint.globalTransform = parent.globalTransform * joint.localTransform;
        }
    }

    CalculateJointMatrices(skeleton);
}

void GLBLoader::CalculateJointMatrices(Skeleton& skeleton) {
    skeleton.jointMatrices.clear();
    for (const auto& joint : skeleton.joints) {
        skeleton.jointMatrices.push_back(joint.globalTransform * joint.inverseBindMatrix);
    }
}

void GLBLoader::UpdateSkeletonJoints(LoadedModel& model) {
    BuildJointHierarchy(model.skeleton);
}

void GLBLoader::RotateJoint(LoadedModel& model, int jointIndex, float angleX, float angleY, float angleZ) {
    if (jointIndex < 0 || jointIndex >= (int)model.skeleton.joints.size()) return;

    auto& joint = model.skeleton.joints[jointIndex];

    glm::mat4 rotX = glm::rotate(glm::mat4(1.0f), glm::radians(angleX), glm::vec3(1, 0, 0));
    glm::mat4 rotY = glm::rotate(glm::mat4(1.0f), glm::radians(angleY), glm::vec3(0, 1, 0));
    glm::mat4 rotZ = glm::rotate(glm::mat4(1.0f), glm::radians(angleZ), glm::vec3(0, 0, 1));

    joint.localTransform = joint.localTransform * rotX * rotY * rotZ;

    UpdateSkeletonJoints(model);
}

void GLBLoader::MoveJoint(LoadedModel& model, int jointIndex, float x, float y, float z) {
    if (jointIndex < 0 || jointIndex >= (int)model.skeleton.joints.size()) return;

    auto& joint = model.skeleton.joints[jointIndex];
    joint.localTransform = glm::translate(joint.localTransform, glm::vec3(x, y, z));

    UpdateSkeletonJoints(model);
}

void GLBLoader::ResetSkeleton(LoadedModel& model) {
    for (size_t i = 0; i < model.skeleton.joints.size(); ++i) {
        if (i == 0) {
            model.skeleton.joints[i].localTransform = glm::mat4(1.0f);
        } else {
            glm::mat4 identity(1.0f);
            model.skeleton.joints[i].localTransform = identity;
        }
    }
    UpdateSkeletonJoints(model);
}

void GLBLoader::UpdateAnimation(LoadedModel& model, float deltaTime) {
    if (!model.hasAnimations || model.currentAnimation < 0) return;

    model.animationTime += deltaTime;
    // TODO: Interpolate joint poses based on animation data
}

void GLBLoader::SetAnimation(LoadedModel& model, int index) {
    if (index >= 0 && index < model.animationCount) {
        model.currentAnimation = index;
        model.animationTime = 0.0f;
    }
}

void GLBLoader::PlayAnimation(LoadedModel& model, bool loop) {
    // TODO: Setup animation playback
}

void GLBLoader::StopAnimation(LoadedModel& model) {
    model.currentAnimation = -1;
}

int GLBLoader::GetJointCount(const LoadedModel& model) const {
    return (int)model.skeleton.joints.size();
}

std::string GLBLoader::GetJointName(const LoadedModel& model, int index) const {
    if (index >= 0 && index < (int)model.skeleton.joints.size()) {
        return model.skeleton.joints[index].name;
    }
    return "";
}

glm::mat4 GLBLoader::GetJointTransform(const LoadedModel& model, int index) const {
    if (index >= 0 && index < (int)model.skeleton.joints.size()) {
        return model.skeleton.joints[index].globalTransform;
    }
    return glm::mat4(1.0f);
}

int GLBLoader::GetJointParent(const LoadedModel& model, int index) const {
    if (index >= 0 && index < (int)model.skeleton.joints.size()) {
        return model.skeleton.joints[index].parentIndex;
    }
    return -1;
}

std::vector<int> GLBLoader::GetJointChildren(const LoadedModel& model, int index) const {
    if (index >= 0 && index < (int)model.skeleton.joints.size()) {
        return model.skeleton.joints[index].children;
    }
    return {};
}

bool GLBLoader::ExtractMeshData(const tinygltf::Model& model, const tinygltf::Mesh& mesh,
                                std::vector<float>& vertices, std::vector<unsigned int>& indices) {
    // TODO: Extract actual mesh data
    return false;
}

void GLBLoader::ExtractSkeleton(const tinygltf::Model& model, LoadedModel& loaded) {
    // TODO: Extract skeleton from glTF skin data
}

void GLBLoader::ExtractAnimations(const tinygltf::Model& model, LoadedModel& loaded) {
    // TODO: Extract animations
}

GLuint GLBLoader::CreateVAO(const std::vector<float>& vertices,
                              const std::vector<unsigned int>& indices) {
    GLuint vao, vbo, ebo;

    glGenVertexArrays(1, &vao);
    glGenBuffers(1, &vbo);
    glGenBuffers(1, &ebo);

    glBindVertexArray(vao);

    glBindBuffer(GL_ARRAY_BUFFER, vbo);
    glBufferData(GL_ARRAY_BUFFER, vertices.size() * sizeof(float), vertices.data(), GL_STATIC_DRAW);

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.size() * sizeof(unsigned int), indices.data(), GL_STATIC_DRAW);

    // Position attribute
    glEnableVertexAttribArray(0);
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(float), (void*)0);

    // Normal attribute
    glEnableVertexAttribArray(1);
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(float), (void*)(3 * sizeof(float)));

    // TexCoord attribute
    glEnableVertexAttribArray(2);
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * sizeof(float), (void*)(6 * sizeof(float)));

    glBindVertexArray(0);

    return vao;
}
