#!/usr/bin/env python3
"""
Universal Memory System - Semantic Search Module
Cross-tier memory recall with relevance scoring
"""

import re
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from collections import Counter


class SemanticSearch:
    """
    Semantic search across memory tiers.
    
    Features:
    - Multi-strategy search (exact, fuzzy, keyword, semantic)
    - Relevance scoring
    - Cross-tier ranking
    - Query expansion
    """
    
    def __init__(self, short_term=None, long_term=None):
        self.short_term = short_term
        self.long_term = long_term
        
        # Stop words for keyword extraction
        self.stop_words = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'shall',
            'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in',
            'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into',
            'through', 'during', 'before', 'after', 'above', 'below',
            'between', 'among', 'under', 'over', 'again', 'further',
            'then', 'once', 'here', 'there', 'when', 'where', 'why',
            'how', 'all', 'each', 'few', 'more', 'most', 'other',
            'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
            'so', 'than', 'too', 'very', 'just', 'and', 'but', 'if',
            'or', 'because', 'as', 'until', 'while', 'this', 'that',
            'these', 'those', 'i', 'me', 'my', 'myself', 'we', 'our',
            'you', 'your', 'he', 'him', 'his', 'she', 'her', 'it',
            'its', 'they', 'them', 'their', 'what', 'which', 'who',
            'whom', 'whose', 'we', 'us', 'our', 'ours'
        }
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract meaningful keywords from text"""
        # Normalize
        text = text.lower()
        
        # Extract words (4+ chars)
        words = re.findall(r'\b[a-z]{4,}\b', text)
        
        # Filter stop words
        words = [w for w in words if w not in self.stop_words]
        
        # Return most frequent
        counter = Counter(words)
        return [w for w, _ in counter.most_common(max_keywords)]
    
    def expand_query(self, query: str) -> List[str]:
        """Expand query with related terms"""
        expansions = {
            'trading': ['trade', 'buy', 'sell', 'position'],
            'bot': ['automate', 'script', 'system'],
            'memory': ['remember', 'store', 'recall'],
            'project': ['app', 'build', 'develop'],
            'money': ['profit', 'revenue', 'income', 'cost'],
            'api': ['key', 'token', 'credential'],
            'code': ['python', 'script', 'function'],
            'decision': ['decided', 'chose', 'concluded']
        }
        
        query_lower = query.lower()
        expanded = [query]
        
        for term, related in expansions.items():
            if term in query_lower:
                expanded.extend(related)
        
        return list(set(expanded))
    
    def calculate_relevance(self, query: str, content: str,
                          importance: int = 5,
                          age_days: int = 0,
                          access_count: int = 0) -> float:
        """
        Calculate relevance score for ranking.
        
        Scoring factors:
        - Keyword overlap (40%)
        - Recency bonus (20%)
        - Importance weight (25%)
        - Access frequency (15%)
        """
        score = 0.0
        
        # Keyword overlap
        query_words = set(self.extract_keywords(query))
        content_words = set(self.extract_keywords(content))
        
        if query_words:
            overlap = len(query_words & content_words) / len(query_words)
            score += overlap * 40
        
        # Exact match bonus
        if query.lower() in content.lower():
            score += 20
        
        # Recency bonus (exponential decay)
        if age_days < 7:
            score += 20 * (1 - (age_days / 7))
        elif age_days < 30:
            score += 5 * (1 - (age_days / 30))
        
        # Importance weight
        score += (importance / 10) * 25
        
        # Access frequency (popularity)
        score += min(access_count * 2, 15)
        
        return score
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Full semantic search across all memory tiers.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of results with relevance scores
        """
        results = []
        
        # Search short-term memory
        if self.short_term:
            stm_results = self.short_term.search(query, limit=limit)
            for entry in stm_results:
                age = (datetime.now() - entry.timestamp).days
                relevance = self.calculate_relevance(
                    query, entry.content, entry.importance, age, 0
                )
                results.append({
                    'tier': 'short_term',
                    'relevance': relevance,
                    'content': entry.content,
                    'timestamp': entry.timestamp.isoformat(),
                    'source': entry.source,
                    'id': entry.id
                })
        
        # Search long-term memory
        if self.long_term:
            ltm_results = self.long_term.search(query, limit=limit)
            for entry in ltm_results:
                try:
                    entry_date = datetime.fromisoformat(entry.timestamp)
                    age = (datetime.now() - entry_date).days
                except:
                    age = 30
                
                relevance = self.calculate_relevance(
                    query, entry.content, entry.importance, age, entry.access_count
                )
                results.append({
                    'tier': 'long_term',
                    'relevance': relevance,
                    'content': entry.content,
                    'timestamp': entry.timestamp,
                    'source': entry.source,
                    'category': entry.category,
                    'id': entry.id
                })
        
        # Sort by relevance
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results[:limit]
    
    def find_related(self, entry_id: str, limit: int = 5) -> List[Dict]:
        """Find memories related to a given entry"""
        # This would use content similarity
        # For now, return recent entries
        if self.long_term:
            results = self.long_term.search("", limit=limit)
            return [
                {
                    'id': r.id,
                    'content': r.content[:100],
                    'category': r.category
                }
                for r in results
            ]
        return []
    
    def format_results(self, results: List[Dict], include_scores: bool = False) -> str:
        """Format search results for display"""
        if not results:
            return "No relevant memories found."
        
        lines = [f"\n📚 Found {len(results)} relevant memories:", ""]
        
        for i, r in enumerate(results, 1):
            tier_icon = "🔥" if r['tier'] == 'short_term' else "❄️"
            content = r['content'][:100] + "..." if len(r['content']) > 100 else r['content']
            
            if include_scores:
                lines.append(f"{tier_icon} [{i}] (score: {r['relevance']:.1f}) {content}")
            else:
                lines.append(f"{tier_icon} [{i}] {content}")
        
        return "\n".join(lines)


if __name__ == "__main__":
    search = SemanticSearch()
    
    # Test keyword extraction
    text = "I need to remember all the trading strategies we discussed"
    keywords = search.extract_keywords(text)
    print(f"Keywords from '{text}':", keywords)
    
    # Test query expansion
    expanded = search.expand_query("trading bot")
    print(f"\nExpanded 'trading bot':", expanded)
    
    # Test relevance scoring
    score = search.calculate_relevance(
        "trading bot",
        "We built a trading bot for Solana",
        importance=8,
        age_days=2,
        access_count=3
    )
    print(f"\nRelevance score: {score:.1f}")