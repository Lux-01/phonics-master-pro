#!/usr/bin/env python3
"""
Universal Memory System - Auto-Tagging Module
Pattern detection and automatic categorization
"""

import re
from typing import List, Dict, Set, Optional
from collections import defaultdict


class AutoTagging:
    """
    Automatic tagging and pattern detection for memories.
    
    Features:
    - Content-based tag extraction
    - Pattern detection
    - Category classification
    - Duplicate detection
    """
    
    def __init__(self):
        # Tag patterns
        self.tag_patterns = {
            # Technologies
            'python': [r'\bpython\b', r'\.py$', r'__init__'],
            'javascript': [r'\bjavascript\b', r'\bjs\b', r'\.js$'],
            'typescript': [r'\btypescript\b', r'\bts\b', r'\.ts$'],
            'flutter': [r'\bflutter\b', r'\bdart\b'],
            'rust': [r'\brust\b', r'\bcargo\b'],
            'go': [r'\bgo\b', r'\bgolang\b'],
            
            # Blockchain/Crypto
            'solana': [r'\bsolana\b', r'\bsol\b', r'\bspl-\w+\b'],
            'ethereum': [r'\beth\b', r'\bethereu\w+', r'\berc20\b'],
            'bitcoin': [r'\bbitcoin\b', r'\bbtc\b'],
            'trading': [r'\btrading\b', r'\btrade\b', r'\bswap\b', r'\buy\b', r'\bsell\b'],
            'defi': [r'\bdefi\b', r'\byield\b', r'\bliquidity\b', r'\bstaking\b'],
            'nft': [r'\bnft\b', r'\bmint\b', r'\bcollection\b'],
            
            # AI/ML
            'ai': [r'\bai\b', r'\bmachine learning\b', r'\bml\b', r'\bmodel\b'],
            'llm': [r'\bllm\b', r'\bgpt\b', r'\bclaude\b', r'\blanguage model'],
            'agent': [r'\bagents?\b', r'\bbot\b', r'\bautomation\b'],
            
            # Tools/Services
            'api': [r'\bapi\b', r'\brest\b', r'\bgraphql\b', r'\bendpoint\b'],
            'database': [r'\bdb\b', r'\bdatabase\b', r'\bsql\b', r'\bpostgres\b', r'\bmongo'],
            'cloud': [r'\baws\b', r'\bgcp\b', r'\bazure\b', r'\bcloud\b', r'\bserverless\b'],
            'docker': [r'\bdocker\b', r'\bcontainer\b', r'\bkubernetes\b', r'\bk8s\b'],
            
            # Concepts
            'research': [r'\bresearch\b', r'\banalysis\b', r'\bstudy\b', r'\binvestigation\b'],
            'decision': [r'\bdecided\b', r'\bdecision\b', r'\bconcluded\b', r'\bchose\b'],
            'project': [r'\bproject\b', r'\bapp\b', r'\bapplication\b', r'\bsystem\b'],
            'bug': [r'\bbug\b', r'\bfix\b', r'\berror\b', r'\bissue\b', r'\bcrash\b'],
            'feature': [r'\bfeature\b', r'\bnew\b', r'\bimplement\b', r'\badd\b'],
            
            # Business
            'revenue': [r'\brevenue\b', r'\bprofit\b', r'\bincome\b', r'\bmonetize\b'],
            'marketing': [r'\bmarketing\b', r'\bseo\b', r'\badvertising\b', r'\bpromotion\b'],
            'product': [r'\bproduct\b', r'\bfeature\b', r'\broadmap\b', r'\blaunch\b'],
        }
        
        # Category rules
        self.category_rules = {
            'research': {
                'keywords': ['research', 'study', 'analyze', 'find', 'search', 'report'],
                'patterns': [r'\bfound\b', r'\bresearch\b', r'\banaly\w+', r'\breport']
            },
            'code': {
                'keywords': ['build', 'create', 'develop', 'code', 'script', 'function'],
                'patterns': [r'\bcode\b', r'\bbuil\w+', r'\bimplement\b', r'\bdevelop']
            },
            'decision': {
                'keywords': ['decided', 'decision', 'choose', 'selected', 'conclude'],
                'patterns': [r'\bdecid\w+', r'\bconclud\w+', r'\bcho[ose]', r'\bselect']
            },
            'api_key': {
                'keywords': ['api key', 'token', 'credential', 'secret', 'password'],
                'patterns': [r'\bapi[_\s]?key', r'\btoken\b', r'\bcredential\w*', r'\bsecret\b']
            },
            'preference': {
                'keywords': ['prefer', 'like', 'want', 'usually', 'always'],
                'patterns': [r'\bprefer\w*', r'\bi like\b', r'\bi want\b', r'\busually\b']
            },
            'project': {
                'keywords': ['project', 'milestone', 'release', 'launch'],
                'patterns': [r'\bproject\b', r'\bmilestone\b', r'\brelease\b', r'\blaunch\b']
            }
        }
    
    def extract_tags(self, content: str, max_tags: int = 5) -> List[str]:
        """
        Extract tags from content based on patterns.
        
        Args:
            content: Text content to analyze
            max_tags: Maximum tags to return
            
        Returns:
            List of tags
        """
        content_lower = content.lower()
        tags = []
        
        for tag, patterns in self.tag_patterns.items():
            for pattern in patterns:
                try:
                    if re.search(pattern, content_lower):
                        tags.append(tag)
                        break
                except:
                    pass
        
        # Remove duplicates and limit
        tags = list(dict.fromkeys(tags))  # Preserve order
        return tags[:max_tags]
    
    def classify_category(self, content: str) -> str:
        """
        Auto-classify content into a category.
        
        Args:
            content: Text to classify
            
        Returns:
            Category name
        """
        content_lower = content.lower()
        scores = {}
        
        for category, rules in self.category_rules.items():
            score = 0
            
            # Keyword matching
            for keyword in rules['keywords']:
                if keyword in content_lower:
                    score += 1
            
            # Pattern matching
            for pattern in rules['patterns']:
                try:
                    if re.search(pattern, content_lower):
                        score += 2
                except:
                    pass
            
            scores[category] = score
        
        # Return highest scoring category
        if scores:
            max_score = max(scores.values())
            if max_score > 0:
                return max(scores, key=scores.get)
        
        return "general"
    
    def calculate_importance(self, content: str, tags: List[str] = None) -> int:
        """
        Calculate importance score (1-10) for content.
        
        Args:
            content: Content to evaluate
            tags: Pre-extracted tags
            
        Returns:
            Importance score (1-10)
        """
        score = 5  # Base score
        content_lower = content.lower()
        
        # Length factor
        if len(content) > 500:
            score += 2
        elif len(content) > 200:
            score += 1
        
        # Category-specific bonuses
        if self.classify_category(content) == 'decision':
            score += 2
        if self.classify_category(content) == 'api_key':
            score += 3
        if self.classify_category(content) == 'research':
            score += 1
        
        # Action keywords
        action_words = ['decided', 'concluded', 'important', 'critical', 'urgent']
        for word in action_words:
            if word in content_lower:
                score += 1
        
        # Exclamation emphasis
        if content.count('!') > 2:
            score += 1
        
        # All caps ratio
        caps_ratio = sum(1 for c in content if c.isupper()) / max(len(content), 1)
        if caps_ratio > 0.3:
            score += 1
        
        return min(score, 10)
    
    def detect_duplicates(self, content: str, existing_memories: List[Dict],
                       threshold: float = 0.8) -> List[Dict]:
        """
        Detect potential duplicates or related memories.
        
        Args:
            content: New content to check
            existing_memories: Existing memory entries
            threshold: Similarity threshold
            
        Returns:
            List of potential duplicates
        """
        duplicates = []
        content_lower = content.lower()
        content_words = set(content_lower.split())
        
        for memory in existing_memories:
            memory_content = memory.get('content', '').lower()
            memory_words = set(memory_content.split())
            
            # Jaccard similarity
            if content_words and memory_words:
                intersection = content_words & memory_words
                union = content_words | memory_words
                similarity = len(intersection) / len(union)
                
                if similarity >= threshold:
                    duplicates.append({
                        'memory': memory,
                        'similarity': similarity
                    })
        
        return duplicates
    
    def suggest_related_topics(self, tags: List[str]) -> List[str]:
        """Suggest related topics based on tags"""
        relationships = {
            'python': ['code', 'script', 'automation'],
            'javascript': ['web', 'frontend', 'nodejs'],
            'solana': ['crypto', 'trading', 'blockchain'],
            'trading': ['finance', 'strategy', 'analysis'],
            'ai': ['ml', 'automation', 'nlp'],
            'api': ['integration', 'backend', 'service'],
            'research': ['decision', 'project', 'learning'],
            'project': ['milestone', 'feature', 'release']
        }
        
        suggestions = []
        for tag in tags:
            if tag in relationships:
                suggestions.extend(relationships[tag])
        
        return list(set(suggestions))[:5]
    
    def auto_tag(self, content: str) -> Dict:
        """
        Comprehensive auto-tagging of content.
        
        Args:
            content: Content to tag
            
        Returns:
            Dict with tags, category, importance, and suggestions
        """
        tags = self.extract_tags(content)
        category = self.classify_category(content)
        importance = self.calculate_importance(content, tags)
        related = self.suggest_related_topics(tags)
        
        return {
            'tags': tags,
            'category': category,
            'importance': importance,
            'suggested_tags': related,
            'is_api_key': category == 'api_key',
            'is_decision': category == 'decision',
            'is_research': category == 'research'
        }


if __name__ == "__main__":
    at = AutoTagging()
    
    # Test cases
    test_content = [
        "I decided to build a Python trading bot for Solana using the Birdeye API",
        "Remember this: My API key for Gemini is abc123xyz789",
        "Research shows that memory systems need multiple layers for effectiveness",
        "Found a bug in the Flutter app - need to fix it"
    ]
    
    print("=" * 60)
    print("🏷️ Auto-Tagging Module Tests")
    print("=" * 60)
    
    for content in test_content:
        result = at.auto_tag(content)
        print(f"\n📝 Content: {content[:60]}...")
        print(f"   Tags: {result['tags']}")
        print(f"   Category: {result['category']}")
        print(f"   Importance: {result['importance']}/10")
        print(f"   Suggested: {result['suggested_tags']}")