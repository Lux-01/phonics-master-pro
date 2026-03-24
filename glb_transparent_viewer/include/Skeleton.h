#pragma once

#include <vector>
#include <string>

class SkeletonController {
public:
    SkeletonController();
    
    void Initialize();
    void Update(float deltaTime);
    
    // Joint manipulation
    void SelectJoint(int index);
    void DeselectJoint();
    int GetSelectedJoint() const { return m_selectedJoint; }
    
    // Pose operations
    void SaveCurrentPose();
    void RestoreSavedPose();
    void ResetToBindPose();
    
    // Interactive manipulation
    void RotateSelectedJoint(float deltaX, float deltaY);
    void TranslateSelectedJoint(float deltaX, float deltaY, float deltaZ);
    void ScaleSelectedJoint(float scale);
    
private:
    int m_selectedJoint = -1;
    struct SavedPose {
        std::vector<float> rotations;
        std::vector<float> positions;
    };
    SavedPose m_savedPose;
};
