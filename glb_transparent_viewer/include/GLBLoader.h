#pragma once

#include <string>
#include <vector>
#include <memory>
#include <glm/glm.hpp>
#include "Renderer.h"

// Forward declarations for tinygltf
namespace tinygltf {
    class Model;
    struct Mesh;
    struct Node;
    struct Skin;
    struct Animation;
}

struct LoadedModel {
    std::vector<Mesh> meshes;
    Skeleton skeleton;
    std::string name;
    
    // Animation data
    bool hasAnimations = false;
    int animationCount = 0;
    int currentAnimation = -1;
    float animationTime = 0.0f;
    
    // Model bounds
    glm::vec3 boundsMin;
    glm::vec3 boundsMax;
    glm::vec3 center;
};

class GLBLoader {
public:
    GLBLoader();
    ~GLBLoader();
    
    // Load .glb file
    std::unique_ptr<LoadedModel> LoadGLB(const std::string& filepath);
    std::unique_ptr<LoadedModel> LoadGLBFromMemory(const std::vector<uint8_t>& data);
    
    // Skeleton interaction
    void UpdateSkeletonJoints(LoadedModel& model);
    void RotateJoint(LoadedModel& model, int jointIndex, float angleX, float angleY, float angleZ);
    void MoveJoint(LoadedModel& model, int jointIndex, float x, float y, float z);
    void ResetSkeleton(LoadedModel& model);
    
    // Animation
    void UpdateAnimation(LoadedModel& model, float deltaTime);
    void SetAnimation(LoadedModel& model, int index);
    void PlayAnimation(LoadedModel& model, bool loop = true);
    void StopAnimation(LoadedModel& model);
    
    // Get joint info
    int GetJointCount(const LoadedModel& model) const;
    std::string GetJointName(const LoadedModel& model, int index) const;
    glm::mat4 GetJointTransform(const LoadedModel& model, int index) const;
    int GetJointParent(const LoadedModel& model, int index) const;
    std::vector<int> GetJointChildren(const LoadedModel& model, int index) const;

private:
    bool ExtractMeshData(const tinygltf::Model& model, const tinygltf::Mesh& mesh, 
                         std::vector<float>& vertices, std::vector<unsigned int>& indices);
    void ExtractSkeleton(const tinygltf::Model& model, LoadedModel& loaded);
    void ExtractAnimations(const tinygltf::Model& model, LoadedModel& loaded);
    void BuildJointHierarchy(Skeleton& skeleton);
    void CalculateJointMatrices(Skeleton& skeleton);
    
    GLuint CreateVAO(const std::vector<float>& vertices, 
                     const std::vector<unsigned int>& indices);
};
