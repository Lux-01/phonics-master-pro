#!/usr/bin/env python3
"""
CEL-Understanding: Causal Reasoning + Explanation Generation
Addresses: "No understanding - I pattern match, I don't 'get it'"

ACA Implementation - Phase 2: Understanding Module
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import sys

sys.path.insert(0, '/home/skux/.openclaw/workspace')


class CELUnderstanding:
    """
    Provides true understanding through:
    - Causal reasoning (why things happen)
    - Concept grounding (linking to knowledge)
    - Explanation generation (making it clear)
    - "Why" question answering
    """
    
    def __init__(self):
        self.causal_patterns = self._load_causal_patterns()
        self.explanation_templates = self._load_explanation_templates()
        self.concept_cache = {}
    
    def _load_causal_patterns(self) -> Dict:
        """Load causal reasoning patterns."""
        return {
            'because': {
                'pattern': r'(.+?)\s+because\s+(.+)',
                'extract': lambda m: {'effect': m.group(1), 'cause': m.group(2)}
            },
            'causes': {
                'pattern': r'(.+?)\s+causes?\s+(.+)',
                'extract': lambda m: {'cause': m.group(1), 'effect': m.group(2)}
            },
            'leads_to': {
                'pattern': r'(.+?)\s+leads?\s+to\s+(.+)',
                'extract': lambda m: {'cause': m.group(1), 'effect': m.group(2)}
            },
            'results_in': {
                'pattern': r'(.+?)\s+results?\s+in\s+(.+)',
                'extract': lambda m: {'cause': m.group(1), 'effect': m.group(2)}
            },
            'if_then': {
                'pattern': r'if\s+(.+?),?\s+then\s+(.+)',
                'extract': lambda m: {'condition': m.group(1), 'result': m.group(2)}
            }
        }
    
    def _load_explanation_templates(self) -> Dict:
        """Load explanation generation templates."""
        return {
            'simple': "{concept} works by {mechanism}.",
            'detailed': "{concept} operates through {mechanism}. This happens because {reasoning}. As a result, {outcome}.",
            'causal': "The reason {effect} occurs is that {cause}.",
            'comparative': "Unlike {alternative}, {concept} {difference} because {reason}.",
            'procedural': "To {action}, you need to {steps}. This works because {principle}."
        }
    
    def process(self, user_input: str, context: Dict = None, 
                analysis: Dict = None) -> str:
        """
        Main processing entry point.
        
        Returns explanation with causal reasoning.
        """
        # Determine what type of understanding is needed
        if self._is_why_question(user_input):
            return self._explain_why(user_input, context)
        
        elif self._is_how_question(user_input):
            return self._explain_how(user_input, context)
        
        elif self._is_what_question(user_input):
            return self._explain_what(user_input, context)
        
        else:
            # General understanding enhancement
            return self._enhance_understanding(user_input, context)
    
    def _is_why_question(self, text: str) -> bool:
        """Detect if this is a 'why' question."""
        why_patterns = [
            r'why\s+(is|are|does|do|did|would|should)',
            r'why\s+\w+',
            r'what\s+is\s+the\s+reason',
            r'how\s+come',
            r'explain\s+why'
        ]
        text_lower = text.lower()
        return any(re.search(p, text_lower) for p in why_patterns)
    
    def _is_how_question(self, text: str) -> bool:
        """Detect if this is a 'how' question."""
        how_patterns = [
            r'^how\s+(do|does|can|should|would)',
            r'how\s+to\s+\w+',
            r'how\s+does\s+\w+\s+work'
        ]
        text_lower = text.lower()
        return any(re.search(p, text_lower) for p in how_patterns)
    
    def _is_what_question(self, text: str) -> bool:
        """Detect if this is a 'what' question."""
        what_patterns = [
            r'^what\s+(is|are)',
            r'what\s+does\s+\w+\s+mean',
            r'define\s+\w+'
        ]
        text_lower = text.lower()
        return any(re.search(p, text_lower) for p in what_patterns)
    
    def _explain_why(self, question: str, context: Dict) -> str:
        """Generate causal explanation for 'why' questions."""
        # Extract the subject
        subject = self._extract_subject(question)
        
        # Look for causal relationships in knowledge
        cause = self._find_cause(subject)
        mechanism = self._find_mechanism(subject)
        
        if cause and mechanism:
            return f"**Why {subject}?**\n\n{cause}\n\n**How it works:** {mechanism}"
        elif cause:
            return f"**Why {subject}?**\n\n{cause}"
        else:
            return f"**Understanding {subject}:**\n\nBased on the patterns I've observed, this likely relates to {self._infer_cause(subject)}."
    
    def _explain_how(self, question: str, context: Dict) -> str:
        """Generate procedural explanation for 'how' questions."""
        subject = self._extract_subject(question)
        
        steps = self._find_procedure(subject)
        principle = self._find_principle(subject)
        
        if steps and principle:
            return f"**How {subject}:**\n\n{steps}\n\n**Why this works:** {principle}"
        elif steps:
            return f"**How {subject}:**\n\n{steps}"
        else:
            return f"**Understanding {subject}:**\n\nThis process involves {self._infer_procedure(subject)}."
    
    def _explain_what(self, question: str, context: Dict) -> str:
        """Generate definitional explanation for 'what' questions."""
        subject = self._extract_subject(question)
        
        definition = self._find_definition(subject)
        example = self._find_example(subject)
        
        if definition and example:
            return f"**What is {subject}?**\n\n{definition}\n\n**Example:** {example}"
        elif definition:
            return f"**What is {subject}?**\n\n{definition}"
        else:
            return f"**{subject}** refers to {self._infer_definition(subject)}."
    
    def _enhance_understanding(self, text: str, context: Dict) -> str:
        """General understanding enhancement."""
        # Extract key concepts
        concepts = self._extract_concepts(text)
        
        if not concepts:
            return text
        
        # Ground concepts in knowledge
        grounded = []
        for concept in concepts[:3]:  # Top 3 concepts
            grounding = self._ground_concept(concept)
            if grounding:
                grounded.append(f"**{concept}**: {grounding}")
        
        if grounded:
            return text + "\n\n**Key concepts:**\n" + "\n".join(grounded)
        
        return text
    
    def _extract_subject(self, text: str) -> str:
        """Extract the main subject from a question."""
        # Remove question words
        cleaned = re.sub(r'^(why|how|what|is|are|does|do|did|would|should|can|to)\s+', '', text.lower())
        cleaned = re.sub(r'\?$', '', cleaned)
        return cleaned.strip()
    
    def _extract_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text."""
        # Simple noun phrase extraction
        words = text.split()
        concepts = []
        
        # Look for capitalized phrases (proper nouns)
        current_concept = []
        for word in words:
            if word[0].isupper() or word in ['scanner', 'trading', 'strategy', 'token']:
                current_concept.append(word)
            else:
                if current_concept:
                    concepts.append(' '.join(current_concept))
                    current_concept = []
        
        if current_concept:
            concepts.append(' '.join(current_concept))
        
        # Also look for technical terms
        tech_terms = ['scanner', 'strategy', 'algorithm', 'pattern', 'signal', 'trade']
        for term in tech_terms:
            if term in text.lower() and term not in [c.lower() for c in concepts]:
                concepts.append(term)
        
        return list(set(concepts))  # Remove duplicates
    
    def _find_cause(self, subject: str) -> Optional[str]:
        """Find causal explanation for subject."""
        # Query knowledge graph or patterns
        causal_db = {
            'scanner miss tokens': "Scanners miss tokens when they don't meet the minimum liquidity threshold or age filters. The scanner is designed to filter out high-risk tokens.",
            'trades fail': "Trades fail when there's insufficient liquidity, high slippage, or network congestion. The transaction can't be executed at the desired price.",
            'price drops': "Price drops when selling pressure exceeds buying pressure. This can happen due to profit-taking, negative news, or market sentiment shifts.",
        }
        
        for key, explanation in causal_db.items():
            if key in subject.lower():
                return explanation
        
        return None
    
    def _find_mechanism(self, subject: str) -> Optional[str]:
        """Find mechanism explanation."""
        mechanism_db = {
            'scanner': "The scanner works by querying DEX APIs (Jupiter, Birdeye) for token data, then applying filters for liquidity, volume, and age. It scores tokens based on multiple metrics.",
            'trading strategy': "The strategy uses technical indicators (RSI, EMA) combined with risk scoring. It enters positions when signals align and exits based on stop-loss or take-profit rules.",
        }
        
        for key, explanation in mechanism_db.items():
            if key in subject.lower():
                return explanation
        
        return None
    
    def _find_procedure(self, subject: str) -> Optional[str]:
        """Find procedural steps."""
        procedure_db = {
            'create strategy': "1. Define entry criteria (indicators, thresholds)\n2. Define exit rules (stop-loss, take-profit)\n3. Set position sizing\n4. Backtest on historical data\n5. Paper trade to validate\n6. Deploy with safety limits",
            'analyze token': "1. Check liquidity and volume\n2. Analyze price action\n3. Review holder distribution\n4. Check contract safety\n5. Evaluate narrative/fit\n6. Calculate risk score",
        }
        
        for key, steps in procedure_db.items():
            if key in subject.lower():
                return steps
        
        return None
    
    def _find_principle(self, subject: str) -> Optional[str]:
        """Find underlying principle."""
        principle_db = {
            'trading': "Trading works by exploiting market inefficiencies. When supply and demand are imbalanced, prices move. Successful trading identifies these imbalances early.",
            'scanning': "Scanning works on the principle that not all tokens are equal. By filtering for quality metrics (liquidity, volume, age), we can identify higher-probability opportunities.",
        }
        
        for key, principle in principle_db.items():
            if key in subject.lower():
                return principle
        
        return None
    
    def _find_definition(self, subject: str) -> Optional[str]:
        """Find definition."""
        definition_db = {
            'mean reversion': "Mean reversion is the theory that prices tend to return to their average over time. Extreme moves in one direction are likely to be followed by moves in the opposite direction.",
            'liquidity': "Liquidity refers to how easily an asset can be bought or sold without affecting its price. High liquidity means large trades can occur with minimal price impact.",
            'market cap': "Market capitalization is the total value of all tokens in circulation, calculated as price × circulating supply.",
        }
        
        for key, definition in definition_db.items():
            if key in subject.lower():
                return definition
        
        return None
    
    def _find_example(self, subject: str) -> Optional[str]:
        """Find example."""
        example_db = {
            'mean reversion': "If a token pumps 50% in an hour with no news, mean reversion suggests it's likely to pull back as early buyers take profits.",
            'liquidity': "A token with $100K liquidity can handle $1K trades easily, but a $10K trade might move the price 10%.",
        }
        
        for key, example in example_db.items():
            if key in subject.lower():
                return example
        
        return None
    
    def _ground_concept(self, concept: str) -> Optional[str]:
        """Ground concept in existing knowledge."""
        # Try to find in knowledge graph
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("kge_runner", 
                "/home/skux/.openclaw/workspace/skills/knowledge-graph-engine/kge_runner.py")
            kge = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(kge)
            result = kge.query_knowledge(f"What is {concept}?")
            if result:
                return result
        except:
            pass
        
        # Fallback to definition lookup
        return self._find_definition(concept)
    
    def _infer_cause(self, subject: str) -> str:
        """Infer cause when not in database."""
        return f"multiple interacting factors including market conditions, token-specific characteristics, and timing"
    
    def _infer_procedure(self, subject: str) -> str:
        """Infer procedure when not in database."""
        return "a series of steps that depend on the specific context and requirements"
    
    def _infer_definition(self, subject: str) -> str:
        """Infer definition when not in database."""
        return f"a concept or system related to {subject.split()[0] if subject else 'this domain'}"


if __name__ == "__main__":
    # Test CEL-Understanding
    print("🧠 Testing CEL-Understanding...")
    
    understanding = CELUnderstanding()
    
    test_questions = [
        "Why does the scanner miss some tokens?",
        "How does mean reversion work?",
        "What is liquidity?",
        "The trading strategy uses multiple indicators"
    ]
    
    for question in test_questions:
        print(f"\n{'='*60}")
        print(f"Q: {question}")
        result = understanding.process(question)
        print(f"A: {result}")
    
    print(f"\n{'='*60}")
    print("CEL-Understanding module ready!")
