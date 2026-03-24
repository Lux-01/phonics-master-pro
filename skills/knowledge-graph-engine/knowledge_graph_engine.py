#!/usr/bin/env python3
"""
Knowledge Graph Engine v1.0
Builds relationship maps of concepts, entities, and dependencies

## ACA Plan:
1. Requirements: Parse files, extract entities and relationships → build graph
2. Architecture: EntityExtractor → RelationshipFinder → GraphBuilder → Visualizer
3. Data Flow: Parse sources → Extract entities → Find relations → Build graph
4. Edge Cases: No entities, circular deps, orphans, huge graphs
5. Tool Constraints: File read, JSON, graph data structures
6. Error Handling: File access, parse errors, cycle detection
7. Testing: Test with sample docs

Author: Autonomous Code Architect (ACA)
"""

import argparse
import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple

WORKSPACE_DIR = Path("/home/skux/.openclaw/workspace")
MEMORY_DIR = WORKSPACE_DIR / "memory"


@dataclass
class Entity:
    """A node in the knowledge graph"""
    id: str
    name: str
    entity_type: str  # skill, file, person, concept
    attributes: Dict = field(default_factory=dict)


@dataclass
class Relationship:
    """An edge in the knowledge graph"""
    source: str
    target: str
    relation_type: str  # depends_on, uses, related_to, contains
    weight: float = 1.0


class KnowledgeGraph:
    """In-memory knowledge graph"""
    
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.relationships: List[Relationship] = []
        self.adjacency: Dict[str, List[str]] = defaultdict(list)
    
    def add_entity(self, entity: Entity):
        self.entities[entity.id] = entity
    
    def add_relationship(self, rel: Relationship):
        self.relationships.append(rel)
        self.adjacency[rel.source].append(rel.target)
    
    def get_neighbors(self, entity_id: str) -> List[str]:
        return self.adjacency.get(entity_id, [])
    
    def find_dependencies(self, entity_id: str, visited: Set[str] = None) -> Set[str]:
        """Find all dependencies recursively"""
        if visited is None:
            visited = set()
        
        if entity_id in visited:
            return visited
        
        visited.add(entity_id)
        
        for neighbor in self.get_neighbors(entity_id):
            self.find_dependencies(neighbor, visited)
        
        return visited


class EntityExtractor:
    """Extract entities from files"""
    
    def extract_skills(self) -> List[Entity]:
        """Extract skills from directory"""
        entities = []
        skills_dir = WORKSPACE_DIR / "skills"
        
        for skill_dir in skills_dir.iterdir():
            if not skill_dir.is_dir() or skill_dir.name in ['dist', 'archive']:
                continue
            
            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists():
                content = skill_md.read_text()
                
                # Extract description
                desc_match = re.search(r'description:\s*(.+?)(?:\n|$)', content)
                description = desc_match.group(1) if desc_match else ""
                
                entities.append(Entity(
                    id=f"skill:{skill_dir.name}",
                    name=skill_dir.name,
                    entity_type="skill",
                    attributes={"description": description[:100]}
                ))
        
        return entities
    
    def extract_files(self) -> List[Entity]:
        """Extract important files"""
        entities = []
        
        important_files = [
            "MEMORY.md",
            "SOUL.md",
            "USER.md",
            "HEARTBEAT.md",
            "IDENTITY.md"
        ]
        
        for fname in important_files:
            fpath = WORKSPACE_DIR / fname
            if fpath.exists():
                entities.append(Entity(
                    id=f"file:{fname}",
                    name=fname,
                    entity_type="file"
                ))
        
        return entities
    
    def extract_concepts(self) -> List[Entity]:
        """Extract key concepts from memory"""
        entities = []
        concepts = [
            "LuxTrader",
            "ACA",
            "ALOE",
            "AOE",
            "Skylar",
            "Moltbook",
            "OpenClaw"
        ]
        
        for concept in concepts:
            entities.append(Entity(
                id=f"concept:{concept.lower()}",
                name=concept,
                entity_type="concept"
            ))
        
        return entities


