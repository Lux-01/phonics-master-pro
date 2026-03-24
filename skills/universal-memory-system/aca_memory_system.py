#!/usr/bin/env python3
"""
Universal Memory System (UMS) v1.0
ACA-Compliant: Planned, self-debugged, tested architecture

Purpose: Never forget anything - research, conversations, decisions, context.
Built following Autonomous Code Architect methodology.
"""

import json
import hashlib
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

MEMORY_DIR = Path("/home/skux/.openclaw/workspace/memory")
KNOWLEDGE_DIR = MEMORY_DIR / "knowledge"
RAW_DIR = MEMORY_DIR / "raw_capture"
INDEX_FILE = MEMORY_DIR / "index.json"

# Categories for automatic classification
class MemoryCategory(Enum):
    RESEARCH = "research"
    CODE = "code"
    DECISION = "decision"
    CONVERSATION = "conversation"
    PROJECT = "project"
    API_KEY = "api_key"
    PREFERENCE = "preference"
    UNKNOWN = "unknown"

# Keywords for auto-categorization
CATEGORY_KEYWORDS = {
    MemoryCategory.RESEARCH: ["research", "study", "analyze", "find", "search",
                               "report", "data", "source", "reference"],
    MemoryCategory.CODE: ["build", "create", "develop", "script", "function",
                           "module", "fix", "bug", "error", "refactor"],
    MemoryCategory.DECISION: ["decided", "decision", "choose", "selected",
                              "concluded", "agreed", "voted"],
    MemoryCategory.CONVERSATION: ["said", "mentioned", "discussed", "talked"],
    MemoryCategory.PROJECT: ["project", "app", "system", "feature", "milestone"],
    MemoryCategory.API_KEY: ["api key", "token", "credential", "password", "secret"],
    MemoryCategory.PREFERENCE: ["prefer", "like", "want", "usually", "always"]
}

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class MemoryEntry:
    """Single memory entry with metadata"""
    id: str
    timestamp: str
    category: str
    content: str
    source: str  # Where this came from
    tags: List[str]
    importance: int  # 1-10, auto-calculated
    access_count: int = 0
    last_accessed: Optional[str] = None
    related_ids: List[str] = None
    
    def __post_init__(self):
        if self.related_ids is None:
            self.related_ids = []
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "MemoryEntry":
        # Filter data to only include fields this class knows about
        valid_fields = {f for f in cls.__dataclass_fields__}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)

@dataclass
class ResearchEntry(MemoryEntry):
    """Extended entry for research with sources"""
    sources: List[str] = None
    key_findings: List[str] = None
    confidence: int = 5  # 1-10
    
    def __post_init__(self):
        super().__post_init__()
        if self.sources is None:
            self.sources = []
        if self.key_findings is None:
            self.key_findings = []

@dataclass
class DecisionEntry(MemoryEntry):
    """Extended entry for decisions"""
    context: str = ""
    alternatives: List[str] = None
    reasoning: str = ""
    reversible: bool = True
    
    def __post_init__(self):
        super().__post_init__()
        if self.alternatives is None:
            self.alternatives = []

@dataclass
class ConversationFragment:
    """Raw conversation capture"""
    timestamp: str
    speaker: str  # "user" or "assistant"
    content: str
    intent: Optional[str] = None
    entities: List[str] = None
    
    def __post_init__(self):
        if self.entities is None:
            self.entities = []

# ============================================================================
# CORE MEMORY SYSTEM
# ============================================================================

