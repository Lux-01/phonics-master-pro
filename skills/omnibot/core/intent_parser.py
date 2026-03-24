"""
Omnibot Intent Parser

Understands user goals and extracts structured intent from natural language.
Uses pattern matching with confidence scoring.
"""

import re
import uuid
from typing import Dict, List, Optional, Any, Pattern
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger("omnibot.intent")


class IntentType(Enum):
    """Supported intent types."""
    RESEARCH = "research"
    DESIGN = "design"
    CODE = "code"
    JOB_SEEK = "job_seek"
    JOB_EXECUTE = "job_execute"
    QUERY = "query"
    META = "meta"
    UNKNOWN = "unknown"


@dataclass
class Intent:
    """
    Parsed intent with confidence and entities.
    
    Attributes:
        intent_id: Unique identifier
        intent_type: Classified intent type
        confidence: 0.0 to 1.0 confidence score
        entities: Extracted entities
        raw_input: Original user input
        disambiguation_needed: Whether clarification required
    """
    intent_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    intent_type: str = IntentType.UNKNOWN.value
    confidence: float = 0.0
    entities: Dict[str, Any] = field(default_factory=dict)
    raw_input: str = ""
    disambiguation_needed: bool = False
    suggested_questions: List[str] = field(default_factory=list)
    
    def is_confident(self, threshold: float = 0.7) -> bool:
        """Check if confidence meets threshold."""
        return self.confidence >= threshold


@dataclass
class IntentPattern:
    """Pattern for matching intent."""
    intent_type: str
    patterns: List[Pattern]
    weight: float = 1.0
    entity_extractors: List[callable] = field(default_factory=list)