class RelationshipFinder:
    """Find relationships between entities"""
    
    def find_skill_dependencies(self, entities: List[Entity]) -> List[Relationship]:
        """Find dependencies between skills"""
        relationships = []
        
        # Read skill dependencies from map
        map_file = WORKSPACE_DIR / "skill_dependency_map.json"
        if map_file.exists():
            with open(map_file) as f:
                data = json.load(f)
            
            for skill_id, deps in data.get("dependency_tree", {}).get("dependent_on", {}).items():
                for dep in deps:
                    relationships.append(Relationship(
                        source=f"skill:{skill_id}",
                        target=f"skill:{dep}",
                        relation_type="depends_on"
                    ))
        
        return relationships
    
    def find_skill_file_relationships(self, entities: List[Entity]) -> List[Relationship]:
        """Find which files reference skills"""
        relationships = []
        
        memory_md = WORKSPACE_DIR / "MEMORY.md"
        if memory_md.exists():
            content = memory_md.read_text()
            
            for entity in entities:
                if entity.entity_type == "skill" and entity.name in content:
                    relationships.append(Relationship(
                        source=f"file:MEMORY.md",
                        target=entity.id,
                        relation_type="references"
                    ))
        
        return relationships


class KnowledgeGraphEngine:
    def __init__(self):
        self.graph = KnowledgeGraph()
        self.extractor = EntityExtractor()
        self.relation_finder = RelationshipFinder()
    
    def build_graph(self) -> KnowledgeGraph:
        """Build complete knowledge graph"""
        # Extract entities
        entities = []
        entities.extend(self.extractor.extract_skills())
        entities.extend(self.extractor.extract_files())
        entities.extend(self.extractor.extract_concepts())
        
        # Add to graph
        for entity in entities:
            self.graph.add_entity(entity)
        
        # Find relationships
        rels = []
        rels.extend(self.relation_finder.find_skill_dependencies(entities))
        rels.extend(self.relation_finder.find_skill_file_relationships(entities))
        
        # Add to graph
        for rel in rels:
            self.graph.add_relationship(rel)
        
        return self.graph
    
    def generate_report(self) -> str:
        """Generate graph report"""
        report = []
        report.append("# Knowledge Graph Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("")
        
        report.append(f"## Statistics")
        report.append(f"- Total entities: {len(self.graph.entities)}")
        report.append(f"- Total relationships: {len(self.graph.relationships)}")
        report.append("")
        
        # Entities by type
        by_type = defaultdict(list)
        for entity in self.graph.entities.values():
            by_type[entity.entity_type].append(entity.name)
        
        report.append("## Entities by Type")
        for etype, names in sorted(by_type.items()):
            report.append(f"\n### {etype.title()} ({len(names)})")
            for name in sorted(names)[:10]:
                report.append(f"- {name}")
        
        report.append("")
        
        # Top connected entities
        report.append("## Most Connected")
        sorted_entities = sorted(
            self.graph.entities.values(),
            key=lambda e: len(self.graph.get_neighbors(e.id)),
            reverse=True
        )[:5]
        
        for entity in sorted_entities:
            neighbors = self.graph.get_neighbors(entity.id)
            report.append(f"- **{entity.name}**: {len(neighbors)} connections")
            for neighbor_id in neighbors[:3]:
                if neighbor_id in self.graph.entities:
                    report.append(f"  - → {self.graph.entities[neighbor_id].name}")
        
        return "\n".join(report)
    
    def export_json(self) -> str:
        """Export graph as JSON"""
        data = {
            "entities": [
                {"id": e.id, "name": e.name, "type": e.entity_type}
                for e in self.graph.entities.values()
            ],
            "relationships": [
                {"source": r.source, "target": r.target, "type": r.relation_type}
                for r in self.graph.relationships
            ]
        }
        return json.dumps(data, indent=2)
    
    def run(self) -> Dict:
        """Main execution"""
        # Ensure directories
        (MEMORY_DIR / "knowledge_graph").mkdir(parents=True, exist_ok=True)
        
        # Build graph
        self.build_graph()
        
        # Save JSON
        json_file = MEMORY_DIR / "knowledge_graph" / "graph.json"
        with open(json_file, "w") as f:
            f.write(self.export_json())
        
        # Generate report
        report = self.generate_report()
        report_file = MEMORY_DIR / "knowledge_graph" / "report.md"
        with open(report_file, "w") as f:
            f.write(report)
        
        return {
            "success": True,
            "entities": len(self.graph.entities),
            "relationships": len(self.graph.relationships),
            "graph_file": str(json_file),
            "report": str(report_file)
        }


def main():
    parser = argparse.ArgumentParser(description="Knowledge Graph Engine")
    args = parser.parse_args()
    
    engine = KnowledgeGraphEngine()
    result = engine.run()
    
    if result.get("success"):
        print(f"✓ Knowledge graph built")
        print(f"  Entities: {result['entities']}")
        print(f"  Relationships: {result['relationships']}")
    else:
        print(f"✗ Error")


if __name__ == "__main__":
    main()
