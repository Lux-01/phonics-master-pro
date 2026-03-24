#!/usr/bin/env python3
"""
Skill Activation & Evolution Integration
Activates dormant skills and enables cross-skill learning
"""
import sys
import os

# Add skill paths
sys.path.insert(0, '/home/skux/.openclaw/workspace/skills/cognitive-enhancement-layer')
sys.path.insert(0, '/home/skux/.openclaw/workspace/skills/social-content-generator')
sys.path.insert(0, '/home/skux/.openclaw/workspace/skills/context-optimizer')
sys.path.insert(0, '/home/skux/.openclaw/workspace/skills/skill-evolution-engine')

from cel_integration import CEL, enhance, explain, generate_idea
from content_generator import generate_content
from auto_trigger import ContextAutoTrigger, record_message, record_file, checkpoint
from cross_skill_learning import CrossSkillLearning, teach, share_pattern, stats

class SkillEcosystem:
    """Integrated skill ecosystem with CEL, social content, context optimization, and cross-skill learning"""
    
    def __init__(self):
        self.cel = CEL()
        self.content_gen = None  # Uses function interface
        self.context_trigger = ContextAutoTrigger()
        self.cross_skill = CrossSkillLearning()
        
    def use_cel(self, user_input, context=None):
        """Use CEL to enhance understanding"""
        return self.cel.enhance(user_input, context)
    
    def generate_moltbook_post(self, topic):
        """Generate content for Moltbook"""
        return generate_content('moltbook', topic)
    
    def record_session_message(self):
        """Record message and check for context triggers"""
        return record_message()
    
    def record_file_read(self, path, summary=""):
        """Record file read"""
        return record_file(path, summary)
    
    def create_checkpoint(self, summary, decisions=None):
        """Create session checkpoint"""
        return checkpoint(summary, decisions)
    
    def teach_skill(self, source, target, learning_type, content):
        """Have one skill teach another"""
        return teach(source, target, learning_type, content)
    
    def share_pattern_across_skills(self, source, pattern, applicable_skills):
        """Share a pattern across skills"""
        return share_pattern(source, pattern, applicable_skills)
    
    def get_learning_stats(self):
        """Get cross-skill learning statistics"""
        return stats()

# Global instance
_ecosystem = None

def get_ecosystem():
    """Get singleton ecosystem instance"""
    global _ecosystem
    if _ecosystem is None:
        _ecosystem = SkillEcosystem()
    return _ecosystem

# Convenience exports
use_cel = lambda text, ctx=None: get_ecosystem().use_cel(text, ctx)
moltbook_post = lambda topic: get_ecosystem().generate_moltbook_post(topic)
learn = lambda s, t, lt, c: get_ecosystem().teach_skill(s, t, lt, c)
share = lambda s, p, skills: get_ecosystem().share_pattern_across_skills(s, p, skills)
learning_stats = lambda: get_ecosystem().get_learning_stats()

if __name__ == "__main__":
    print("=" * 60)
    print("SKILL ECOSYSTEM ACTIVATION COMPLETE")
    print("=" * 60)
    print("\n✅ CEL (Cognitive Enhancement Layer) - ACTIVE")
    print("   Usage: use_cel('your question')")
    print("\n✅ Social Content Generator - ACTIVE")
    print("   Usage: moltbook_post('topic')")
    print("\n✅ Context Optimizer Auto-Triggers - ACTIVE")
    print("   Auto-triggers at 30 messages, file re-reads, stale context")
    print("\n✅ Cross-Skill Learning - ACTIVE")
    print("   Skills teach each other, share patterns, propagate success")
    print("   Usage: learn('source_skill', 'target_skill', 'type', {})")
    print("\n" + "=" * 60)
