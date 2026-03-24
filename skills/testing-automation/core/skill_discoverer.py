#!/usr/bin/env python3
"""
Skill Discoverer Module
Finds and catalogs all skills in the workspace.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class SkillInfo:
    """Information about a discovered skill"""
    name: str
    path: Path
    has_skill_md: bool
    has_init_py: bool
    has_tests: bool
    is_python: bool
    files: List[str]
    size_kb: int


class SkillDiscoverer:
    """
    Discovers and catalogs skills in the workspace.
    
    Features:
    - Auto-discovers all skill directories
    - Categorizes by type
    - Tracks dependencies
    - Validates structure
    """
    
    def __init__(self, skills_dir: str = None):
        self.skills_dir = Path(skills_dir) if skills_dir else Path.home() / ".openclaw/workspace/skills"
        self.discovered: List[SkillInfo] = []
        self.errors: List[str] = []
    
    def discover_all(self) -> List[SkillInfo]:
        """
        Discover all skills in the skills directory.
        
        Returns:
            List of SkillInfo objects
        """
        self.discovered = []
        
        if not self.skills_dir.exists():
            self.errors.append(f"Skills directory not found: {self.skills_dir}")
            return []
        
        for item in self.skills_dir.iterdir():
            if not item.is_dir():
                continue
            
            # Skip archived/non-skills
            if item.name.startswith('.') or item.name == 'dist':
                continue
            
            # Check if it's a skill (has SKILL.md or typical structure)
            skill_info = self._analyze_skill(item)
            if skill_info:
                self.discovered.append(skill_info)
        
        # Sort by name
        self.discovered.sort(key=lambda x: x.name)
        return self.discovered
    
    def _analyze_skill(self, skill_path: Path) -> Optional[SkillInfo]:
        """Analyze a single skill directory"""
        try:
            files = []
            total_size = 0
            py_files = 0
            
            for file in skill_path.rglob('*'):
                if file.is_file():
                    files.append(str(file.relative_to(skill_path)))
                    try:
                        total_size += file.stat().st_size
                        if file.suffix == '.py':
                            py_files += 1
                    except:
                        pass
            
            # Skip if no files
            if not files:
                return None
            
            # Check for standard files
            has_skill_md = (skill_path / "SKILL.md").exists()
            has_init_py = (skill_path / "__init__.py").exists()
            has_tests = (skill_path / "tests").is_dir() or (skill_path / "test").is_dir()
            
            return SkillInfo(
                name=skill_path.name,
                path=skill_path,
                has_skill_md=has_skill_md,
                has_init_py=has_init_py,
                has_tests=has_tests,
                is_python=py_files > 0,
                files=files,
                size_kb=total_size // 1024
            )
        
        except Exception as e:
            self.errors.append(f"Error analyzing {skill_path}: {e}")
            return None
    
    def get_by_name(self, name: str) -> Optional[SkillInfo]:
        """Get a specific skill by name"""
        for skill in self.discovered:
            if skill.name == name:
                return skill
        return None
    
    def get_python_skills(self) -> List[SkillInfo]:
        """Get only Python skills"""
        return [s for s in self.discovered if s.is_python]
    
    def get_with_tests(self) -> List[SkillInfo]:
        """Get skills with test directories"""
        return [s for s in self.discovered if s.has_tests]
    
    def get_incomplete(self) -> List[SkillInfo]:
        """Get skills missing STANDARD.md"""
        return [s for s in self.discovered if not s.has_skill_md]
    
    def generate_summary(self) -> Dict:
        """Generate summary statistics"""
        total = len(self.discovered)
        python_skills = len(self.get_python_skills())
        with_tests = len(self.get_with_tests())
        incomplete = len(self.get_incomplete())
        
        total_size = sum(s.size_kb for s in self.discovered)
        
        return {
            'total_skills': total,
            'python_skills': python_skills,
            'with_tests': with_tests,
            'incomplete': incomplete,
            'total_size_kb': total_size,
            'average_size_kb': total_size // total if total > 0 else 0,
            'errors': self.errors
        }
    
    def export_json(self, output_path: str = None) -> str:
        """Export discovery results to JSON"""
        data = {
            'skills': [
                {
                    'name': s.name,
                    'path': str(s.path),
                    'has_skill_md': s.has_skill_md,
                    'has_init_py': s.has_init_py,
                    'has_tests': s.has_tests,
                    'is_python': s.is_python,
                    'file_count': len(s.files),
                    'size_kb': s.size_kb
                }
                for s in self.discovered
            ],
            'summary': self.generate_summary()
        }
        
        if output_path is None:
            output_path = self.skills_dir.parent / "skill_inventory.json"
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return str(output_path)


def main():
    """CLI for skill discovery"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Discover OpenClaw skills')
    parser.add_argument('--json', action='store_true', help='Export to JSON')
    parser.add_argument('--path', type=str, help='Custom skills directory')
    
    args = parser.parse_args()
    
    print("🔍 Skill Discoverer")
    print("=" * 60)
    
    discoverer = SkillDiscoverer(args.path)
    skills = discoverer.discover_all()
    
    print(f"\nFound {len(skills)} skills:")
    print("-" * 60)
    
    for skill in skills:
        status = ""
        if not skill.has_skill_md:
            status += " 📄"
        if not skill.has_init_py and skill.is_python:
            status += " 🐍"
        if skill.has_tests:
            status += " ✅"
        
        print(f"  {skill.name:30s} {len(skill.files):3d} files {skill.size_kb:5d}KB{status}")
    
    summary = discoverer.generate_summary()
    print(f"\n{'=' * 60}")
    print(f"Summary: {summary['total_skills']} skills, {summary['total_size_kb']}KB")
    print(f"         {summary['python_skills']} Python, {summary['with_tests']} with tests")
    
    if summary['incomplete'] > 0:
        print(f"⚠️  {summary['incomplete']} skills missing SKILL.md")
    
    if args.json:
        path = discoverer.export_json()
        print(f"\n📄 Exported to: {path}")


if __name__ == "__main__":
    main()