#!/usr/bin/env python3
"""
Knowledge Graph Engine (KGE)
Build a map of everything known. Organize concepts, entities, relationships.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field

# Paths
KGE_DIR = Path("/home/skux/.openclaw/workspace/skills/knowledge-graph-engine")
DATA_DIR = KGE_DIR / "data"
ENTITIES_DIR = DATA_DIR / "entities"
RELATIONS_DIR = DATA_DIR / "relationships"
QUERIES_DIR = DATA_DIR / "queries"

for d in [KGE_DIR, DATA_DIR, ENTITIES_DIR, RELATIONS_DIR, QUERIES_DIR]:
    d.mkdir(parents=True, exist_ok=True)


@dataclass
class Entity:
    id: str
    type: str
    name: str
    aliases: List[str] = field(default_factory=list)
    properties: Dict = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    created: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "aliases": self.aliases,
            "properties": self.properties,
            "tags": self.tags,
            "created": self.created
        }


@dataclass
class Relationship:
    id: str
    type: str
    from_entity: str
    to_entity: str
    properties: Dict = field(default_factory=dict)
    created: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type,
            "from": self.from_entity,
            "to": self.to_entity,
            "properties": self.properties,
            "created": self.created
        }


class KnowledgeGraphEngine:
    """
    Build and query knowledge graphs.
    """
    
    def __init__(self):
        self.data_dir = DATA_DIR
        self.entities_dir = ENTITIES_DIR
        self.relations_dir = RELATIONS_DIR
        self.queries_dir = QUERIES_DIR
        
        self.entities: Dict[str, Entity] = {}
        self.relationships: Dict[str, Relationship] = {}
        
        self._load_graph()
        self._initialize_bootstrap_entities()
    
    def _initialize_bootstrap_entities(self):
        """Initialize with bootstrap knowledge."""
        
        # Check if already initialized
        if self.entities:
            return
        
        # Add bootstrap entities
        bootstrap = [
            {"type": "project", "name": "Crypto Scanner v5.4", "tags": ["scanner", "solana", "trading"]},
            {"type": "project", "name": "Crypto Scanner v5.5", "tags": ["scanner", "solana", "charts"]},
            {"type": "project", "name": "LuxTrader", "tags": ["trading", "automation"]},
            {"type": "project", "name": "Holy Trinity", "tags": ["trading", "multi-strategy"]},
            {"type": "skill", "name": "Pattern Extractor", "tags": ["learning", "patterns"]},
            {"type": "skill", "name": "Outcome Tracker", "tags": ["tracking", "outcomes"]},
            {"type": "skill", "name": "ALOE", "tags": ["learning", "reflection"]},
            {"type": "skill", "name": "Scanner Architect", "tags": ["planning", "code"]},
            {"type": "skill", "name": "Skill Evolution Engine", "tags": ["audit", "evolution"]},
            {"type": "skill", "name": "ATS", "tags": ["analysis", "trading"]},
            {"type": "skill", "name": "AOE", "tags": ["opportunities", "scanning"]},
            {"type": "skill", "name": "MAC", "tags": ["coordination", "agents"]},
            {"type": "person", "name": "Tem", "tags": ["user", "trader"]},
            {"type": "person", "name": "Lux", "tags": ["assistant", "ai"]},
            {"type": "technology", "name": "Solana", "tags": ["blockchain", "layer1"]},
            {"type": "technology", "name": "Python", "tags": ["language", "programming"]},
            {"type": "concept", "name": "Mean Reversion", "tags": ["strategy", "trading"]},
            {"type": "concept", "name": "Pattern Recognition", "tags": ["ml", "trading"]},
        ]
        
        for item in bootstrap:
            self.add_entity(
                entity_type=item["type"],
                name=item["name"],
                tags=item["tags"]
            )
        
        # Add relationships
        self.add_relationship("uses", "Crypto Scanner v5.4", "Solana")
        self.add_relationship("uses", "Crypto Scanner v5.5", "Solana")
        self.add_relationship("implements", "Crypto Scanner v5.4", "Pattern Recognition")
        self.add_relationship("implements", "LuxTrader", "Mean Reversion")
        self.add_relationship("created_by", "Crypto Scanner v5.4", "Lux")
        self.add_relationship("interests", "Tem", "Trading")
        
        self._save_graph()
    
    def add_entity(self, entity_type: str, name: str, 
                   aliases: List[str] = None,
                   properties: Dict = None,
                   tags: List[str] = None) -> Entity:
        """Add an entity to the graph."""
        
        entity_id = f"ENT-{name.replace(' ', '_').lower()}"
        
        entity = Entity(
            id=entity_id,
            type=entity_type,
            name=name,
            aliases=aliases or [],
            properties=properties or {},
            tags=tags or []
        )
        
        self.entities[entity_id] = entity
        self._save_entity(entity)
        
        return entity
    
    def add_relationship(self, rel_type: str, from_name: str, to_name: str,
                        properties: Dict = None) -> Optional[Relationship]:
        """Add a relationship between entities."""
        
        # Find entities by name
        from_entity = self._find_entity_by_name(from_name)
        to_entity = self._find_entity_by_name(to_name)
        
        if not from_entity or not to_entity:
            return None
        
        rel_id = f"REL-{from_entity.id}-{rel_type}-{to_entity.id}"
        
        rel = Relationship(
            id=rel_id,
            type=rel_type,
            from_entity=from_entity.id,
            to_entity=to_entity.id,
            properties=properties or {}
        )
        
        self.relationships[rel_id] = rel
        self._save_relationship(rel)
        
        return rel
    
    def _find_entity_by_name(self, name: str) -> Optional[Entity]:
        """Find entity by name or alias."""
        
        for entity in self.entities.values():
            if entity.name.lower() == name.lower():
                return entity
            if name.lower() in [a.lower() for a in entity.aliases]:
                return entity
        
        return None
    
    def find_entity(self, query: str) -> List[Entity]:
        """Find entities matching query."""
        
        results = []
        query_lower = query.lower()
        
        for entity in self.entities.values():
            # Match by name
            if query_lower in entity.name.lower():
                results.append(entity)
                continue
            
            # Match by alias
            if any(query_lower in a.lower() for a in entity.aliases):
                results.append(entity)
                continue
            
            # Match by tag
            if any(query_lower in t.lower() for t in entity.tags):
                results.append(entity)
                continue
        
        return results
    
    def get_related(self, entity_name: str, relation_type: str = None) -> List[Dict]:
        """Get entities related to a given entity."""
        
        entity = self._find_entity_by_name(entity_name)
        if not entity:
            return []
        
        related = []
        
        for rel in self.relationships.values():
            if rel.from_entity == entity.id:
                # Outgoing relationship
                if relation_type is None or rel.type == relation_type:
                    to_entity = self.entities.get(rel.to_entity)
                    if to_entity:
                        related.append({
                            "relationship": rel.type,
                            "direction": "outgoing",
                            "entity": to_entity.to_dict(),
                            "properties": rel.properties
                        })
            
            elif rel.to_entity == entity.id:
                # Incoming relationship
                if relation_type is None or rel.type == relation_type:
                    from_entity = self.entities.get(rel.from_entity)
                    if from_entity:
                        related.append({
                            "relationship": rel.type,
                            "direction": "incoming",
                            "entity": from_entity.to_dict(),
                            "properties": rel.properties
                        })
        
        return related
    
    def query(self, query_type: str, **params) -> List[Dict]:
        """Execute a query on the graph."""
        
        if query_type == "find_by_type":
            entity_type = params.get("type")
            return [e.to_dict() for e in self.entities.values() if e.type == entity_type]
        
        elif query_type == "find_by_tag":
            tag = params.get("tag")
            return [e.to_dict() for e in self.entities.values() if tag in e.tags]
        
        elif query_type == "connections":
            entity_name = params.get("entity")
            return self.get_related(entity_name)
        
        elif query_type == "similar":
            entity_name = params.get("entity")
            entity = self._find_entity_by_name(entity_name)
            if not entity:
                return []
            
            # Find similar by shared tags
            similar = []
            for other in self.entities.values():
                if other.id != entity.id:
                    shared_tags = set(entity.tags) & set(other.tags)
                    if shared_tags:
                        similar.append({
                            "entity": other.to_dict(),
                            "shared_tags": list(shared_tags),
                            "similarity": len(shared_tags) / max(len(entity.tags), len(other.tags))
                        })
            
            return sorted(similar, key=lambda x: x["similarity"], reverse=True)
        
        elif query_type == "path":
            from_name = params.get("from")
            to_name = params.get("to")
            # Simple path finding - direct connections
            from_entity = self._find_entity_by_name(from_name)
            to_entity = self._find_entity_by_name(to_name)
            
            if not from_entity or not to_entity:
                return []
            
            # Find direct connections
            for rel in self.relationships.values():
                if (rel.from_entity == from_entity.id and rel.to_entity == to_entity.id) or \
                   (rel.to_entity == from_entity.id and rel.from_entity == to_entity.id):
                    return [{"path": f"{from_name} --{rel.type}--> {to_name}"}]
            
            return []
        
        return []
    
    def infer(self, entity_name: str) -> List[Dict]:
        """Infer new knowledge about an entity."""
        
        entity = self._find_entity_by_name(entity_name)
        if not entity:
            return []
        
        inferences = []
        
        # Inference 1: Similar projects use similar technologies
        if entity.type == "project":
            similar = self.query("similar", entity=entity_name)
            for sim in similar[:3]:
                similar_entity = sim.get("entity", {})
                similar_name = similar_entity.get("name")
                
                # What technologies does similar project use?
                similar_tech = self.get_related(similar_name, "uses")
                current_tech = self.get_related(entity_name, "uses")
                current_tech_names = [t.get("entity", {}).get("name") for t in current_tech]
                
                for tech in similar_tech:
                    tech_name = tech.get("entity", {}).get("name")
                    if tech_name not in current_tech_names:
                        inferences.append({
                            "type": "might_use",
                            "reasoning": f"{similar_name} uses {tech_name}, and projects are similar",
                            "confidence": sim.get("similarity", 0) * 0.7
                        })
        
        # Inference 2: Projects with trading tag likely implement strategies
        if "trading" in entity.tags and entity.type == "project":
            strategies = self.query("find_by_tag", tag="strategy")
            for strategy in strategies[:3]:
                inferences.append({
                    "type": "might_implement",
                    "reasoning": f"Trading projects often implement strategies",
                    "target": strategy.get("name"),
                    "confidence": 0.6
                })
        
        return inferences
    
    def visualize(self, entity_name: str = None, depth: int = 1) -> str:
        """Create text visualization of graph."""
        
        if entity_name:
            entity = self._find_entity_by_name(entity_name)
            if not entity:
                return f"Entity '{entity_name}' not found"
            
            lines = [f"\n{entity.name} ({entity.type})"]
            lines.append("=" * 40)
            
            if entity.properties:
                lines.append("Properties:")
                for k, v in entity.properties.items():
                    lines.append(f"  {k}: {v}")
            
            related = self.get_related(entity_name)
            if related:
                lines.append("\nConnections:")
                for rel in related:
                    direction = "←" if rel["direction"] == "incoming" else "→"
                    other = rel["entity"]["name"]
                    rel_type = rel["relationship"]
                    lines.append(f"  {direction} {rel_type} → {other}")
            
            return "\n".join(lines)
        
        else:
            # Summary view
            lines = ["\nKnowledge Graph Summary"]
            lines.append("=" * 40)
            lines.append(f"Entities: {len(self.entities)}")
            lines.append(f"Relationships: {len(self.relationships)}")
            
            # Count by type
            by_type = {}
            for e in self.entities.values():
                by_type[e.type] = by_type.get(e.type, 0) + 1
            
            lines.append("\nBy Type:")
            for t, count in sorted(by_type.items()):
                lines.append(f"  {t}: {count}")
            
            return "\n".join(lines)
    
    def _save_entity(self, entity: Entity):
        """Save entity to disk."""
        entity_file = self.entities_dir / f"{entity.id}.json"
        with open(entity_file, 'w') as f:
            json.dump(entity.to_dict(), f, indent=2)
    
    def _save_relationship(self, rel: Relationship):
        """Save relationship to disk."""
        rel_file = self.relations_dir / f"{rel.id}.json"
        with open(rel_file, 'w') as f:
            json.dump(rel.to_dict(), f, indent=2)
    
    def _save_graph(self):
        """Save entire graph."""
        for entity in self.entities.values():
            self._save_entity(entity)
        for rel in self.relationships.values():
            self._save_relationship(rel)
    
    def _load_graph(self):
        """Load graph from disk."""
        
        # Load entities
        for entity_file in self.entities_dir.glob("ENT-*.json"):
            try:
                with open(entity_file) as f:
                    data = json.load(f)
                entity = Entity(**{k: v for k, v in data.items()})
                self.entities[entity.id] = entity
            except:
                pass
        
        # Load relationships
        for rel_file in self.relations_dir.glob("REL-*.json"):
            try:
                with open(rel_file) as f:
                    data = json.load(f)
                rel = Relationship(
                    id=data["id"],
                    type=data["type"],
                    from_entity=data["from"],
                    to_entity=data["to"],
                    properties=data.get("properties", {}),
                    created=data.get("created", datetime.now().isoformat())
                )
                self.relationships[rel.id] = rel
            except:
                pass
    
    def get_stats(self) -> Dict:
        """Get graph statistics."""
        
        by_type = {}
        for e in self.entities.values():
            by_type[e.type] = by_type.get(e.type, 0) + 1
        
        by_relation = {}
        for r in self.relationships.values():
            by_relation[r.type] = by_relation.get(r.type, 0) + 1
        
        return {
            "entities": len(self.entities),
            "relationships": len(self.relationships),
            "by_type": by_type,
            "by_relation": by_relation
        }


# Global instance
kge = KnowledgeGraphEngine()


def add_entity(entity_type: str, name: str, **kwargs) -> Entity:
    """Quick add entity function."""
    return kge.add_entity(entity_type, name, **kwargs)


def add_relationship(rel_type: str, from_name: str, to_name: str, **kwargs) -> Relationship:
    """Quick add relationship function."""
    return kge.add_relationship(rel_type, from_name, to_name, **kwargs)


def find(query: str) -> List[Entity]:
    """Quick find function."""
    return kge.find_entity(query)


def query(query_type: str, **params) -> List[Dict]:
    """Quick query function."""
    return kge.query(query_type, **params)


def visualize(entity: str = None) -> str:
    """Quick visualize function."""
    return kge.visualize(entity)


def get_stats() -> Dict:
    """Quick stats function."""
    return kge.get_stats()


if __name__ == "__main__":
    print("🧠 Knowledge Graph Engine (KGE)")
    print("=" * 60)
    
    # Show graph summary
    print(visualize())
    
    # Query examples
    print("\n📊 Query Examples:")
    
    # Find by type
    print("\n1. Projects:")
    projects = query("find_by_type", type="project")
    for p in projects[:3]:
        print(f"   • {p['name']}")
    
    # Find by tag
    print("\n2. Entities with 'trading' tag:")
    trading = query("find_by_tag", tag="trading")
    for e in trading[:3]:
        print(f"   • {e['name']} ({e['type']})")
    
    # Connections
    print("\n3. Connections to 'Crypto Scanner v5.4':")
    connections = query("connections", entity="Crypto Scanner v5.4")
    for c in connections:
        icon = "←" if c['direction'] == 'incoming' else "→"
        print(f"   {icon} {c['relationship']} → {c['entity']['name']}")
    
    # Similar
    print("\n4. Similar to 'Crypto Scanner v5.4':")
    similar = query("similar", entity="Crypto Scanner v5.4")
    for s in similar[:3]:
        print(f"   • {s['entity']['name']} (similarity: {s['similarity']:.1%})")
    
    # Visualization
    print("\n" + visualize("Crypto Scanner v5.4"))
    
    # Stats
    print(f"\n📈 Stats: {json.dumps(get_stats(), indent=2)}")
    
    print(f"\n🧠 KGE ready for knowledge mapping!")
