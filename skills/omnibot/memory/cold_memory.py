"""
Cold Memory - Curated long-term storage.
Important memories preserved indefinitely.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import json
import re

class ColdMemory:
    """
    Long-term curated memory storage.
    Carefully selected important information.
    """
    
    def __init__(self, memory_file: Path):
        self.memory_file = Path(memory_file)
        self.critical_file = self.memory_file.parent / "critical_info.json"
        self.cache = None
        self._load_cache()
    
    def store(self, content: str, tags: Optional[List[str]] = None,
              section: Optional[str] = None) -> str:
        """
        Store information in cold memory (MEMORY.md).
        
        Args:
            content: Important information to store
            tags: Tags for categorization
            section: Optional section to store under
            
        Returns:
            Memory reference ID
        """
        mem_id = f"cold_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        entry = {
            "id": mem_id,
            "content": content,
            "tags": tags or [],
            "section": section or "General",
            "created_at": datetime.now().isoformat(),
            "tier": "cold"
        }
        
        # Append to MEMORY.md
        self._append_to_memory_file(entry)
        
        # Also update critical_info.json for structured access
        self._update_critical_info(entry)
        
        return mem_id
    
    def search(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search cold memory.
        
        Args:
            query: Search query
            max_results: Maximum results
            
        Returns:
            List of matching memories
        """
        results = []
        query_lower = query.lower()
        
        # Search MEMORY.md
        if self.memory_file.exists():
            content = self.memory_file.read_text()
            
            # Parse by sections
            sections = self._parse_memory_md(content)
            
            for section_name, section_content in sections.items():
                score = 0
                
                # Section name match
                if query_lower in section_name.lower():
                    score += 15
                
                # Content match
                if query_lower in section_content.lower():
                    score += 10
                
                if score > 0:
                    results.append({
                        "id": f"md_{section_name.replace(' ', '_')}",
                        "section": section_name,
                        "content": section_content[:500],  # Preview
                        "tags": self._extract_tags(section_content),
                        "relevance": score,
                        "tier": "cold"
                    })
        
        # Search critical_info.json
        if self.critical_file.exists():
            try:
                with open(self.critical_file, 'r') as f:
                    critical = json.load(f)
                    
                for key, value in critical.items():
                    score = 0
                    
                    if query_lower in key.lower():
                        score += 20
                    
                    value_str = str(value)
                    if query_lower in value_str.lower():
                        score += 8
                    
                    if score > 0:
                        results.append({
                            "id": f"json_{key}",
                            "section": "Critical Info",
                            "content": f"{key}: {value_str[:200]}",
                            "tags": ["critical", "structured"],
                            "relevance": score,
                            "tier": "cold"
                        })
            except Exception:
                pass
        
        # Sort by relevance
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results[:max_results]
    
    def get_section(self, section_name: str) -> Optional[str]:
        """Get a specific section from MEMORY.md."""
        if not self.memory_file.exists():
            return None
        
        content = self.memory_file.read_text()
        sections = self._parse_memory_md(content)
        
        # Fuzzy match section names
        for name, content in sections.items():
            if section_name.lower() in name.lower() or name.lower() in section_name.lower():
                return content
        
        return None
    
    def get_critical_info(self, key: Optional[str] = None) -> Any:
        """Get critical information from structured storage."""
        if not self.critical_file.exists():
            return None if key else {}
        
        try:
            with open(self.critical_file, 'r') as f:
                data = json.load(f)
            
            if key:
                return data.get(key)
            return data
        except Exception:
            return None if key else {}
    
    def update_critical(self, key: str, value: Any) -> bool:
        """Update a critical info entry."""
        try:
            data = self.get_critical_info() or {}
            data[key] = value
            data[f"{key}_updated_at"] = datetime.now().isoformat()
            
            self.critical_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.critical_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception:
            return False
    
    def _load_cache(self):
        """Load memory into cache for fast access."""
        self.cache = {
            "memory_md": {},
            "critical_info": {}
        }
        
        if self.memory_file.exists():
            content = self.memory_file.read_text()
            self.cache["memory_md"] = self._parse_memory_md(content)
        
        if self.critical_file.exists():
            try:
                with open(self.critical_file, 'r') as f:
                    self.cache["critical_info"] = json.load(f)
            except Exception:
                pass
    
    def _parse_memory_md(self, content: str) -> Dict[str, str]:
        """Parse MEMORY.md into sections."""
        sections = {}
        current_section = "General"
        current_content = []
        
        for line in content.split('\n'):
            # Header detection
            if line.startswith('# ') or line.startswith('## '):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = line.lstrip('# ').strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _append_to_memory_file(self, entry: Dict):
        """Append entry to MEMORY.md."""
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        section = entry.get("section", "General")
        content = entry["content"]
        tags = ', '.join(entry.get("tags", []))
        
        entry_text = f"\n\n---\n**[{timestamp}]** ({section})\n\n{content}"
        if tags:
            entry_text += f"\n\n*Tags: {tags}*"
        entry_text += "\n"
        
        with open(self.memory_file, 'a') as f:
            f.write(entry_text)
    
    def _update_critical_info(self, entry: Dict):
        """Update critical_info.json."""
        data = self.get_critical_info() or {}
        
        # Add to entries list
        if "entries" not in data:
            data["entries"] = []
        
        data["entries"].append({
            "id": entry["id"],
            "content": entry["content"],
            "tags": entry.get("tags", []),
            "section": entry.get("section", "General"),
            "created_at": entry["created_at"]
        })
        
        self.critical_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.critical_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extract tags from content."""
        # Look for common patterns
        tags = []
        
        # *Tags: tag1, tag2*
        tag_match = re.search(r'\*Tags?:\s*([^*]+)\*', content)
        if tag_match:
            tags.extend(t.strip() for t in tag_match.group(1).split(','))
        
        return tags
    
    def get_stats(self) -> Dict:
        """Get cold memory statistics."""
        sections = 0
        if self.memory_file.exists():
            content = self.memory_file.read_text()
            sections = len(self._parse_memory_md(content))
        
        critical_entries = 0
        if self.critical_file.exists():
            try:
                with open(self.critical_file, 'r') as f:
                    data = json.load(f)
                critical_entries = len(data.get("entries", []))
            except Exception:
                pass
        
        return {
            "memory_file_exists": self.memory_file.exists(),
            "sections": sections,
            "critical_entries": critical_entries,
            "tier": "cold (long-term curated)"
        }