class IntentParser:
    """
    Parses user input into structured intent.
    
    Supports:
    - Pattern matching for intent classification
    - Entity extraction (URLs, dates, names, etc.)
    - Confidence scoring
    - Disambiguation for ambiguous input
    
    Example:
        parser = IntentParser()
        intent = parser.parse("Create a website for my coffee shop")
        # intent.intent_type == "design"
        # intent.confidence == 0.85
        # intent.entities == {"topic": "website", "business": "coffee shop"}
    """
    
    def __init__(self):
        """Initialize intent parser with patterns."""
        self._patterns: Dict[str, List[IntentPattern]] = {}
        self._entity_patterns = {
            "url": re.compile(r'https?://[^\s]+|www\.[^\s]+'),
            "email": re.compile(r'[\w.-]+@[\w.-]+\.[a-zA-Z]{2,}'),
            "date": re.compile(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]* \d{1,2}(?:,)? \d{4}', re.I),
            "money": re.compile(r'\$[\d,]+(?:\.\d{2})?|\d+(?:\.\d{2})?\s*(?:dollars?|usd)', re.I),
            "time": re.compile(r'\d{1,2}:\d{2}\s*(?:am|pm)?', re.I),
        }
        
        self._setup_intent_patterns()
        logger.info("IntentParser initialized")
    
    def _setup_intent_patterns(self):
        """Setup regex patterns for intent classification."""
        
        # Research patterns
        self._add_intent_pattern(IntentType.RESEARCH.value, [
            r'\b(find|search|look up|research|get info|tell me about|what is|who is|where is|how (?:do|does|can|to))\b',
            r'\b(learn about|information on|details about|explain)\b',
        ], weight=1.0)
        
        # Design patterns
        self._add_intent_pattern(IntentType.DESIGN.value, [
            r'\b(create|design|make|build)\s+(?:a|an|me)\s+(?:website|logo|graphic|ui|ux|mockup|wireframe)\b',
            r'\b(website for|design for|portfolio|landing page)\b',
            r'\b(style|theme|layout|visual|branding)\b',
        ], weight=1.2)
        
        # Code patterns
        self._add_intent_pattern(IntentType.CODE.value, [
            r'\b(write|code|script|program|function|class|module|app|application)\b',
            r'\b(build|create)\s+(?:a|an|me)\s+(?:script|program|bot|tool|app)\b',
            r'\b(in python|in javascript|in js|in rust|in go|in java|in c\+\+)\b',
            r'\b(api|scraper|automation|script that|code that)\b',
        ], weight=1.1)
        
        # Job seek patterns
        self._add_intent_pattern(IntentType.JOB_SEEK.value, [
            r'\b(find|looking for|search for|get|help me find)\s+(?:a|an)?\s*(?:job|work|position|career|opportunit|gig|role)\b',
            r'\b(job search|hiring|employment|freelance|contract)\b',
            r'\b(resume|cv|cover letter|interview|apply|application)\b',
        ], weight=1.0)
        
        # Job execute patterns
        self._add_intent_pattern(IntentType.JOB_EXECUTE.value, [
            r'\b(complete|finish|do|execute|run|start|work on)\s+(?:this|the|my)\s*(?:task|job|project|mission)\b',
            r'\b(execute|run|process|handle)\s+(?:the|this)\b',
            r'\b(do it|get it done|make it happen|proceed|continue)\b',
        ], weight=0.9)
        
        # Query patterns (questions about past)
        self._add_intent_pattern(IntentType.QUERY.value, [
            r'\b(what did we|remember|recall|when did|where did|how did we|did we)\b',
            r'\b(what was|where is|show me|remind me|check if)\b',
            r'\b(status of|progress on|update on)\b',
        ], weight=0.8)
        
        # Meta patterns
        self._add_intent_pattern(IntentType.META.value, [
            r'\b(how do you work|what can you do|who are you|help|capabilities|features)\b',
            r'\b(settings|configure|setup|preference)\b',
            r'\b(status|health|state|version)\b',
        ], weight=0.7)
    
    def _add_intent_pattern(self, intent_type: str, patterns: List[str], weight: float = 1.0):
        """Add patterns for an intent type."""
        compiled = [re.compile(p, re.I) for p in patterns]
        
        if intent_type not in self._patterns:
            self._patterns[intent_type] = []
        
        self._patterns[intent_type].append(IntentPattern(
            intent_type=intent_type,
            patterns=compiled,
            weight=weight
        ))
    
    def parse(self, user_input: str) -> Intent:
        """
        Parse user input into structured intent.
        
        Args:
            user_input: Raw user input
            
        Returns:
            Intent with type, confidence, and entities
        """
        user_input_lower = user_input.lower()
        
        # Score each intent type
        scores: Dict[str, float] = {}
        
        for intent_type, patterns in self._patterns.items():
            for pattern_group in patterns:
                for pattern in pattern_group.patterns:
                    matches = pattern.findall(user_input_lower)
                    if matches:
                        score = len(matches) * pattern_group.weight
                        scores[intent_type] = scores.get(intent_type, 0) + score
        
        # Determine best intent
        if scores:
            best_intent = max(scores, key=scores.get)
            max_score = scores[best_intent]
            total_score = sum(scores.values())
            confidence = min(max_score / (total_score or 1), 1.0)
        else:
            best_intent = IntentType.UNKNOWN.value
            confidence = 0.0
        
        # Extract entities
        entities = self.extract_entities(user_input)
        
        # Check if disambiguation needed
        disambiguation_needed, questions = self._check_disambiguation(
            user_input, best_intent, confidence
        )
        
        return Intent(
            intent_type=best_intent,
            confidence=round(confidence, 2),
            entities=entities,
            raw_input=user_input,
            disambiguation_needed=disambiguation_needed,
            suggested_questions=questions
        )
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract entities from text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of entity types to values
        """
        entities = {
            "urls": [],
            "emails": [],
            "dates": [],
            "money": [],
            "times": [],
            "topics": [],
        }
        
        # Extract with regex patterns
        for entity_type, pattern in self._entity_patterns.items():
            matches = pattern.findall(text)
            key = entity_type + "s" if not entity_type.endswith("s") else entity_type
            entities[key] = matches
        
        # Extract quoted strings as topics
        quoted = re.findall(r'["\']([^"\']+)["\']', text)
        if quoted:
            entities["quoted_phrases"] = quoted
        
        # Extract "for X" patterns
        for_match = re.search(r'\bfor\s+(?:(?:my|a|an|the)\s+)?([^,.]+)', text, re.I)
        if for_match:
            entities["for_target"] = for_match.group(1).strip()
        
        # Extract "about X" patterns
        about_match = re.search(r'\babout\s+([^,.]+)', text, re.I)
        if about_match:
            entities["about_topic"] = about_match.group(1).strip()
        
        # Extract file extensions
        files = re.findall(r'[\w-]+\.(?:py|js|ts|rs|go|java|txt|md|json|yaml|yml)', text, re.I)
        if files:
            entities["file_references"] = files
        
        # Clean up empty lists
        entities = {k: v for k, v in entities.items() if v}
        
        return entities
    
    def _check_disambiguation(self, text: str, intent_type: str, 
                             confidence: float) -> tuple:
        """
        Check if input is ambiguous and needs clarification.
        
        Args:
            text: Raw input
            intent_type: Detected intent
            confidence: Confidence score
            
        Returns:
            Tuple of (needs_disambiguation, suggested_questions)
        """
        if confidence >= 0.7:
            return False, []
        
        questions = []
        text_lower = text.lower()
        
        # Ambiguous "create"
        if "create" in text_lower or "build" in text_lower:
            if "website" in text_lower or "design" in text_lower or "logo" in text_lower:
                return False, []
            elif "code" in text_lower or "script" in text_lower or "program" in text_lower:
                return False, []
            questions.append("Do you want me to write code or create a design?")
        
        # Ambiguous "find"
        if "find" in text_lower and confidence < 0.7:
            questions.append("Are you looking for a job or searching for information?")
        
        # Too short/vague
        if len(text.split()) < 3:
            questions.append("Could you provide more details about what you need?")
        
        return len(questions) > 0, questions
    
    def disambiguate(self, 
                    ambiguous_input: str,
                    previous_intents: Optional[List[Intent]] = None) -> List[str]:
        """
        Generate clarifying questions for ambiguous input.
        
        Args:
            ambiguous_input: The vague input
            previous_intents: Previous conversation context
            
        Returns:
            List of clarifying questions
        """
        questions = []
        text = ambiguous_input.lower()
        
        # Check for common ambiguity patterns
        if re.search(r'\b(create|build|make)\b', text):
            questions.extend([
                "Are you asking me to write code (programming) or create a design?",
                "Would you like a website, an app, or a script?",
            ])
        
        elif re.search(r'\b(find|search|look)\b', text):
            questions.extend([
                "Are you looking for a job/position, or searching for information?",
                "Do you want me to search the web or check my memory?",
            ])
        
        elif len(text.split()) < 4:
            questions.extend([
                "Could you provide more details about what you need?",
                "What specific task would you like me to help with?",
                "Could you rephrase that with more context?",
            ])
        
        # Use context from previous intents
        if previous_intents:
            last_intent = previous_intents[-1]
            if last_intent.intent_type == IntentType.CODE.value:
                questions.append(f"Are you continuing the coding task about {last_intent.entities.get('about_topic', 'that topic')}?")
        
        return questions
    
    def batch_parse(self, inputs: List[str]) -> List[Intent]:
        """
        Parse multiple inputs.
        
        Args:
            inputs: List of user inputs
            
        Returns:
            List of intents
        """
        return [self.parse(inp) for inp in inputs]
    
    def add_custom_pattern(self, intent_type: str, 
                         pattern: str,
                         weight: float = 1.0):
        """
        Add custom pattern for intent matching.
        
        Args:
            intent_type: Intent type to match
            pattern: Regex pattern
            weight: Pattern weight
        """
        self._add_intent_pattern(intent_type, [pattern], weight)
        logger.info(f"Added custom pattern for {intent_type}")
    
    def get_intent_stats(self) -> Dict[str, Any]:
        """Get parser statistics."""
        return {
            "configured_intents": len(self._patterns),
            "intent_types": list(self._patterns.keys()),
            "entity_patterns": len(self._entity_patterns),
        }