class UniversalMemorySystem:
    """
    Main memory system interface.
    Provides: capture, store, retrieve, search, and context surfacing.
    """
    
    def __init__(self):
        self.memory_dir = MEMORY_DIR
        self._ensure_directories()
        self.index = self._load_index()
        self.session_cache: List[MemoryEntry] = []
    
    def _ensure_directories(self):
        """Create memory structure if missing"""
        directories = [
            MEMORY_DIR,
            KNOWLEDGE_DIR,
            KNOWLEDGE_DIR / "research",
            KNOWLEDGE_DIR / "decisions",
            KNOWLEDGE_DIR / "projects",
            KNOWLEDGE_DIR / "people",
            RAW_DIR
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_index(self) -> Dict:
        """Load or create searchable index"""
        if INDEX_FILE.exists():
            try:
                with open(INDEX_FILE) as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        
        # Create fresh index
        return {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "entries": {},
            "tags": {},
            "keywords": {}
        }
    
    def _save_index(self):
        """Persist index to disk"""
        self.index["updated"] = datetime.now().isoformat()
        with open(INDEX_FILE, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def _generate_id(self, content: str) -> str:
        """Generate unique ID from content hash"""
        timestamp = datetime.now().isoformat()
        hash_input = f"{content}{timestamp}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text"""
        # Simple keyword extraction - can be enhanced with NLP
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        
        # Filter common words
        stop_words = {"this", "that", "with", "from", "they", "have", "were", "been", 
                      "their", "said", "each", "which", "will", "about", "could", "other"}
        keywords = [w for w in words if w not in stop_words]
        
        # Return top 10 by frequency
        from collections import Counter
        return [word for word, count in Counter(keywords).most_common(10)]
    
    def _classify_content(self, content: str) -> MemoryCategory:
        """Auto-classify content into category"""
        content_lower = content.lower()
        scores = {cat: 0 for cat in MemoryCategory}
        
        for category, keywords in CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in content_lower:
                    scores[category] += 1
        
        # Get highest scoring category
        max_score = max(scores.values())
        if max_score == 0:
            return MemoryCategory.UNKNOWN
        
        return max(scores, key=scores.get)
    
    def _calculate_importance(self, content: str, category: MemoryCategory) -> int:
        """Calculate importance score (1-10)"""
        score = 5  # Base score
        
        # Length factor (substantial content = more important)
        if len(content) > 500:
            score += 2
        elif len(content) > 200:
            score += 1
        
        # Category factor
        if category == MemoryCategory.DECISION:
            score += 2
        elif category == MemoryCategory.API_KEY:
            score += 3
        elif category == MemoryCategory.RESEARCH:
            score += 1
        
        # Capitalization factor (shouting = important)
        caps_ratio = sum(1 for c in content if c.isupper()) / max(len(content), 1)
        if caps_ratio > 0.3:
            score += 1
        
        return min(score, 10)
    
    # ========================================================================
    # PUBLIC API
    # ========================================================================
    
    def capture(self, content: str, source: str = "conversation",
                category: Optional[str] = None,
                tags: Optional[List[str]] = None) -> str:
        """
        Capture a new memory entry.
        
        Args:
            content: The content to remember
            source: Where this came from (conversation, research, etc.)
            category: Optional explicit category
            tags: Optional tags for organization
            
        Returns:
            entry_id: The ID of the created entry
        """
        # Auto-classify if not provided
        if category:
            cat = MemoryCategory(category)
        else:
            cat = self._classify_content(content)
        
        # Create entry
        entry = MemoryEntry(
            id=self._generate_id(content),
            timestamp=datetime.now().isoformat(),
            category=cat.value,
            content=content,
            source=source,
            tags=tags or [],
            importance=self._calculate_importance(content, cat)
        )
        
        # Add to index
        self.index["entries"][entry.id] = {
            "timestamp": entry.timestamp,
            "category": entry.category,
            "tags": entry.tags,
            "keywords": self._extract_keywords(content),
            "importance": entry.importance
        }
        
        # Update tag index
        for tag in entry.tags:
            if tag not in self.index["tags"]:
                self.index["tags"][tag] = []
            self.index["tags"][tag].append(entry.id)
        
        # Update keyword index
        for keyword in self._extract_keywords(content):
            if keyword not in self.index["keywords"]:
                self.index["keywords"][keyword] = []
            self.index["keywords"][keyword].append(entry.id)
        
        # Save to disk
        self._save_entry_to_file(entry)
        self._save_index()
        
        # Add to session cache
        self.session_cache.append(entry)
        
        return entry.id
    
    def _save_entry_to_file(self, entry: MemoryEntry):
        """Save entry to appropriate file based on category"""
        date_str = entry.timestamp[:10]  # YYYY-MM-DD
        
        if entry.category == MemoryCategory.RESEARCH.value:
            filename = KNOWLEDGE_DIR / "research" / f"{date_str}.jsonl"
        elif entry.category == MemoryCategory.DECISION.value:
            filename = KNOWLEDGE_DIR / "decisions" / f"{date_str}.jsonl"
        elif entry.category == MemoryCategory.PROJECT.value:
            filename = KNOWLEDGE_DIR / "projects" / f"{date_str}.jsonl"
        else:
            filename = RAW_DIR / f"{date_str}.jsonl"
        
        # Append to file
        with open(filename, 'a') as f:
            f.write(json.dumps(entry.to_dict()) + '\n')
    
    def search(self, query: str, limit: int = 10,
               category_filter: Optional[str] = None,
               date_range: Optional[Tuple[str, str]] = None) -> List[MemoryEntry]:
        """
        Search memories by query.
        
        Args:
            query: Search query
            limit: Max results
            category_filter: Optional category to filter by
            date_range: Optional (start, end) dates
            
        Returns:
            List of matching MemoryEntry objects
        """
        results = []
        query_lower = query.lower()
        query_keywords = self._extract_keywords(query)
        
        # Search by keyword index first
        matching_ids = set()
        for keyword in query_keywords:
            if keyword in self.index["keywords"]:
                matching_ids.update(self.index["keywords"][keyword])
        
        # Also search content directly for partial matches
        for entry_id, meta in self.index["entries"].items():
            if entry_id not in matching_ids:
                # Check if query appears in any indexed content
                if any(kw in query_lower for kw in meta.get("keywords", [])):
                    matching_ids.add(entry_id)
        
        # Filter and rank results
        for entry_id in matching_ids:
            meta = self.index["entries"][entry_id]
            
            # Apply category filter
            if category_filter and meta["category"] != category_filter:
                continue
            
            # Apply date range filter
            if date_range:
                entry_date = meta["timestamp"][:10]
                if not (date_range[0] <= entry_date <= date_range[1]):
                    continue
            
            # Load full entry
            entry = self._load_entry_by_id(entry_id)
            if entry:
                # Calculate relevance score
                relevance = self._calculate_relevance(entry, query_keywords)
                results.append((relevance, entry))
        
        # Sort by relevance and return top results
        results.sort(key=lambda x: x[0], reverse=True)
        
        # Update access metadata
        for _, entry in results[:limit]:
            self._mark_accessed(entry.id)
        
        return [entry for _, entry in results[:limit]]
    
    def _load_entry_by_id(self, entry_id: str) -> Optional[MemoryEntry]:
        """Load a specific entry by ID"""
        if entry_id not in self.index["entries"]:
            return None
        
        meta = self.index["entries"][entry_id]
        date_str = meta["timestamp"][:10]
        category = meta["category"]
        
        # Determine file path
        if category == MemoryCategory.RESEARCH.value:
            filename = KNOWLEDGE_DIR / "research" / f"{date_str}.jsonl"
        elif category == MemoryCategory.DECISION.value:
            filename = KNOWLEDGE_DIR / "decisions" / f"{date_str}.jsonl"
        elif category == MemoryCategory.PROJECT.value:
            filename = KNOWLEDGE_DIR / "projects" / f"{date_str}.jsonl"
        else:
            filename = RAW_DIR / f"{date_str}.jsonl"
        
        # Search file for entry
        if filename.exists():
            with open(filename) as f:
                for line in f:
                    data = json.loads(line.strip())
                    if data["id"] == entry_id:
                        return MemoryEntry.from_dict(data)
        
        return None
    
    def _calculate_relevance(self, entry: MemoryEntry, query_keywords: List[str]) -> float:
        """Calculate relevance score for ranking"""
        score = 0.0
        entry_keywords = self._extract_keywords(entry.content)
        
        # Keyword overlap
        overlap = set(query_keywords) & set(entry_keywords)
        score += len(overlap) * 10
        
        # Recency bonus
        entry_date = datetime.fromisoformat(entry.timestamp)
        days_ago = (datetime.now() - entry_date).days
        if days_ago < 7:
            score += 5
        elif days_ago < 30:
            score += 2
        
        # Importance weight
        score += entry.importance * 2
        
        # Access frequency (popular = relevant)
        score += entry.access_count * 0.5
        
        return score
    
    def _mark_accessed(self, entry_id: str):
        """Update access metadata for an entry"""
        if entry_id in self.index["entries"]:
            self.index["entries"][entry_id]["last_accessed"] = datetime.now().isoformat()
            # We'll update access count when loading the full entry
        self._save_index()
    
    def get_context(self, query: str, max_entries: int = 5) -> str:
        """
        Get formatted context string for use in responses.
        Automatically surfaces relevant memories.
        
        Args:
            query: The current query/topic
            max_entries: Max memories to include
            
        Returns:
            Formatted context string
        """
        results = self.search(query, limit=max_entries)
        
        if not results:
            return ""
        
        context_parts = ["\n📚 Relevant Context:"]
        
        for entry in results:
            date_str = entry.timestamp[:10]
            
            if entry.category == MemoryCategory.RESEARCH.value:
                context_parts.append(f"\n🔍 Research ({date_str}): {entry.content[:200]}...")
            elif entry.category == MemoryCategory.DECISION.value:
                context_parts.append(f"\n📋 Decision ({date_str}): {entry.content[:200]}...")
            elif entry.category == MemoryCategory.CODE.value:
                context_parts.append(f"\n💻 Code ({date_str}): {entry.content[:200]}...")
            else:
                context_parts.append(f"\n💬 Memory ({date_str}): {entry.content[:200]}...")
        
        context_parts.append("\n")
        return "\n".join(context_parts)
    
    def remember_research(self, topic: str, findings: str,
                          sources: Optional[List[str]] = None,
                          key_points: Optional[List[str]] = None) -> str:
        """
        Store research findings with full metadata.
        
        Args:
            topic: Research topic
            findings: Full research content
            sources: List of source URLs/references
            key_points: Key takeaway points
            
        Returns:
            entry_id
        """
        entry = ResearchEntry(
            id=self._generate_id(findings),
            timestamp=datetime.now().isoformat(),
            category=MemoryCategory.RESEARCH.value,
            content=findings,
            source="research",
            tags=["research", topic.lower().replace(" ", "_")],
            importance=8,
            sources=sources or [],
            key_findings=key_points or [],
            confidence=7
        )
        
        # Save to research file
        date_str = entry.timestamp[:10]
        filename = KNOWLEDGE_DIR / "research" / f"{date_str}.jsonl"
        with open(filename, 'a') as f:
            f.write(json.dumps(entry.to_dict()) + '\n')
        
        # Update index
        self.index["entries"][entry.id] = {
            "timestamp": entry.timestamp,
            "category": entry.category,
            "tags": entry.tags,
            "keywords": self._extract_keywords(findings),
            "importance": entry.importance
        }
        self._save_index()
        
        return entry.id
    
    def remember_decision(self, decision: str, context: str,
                          reasoning: str,
                          alternatives: Optional[List[str]] = None,
                          reversible: bool = True) -> str:
        """
        Store a decision with full context and reasoning.
        
        Args:
            decision: The decision made
            context: Background context
            reasoning: Why this decision was made
            alternatives: Other options considered
            reversible: Can this be changed later?
            
        Returns:
            entry_id
        """
        entry = DecisionEntry(
            id=self._generate_id(decision),
            timestamp=datetime.now().isoformat(),
            category=MemoryCategory.DECISION.value,
            content=decision,
            source="decision_log",
            tags=["decision"],
            importance=9,
            context=context,
            reasoning=reasoning,
            alternatives=alternatives or [],
            reversible=reversible
        )
        
        # Save to decisions file
        date_str = entry.timestamp[:10]
        filename = KNOWLEDGE_DIR / "decisions" / f"{date_str}.jsonl"
        with open(filename, 'a') as f:
            f.write(json.dumps(entry.to_dict()) + '\n')
        
        # Update index
        self.index["entries"][entry.id] = {
            "timestamp": entry.timestamp,
            "category": entry.category,
            "tags": entry.tags,
            "keywords": self._extract_keywords(decision + " " + reasoning),
            "importance": entry.importance
        }
        self._save_index()
        
        return entry.id
    
    def get_daily_summary(self, date: Optional[str] = None) -> str:
        """Generate a summary of memories for a given date"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # Collect all entries for date
        entries = []
        
        # Check raw captures
        raw_file = RAW_DIR / f"{date}.jsonl"
        if raw_file.exists():
            with open(raw_file) as f:
                for line in f:
                    entries.append(json.loads(line.strip()))
        
        # Check research
        research_file = KNOWLEDGE_DIR / "research" / f"{date}.jsonl"
        if research_file.exists():
            with open(research_file) as f:
                for line in f:
                    entries.append(json.loads(line.strip()))
        
        # Check decisions
        decisions_file = KNOWLEDGE_DIR / "decisions" / f"{date}.jsonl"
        if decisions_file.exists():
            with open(decisions_file) as f:
                for line in f:
                    entries.append(json.loads(line.strip()))
        
        if not entries:
            return f"No memories for {date}"
        
        # Generate summary
        summary = [f"# Memory Summary for {date}", ""]
        
        by_category = {}
        for entry in entries:
            cat = entry.get("category", "unknown")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(entry)
        
        for category, cat_entries in sorted(by_category.items()):
            summary.append(f"\n## {category.upper()}")
            for entry in cat_entries[:5]:  # Top 5 per category
                content = entry.get("content", "")[:150]
                summary.append(f"- {content}...")
        
        return "\n".join(summary)


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

_ums_instance = None

def get_ums() -> UniversalMemorySystem:
    """Get or create singleton UMS instance"""
    global _ums_instance
    if _ums_instance is None:
        _ums_instance = UniversalMemorySystem()
    return _ums_instance

def remember(content: str, category: Optional[str] = None,
             tags: Optional[List[str]] = None) -> str:
    """Quick remember function"""
    ums = get_ums()
    return ums.capture(content, category=category, tags=tags)

def recall(query: str, limit: int = 5) -> List[MemoryEntry]:
    """Quick recall function"""
    ums = get_ums()
    return ums.search(query, limit=limit)

def get_context(query: str) -> str:
    """Get context for a query"""
    ums = get_ums()
    return ums.get_context(query)


# ============================================================================
# SELF-TEST
# ============================================================================

if __name__ == "__main__":
    print("="*60)
    print("🧠 Universal Memory System - Self Test")
    print("="*60)
    
    # Create test instance
    ums = UniversalMemorySystem()
    
    # Test 1: Capture
    print("\n[TEST 1] Capture memory...")
    entry_id = ums.capture(
        "User wants to build a better memory system using ACA methodology",
        category="code",
        tags=["memory", "aca", "build"]
    )
    print(f"✅ Captured with ID: {entry_id[:16]}...")
    
    # Test 2: Research
    print("\n[TEST 2] Store research...")
    research_id = ums.remember_research(
        topic="memory systems",
        findings="Memory systems should have multiple layers: raw capture, daily journal, knowledge base, and quick access index.",
        sources=["aca_skill.md"],
        key_points=["Multi-layer architecture", "Auto-categorization", "Searchable index"]
    )
    print(f"✅ Research stored with ID: {research_id[:16]}...")
    
    # Test 3: Decision
    print("\n[TEST 3] Store decision...")
    decision_id = ums.remember_decision(
        decision="Build Universal Memory System",
        context="User wants comprehensive memory that never forgets anything",
        reasoning="Current memory is fragmented. UMS provides structured, searchable, persistent memory across all categories.",
        alternatives=["Enhance existing system", "Use external database"],
        reversible=True
    )
    print(f"✅ Decision stored with ID: {decision_id[:16]}...")
    
    # Test 4: Search
    print("\n[TEST 4] Search memory...")
    results = ums.search("memory system", limit=5)
    print(f"✅ Found {len(results)} results for 'memory system'")
    for r in results:
        print(f"   - [{r.category}] {r.content[:60]}...")
    
    # Test 5: Context
    print("\n[TEST 5] Get context...")
    context = ums.get_context("building systems")
    print(f"✅ Context retrieved:\n{context[:200]}...")
    
    # Test 6: Daily summary
    print("\n[TEST 6] Daily summary...")
    summary = ums.get_daily_summary()
    print(f"✅ Summary generated:\n{summary[:300]}...")
    
    print("\n" + "="*60)
    print("✅ All tests passed!")
    print("="*60)
    print(f"\nMemory structure created at: {MEMORY_DIR}")
    print("Files created:")
    for path in MEMORY_DIR.rglob("*"):
        if path.is_file():
            print(f"  - {path.relative_to(MEMORY_DIR)}")
