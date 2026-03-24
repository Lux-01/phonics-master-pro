#!/usr/bin/env python3
"""
CEL-Creativity: Novel Concept Generation + Cross-Domain Analogy
Addresses: "No creativity - I combine existing patterns, don't invent"

ACA Implementation - Phase 3: Creativity Module
"""

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import sys

sys.path.insert(0, '/home/skux/.openclaw/workspace')


class CELCreativity:
    """
    Provides creative capabilities through:
    - Novel concept generation (combining ideas in new ways)
    - Cross-domain analogy (applying patterns from other fields)
    - "What if" scenario generation
    - Divergent thinking (exploring many possibilities)
    - Value assessment (filtering good ideas from bad)
    """
    
    def __init__(self):
        self.concept_space = self._load_concept_space()
        self.analogy_mappings = self._load_analogy_mappings()
        self.novelty_threshold = 0.7  # Minimum novelty score
        
    def _load_concept_space(self) -> Dict:
        """Load the space of combinable concepts."""
        return {
            'trading': {
                'concepts': ['mean reversion', 'momentum', 'arbitrage', 'scalping', 'swing trading'],
                'mechanisms': ['technical indicators', 'price action', 'volume analysis', 'sentiment'],
                'tools': ['stop loss', 'take profit', 'position sizing', 'risk management']
            },
            'ai': {
                'concepts': ['neural networks', 'reinforcement learning', 'pattern recognition', 'prediction'],
                'mechanisms': ['training', 'inference', 'feedback loops', 'optimization'],
                'tools': ['classification', 'regression', 'clustering', 'generation']
            },
            'biology': {
                'concepts': ['evolution', 'adaptation', 'natural selection', 'ecosystems'],
                'mechanisms': ['mutation', 'selection', 'inheritance', 'competition'],
                'tools': ['genetic algorithms', 'swarm intelligence', 'neural evolution']
            },
            'physics': {
                'concepts': ['momentum', 'inertia', 'resonance', 'entropy'],
                'mechanisms': ['feedback', 'oscillation', 'equilibrium', 'phase transitions'],
                'tools': ['damping', 'amplification', 'filtering', 'modulation']
            }
        }
    
    def _load_analogy_mappings(self) -> Dict:
        """Load cross-domain analogy mappings."""
        return {
            'trading': {
                'biology': {
                    'mean reversion': 'homeostasis (returning to balance)',
                    'momentum': 'inertia (continuing in direction)',
                    'market cycles': 'seasonal adaptation',
                    'diversification': 'ecosystem diversity'
                },
                'physics': {
                    'momentum': 'momentum (mass × velocity)',
                    'support/resistance': 'energy barriers',
                    'volatility': 'entropy (disorder)',
                    'trend': 'inertia (resistance to change)'
                },
                'ai': {
                    'pattern recognition': 'pattern recognition (neural networks)',
                    'prediction': 'inference (model prediction)',
                    'backtesting': 'training/validation',
                    'optimization': 'gradient descent'
                }
            }
        }
    
    def process(self, user_input: str, context: Dict = None,
                analysis: Dict = None) -> str:
        """
        Main processing entry point.
        
        Returns creative insights and novel ideas.
        """
        # Determine what type of creativity is needed
        if self._is_create_request(user_input):
            return self._generate_novel_idea(user_input, context)
        
        elif self._is_analogy_request(user_input):
            return self._generate_analogy(user_input, context)
        
        elif self._is_what_if_request(user_input):
            return self._generate_scenario(user_input, context)
        
        else:
            # General creative enhancement
            return self._enhance_creatively(user_input, context)
    
    def _is_create_request(self, text: str) -> bool:
        """Detect if user wants something created."""
        create_patterns = [
            r'create\s+(a|an|new)',
            r'design\s+(a|an)',
            r'invent\s+(a|an)',
            r'come\s+up\s+with',
            r'generate\s+(a|an)',
            r'build\s+(a|an)',
            r'develop\s+(a|an)'
        ]
        text_lower = text.lower()
        return any(self._match_pattern(p, text_lower) for p in create_patterns)
    
    def _is_analogy_request(self, text: str) -> bool:
        """Detect if user wants an analogy."""
        analogy_patterns = [
            r'like\s+what',
            r'analogy',
            r'similar\s+to',
            r'compare\s+to',
            r'metaphor',
            r'what\s+is\s+this\s+like'
        ]
        text_lower = text.lower()
        return any(self._match_pattern(p, text_lower) for p in analogy_patterns)
    
    def _is_what_if_request(self, text: str) -> bool:
        """Detect if user wants scenario exploration."""
        what_if_patterns = [
            r'what\s+if',
            r'imagine\s+if',
            r'suppose',
            r'how\s+would',
            r'what\s+would\s+happen',
            r'scenario'
        ]
        text_lower = text.lower()
        return any(self._match_pattern(p, text_lower) for p in what_if_patterns)
    
    def _match_pattern(self, pattern: str, text: str) -> bool:
        """Match pattern in text."""
        import re
        return bool(re.search(pattern, text))
    
    def _generate_novel_idea(self, request: str, context: Dict) -> str:
        """Generate a novel idea by combining concepts."""
        # Extract domain from request
        domain = self._extract_domain(request)
        
        # Generate multiple combinations
        ideas = []
        for _ in range(5):  # Generate 5 candidates
            idea = self._combine_concepts(domain)
            if idea:
                ideas.append(idea)
        
        # Score and filter for novelty
        scored_ideas = [(idea, self._score_novelty(idea)) for idea in ideas]
        scored_ideas.sort(key=lambda x: x[1], reverse=True)
        
        # Return top idea above threshold
        for idea, score in scored_ideas:
            if score >= self.novelty_threshold:
                return f"**Novel Idea (novelty: {score:.0%}):**\n\n{idea}\n\nThis combines elements from {self._describe_combination(idea)}"
        
        # Fallback to best available
        if scored_ideas:
            idea, score = scored_ideas[0]
            return f"**Idea (novelty: {score:.0%}):**\n\n{idea}"
        
        return "I'm working on generating a creative solution for this..."
    
    def _generate_analogy(self, request: str, context: Dict) -> str:
        """Generate cross-domain analogy."""
        subject = self._extract_subject(request)
        source_domain = self._extract_domain(request)
        
        # Find analogies in other domains
        analogies = []
        for target_domain, mappings in self.analogy_mappings.get(source_domain, {}).items():
            for concept, analogy in mappings.items():
                if concept in subject.lower() or subject.lower() in concept:
                    analogies.append((target_domain, analogy))
        
        if analogies:
            domain, analogy = analogies[0]
            return f"**Analogy:** {subject} is like {analogy} in {domain}.\n\nThis works because both involve similar underlying principles of feedback and adaptation."
        
        # Generate novel analogy
        return self._create_novel_analogy(subject, source_domain)
    
    def _generate_scenario(self, request: str, context: Dict) -> str:
        """Generate 'what if' scenarios."""
        # Extract the condition
        condition = self._extract_condition(request)
        
        # Generate multiple scenarios
        scenarios = []
        
        # Best case
        scenarios.append({
            'name': 'Optimistic',
            'description': self._generate_best_case(condition),
            'probability': '20%'
        })
        
        # Most likely
        scenarios.append({
            'name': 'Realistic',
            'description': self._generate_likely_case(condition),
            'probability': '60%'
        })
        
        # Worst case
        scenarios.append({
            'name': 'Pessimistic',
            'description': self._generate_worst_case(condition),
            'probability': '20%'
        })
        
        # Format response
        result = f"**What if {condition}?**\n\n"
        for scenario in scenarios:
            result += f"\n**{scenario['name']}** ({scenario['probability']} probability):\n{scenario['description']}"
        
        return result
    
    def _enhance_creatively(self, text: str, context: Dict) -> str:
        """Add creative perspective to existing content."""
        # Generate alternative perspectives
        perspectives = self._generate_perspectives(text)
        
        if perspectives:
            return text + "\n\n**Alternative Perspectives:**\n" + "\n".join(f"• {p}" for p in perspectives[:3])
        
        return text
    
    def _combine_concepts(self, domain: str) -> Optional[str]:
        """Combine concepts from different domains."""
        # Get concepts from primary domain
        primary = self.concept_space.get(domain, {})
        
        # Get concepts from random other domain
        other_domains = [d for d in self.concept_space.keys() if d != domain]
        if not other_domains:
            return None
        
        secondary_domain = random.choice(other_domains)
        secondary = self.concept_space.get(secondary_domain, {})
        
        # Combine elements
        if primary.get('concepts') and secondary.get('mechanisms'):
            concept = random.choice(primary['concepts'])
            mechanism = random.choice(secondary['mechanisms'])
            tool = random.choice(primary.get('tools', ['system']))
            
            return f"A {tool} that applies {mechanism} from {secondary_domain} to {concept} in {domain}"
        
        return None
    
    def _score_novelty(self, idea: str) -> float:
        """Score how novel an idea is (0-1)."""
        # Check against known patterns
        # Higher score = more novel
        
        score = 0.5  # Base score
        
        # Bonus for cross-domain
        domains_mentioned = sum(1 for d in self.concept_space.keys() if d in idea.lower())
        score += 0.1 * domains_mentioned
        
        # Bonus for unexpected combinations
        unexpected_words = ['biological', 'physics', 'evolution', 'ecosystem', 'entropy']
        score += 0.05 * sum(1 for w in unexpected_words if w in idea.lower())
        
        return min(1.0, score)
    
    def _describe_combination(self, idea: str) -> str:
        """Describe what domains are combined."""
        domains_found = [d for d in self.concept_space.keys() if d in idea.lower()]
        return " and ".join(domains_found) if domains_found else "multiple domains"
    
    def _create_novel_analogy(self, subject: str, domain: str) -> str:
        """Create a novel analogy when none exists."""
        # Find similar patterns in other domains
        other_domains = [d for d in self.concept_space.keys() if d != domain]
        
        if other_domains:
            target = random.choice(other_domains)
            concept = random.choice(self.concept_space[target].get('concepts', ['systems']))
            return f"**Analogy:** {subject} works like {concept} in {target} - both involve dynamic adaptation to changing conditions."
        
        return f"**Analogy:** {subject} is like a complex adaptive system - many parts interacting to produce emergent behavior."
    
    def _generate_perspectives(self, text: str) -> List[str]:
        """Generate alternative perspectives on content."""
        perspectives = []
        
        # Technical perspective
        perspectives.append(f"From a technical standpoint: This involves system optimization and feedback loops.")
        
        # Strategic perspective
        perspectives.append(f"Strategically: Consider the long-term implications and second-order effects.")
        
        # Risk perspective
        perspectives.append(f"Risk perspective: What could go wrong, and how would we detect it early?")
        
        return perspectives
    
    def _extract_domain(self, text: str) -> str:
        """Extract domain from text."""
        domain_keywords = {
            'trading': ['trade', 'token', 'price', 'market', 'strategy'],
            'ai': ['ai', 'machine learning', 'neural', 'algorithm', 'model'],
            'biology': ['bio', 'evolution', 'organic', 'natural', 'ecosystem'],
            'physics': ['physics', 'mechanics', 'energy', 'force', 'momentum']
        }
        
        text_lower = text.lower()
        for domain, keywords in domain_keywords.items():
            if any(kw in text_lower for kw in keywords):
                return domain
        
        return 'trading'  # Default
    
    def _extract_subject(self, text: str) -> str:
        """Extract subject from text."""
        # Remove request words
        words = ['create', 'design', 'invent', 'generate', 'build', 'develop', 'analogy', 'like']
        subject = text.lower()
        for word in words:
            subject = subject.replace(word, '')
        return subject.strip(' ?')
    
    def _extract_condition(self, text: str) -> str:
        """Extract condition from 'what if' question."""
        import re
        match = re.search(r'what\s+if\s+(.+?)[\?\.]?$', text.lower())
        if match:
            return match.group(1).strip()
        return "this situation changes"
    
    def _generate_best_case(self, condition: str) -> str:
        """Generate best case scenario."""
        return f"Everything aligns perfectly. The conditions create a virtuous cycle where each success enables greater success. Outcomes exceed expectations by 2-3x."
    
    def _generate_likely_case(self, condition: str) -> str:
        """Generate most likely scenario."""
        return f"Mixed results with overall positive trend. Some challenges emerge but are manageable. Progress is slower than hoped but steady."
    
    def _generate_worst_case(self, condition: str) -> str:
        """Generate worst case scenario."""
        return f"Unforeseen complications arise. External factors create headwinds. Requires significant adaptation or pivot. Lessons learned are valuable."


if __name__ == "__main__":
    # Test CEL-Creativity
    print("💡 Testing CEL-Creativity...")
    
    creativity = CELCreativity()
    
    test_requests = [
        "Create a new trading strategy",
        "What's an analogy for momentum trading?",
        "What if the market crashes tomorrow?",
        "We need to improve the scanner"
    ]
    
    for request in test_requests:
        print(f"\n{'='*60}")
        print(f"Request: {request}")
        result = creativity.process(request)
        print(f"Result: {result}")
    
    print(f"\n{'='*60}")
    print("CEL-Creativity module ready!")
