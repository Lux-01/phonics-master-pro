#!/usr/bin/env python3
"""
Skill Dependency Map Generator
Creates a map of skill interdependencies

ACA Methodology:
1. Requirements: Map all skill dependencies
2. Architecture: Analysis-based graph
3. Data Flow: Parse SKILL.md files
4. Edge Cases: Missing references, circular deps
5. Tool Constraints: Python standard lib only
6. Error Handling: Graceful skip of invalid skills
7. Testing: Verify output completeness
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

SKILLS_DIR = "/home/skux/.openclaw/workspace/skills"
OUTPUT_FILE = "/home/skux/.openclaw/workspace/skill_dependency_map.json"

def extract_skill_info(skill_path):
    """Extract skill metadata from SKILL.md"""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return None
    
    content = skill_md.read_text()
    
    # Extract frontmatter
    frontmatter_match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return None
    
    frontmatter = frontmatter_match.group(1)
    
    # Parse name
    name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
    name = name_match.group(1).strip() if name_match else skill_path.name
    
    # Parse description
    desc_match = re.search(r'^description:\s*(.+)$', frontmatter, re.MULTILINE | re.DOTALL)
    description = desc_match.group(1).strip() if desc_match else ""
    
    # Find references to other skills
    dependencies = []
    skill_pattern = r'[a-z0-9-]+-?[a-z0-9-]*'
    words = re.findall(skill_pattern, content.lower())
    
    # Check for skill mentions
    for word in set(words):
        if word != name and len(word) > 3:
            potential_skill = Path(SKILLS_DIR) / word
            if potential_skill.exists() and potential_skill.is_dir():
                if word not in dependencies:
                    dependencies.append(word)
    
    # Check for explicit skill mentions
    skill_refs = re.findall(r'`([a-z0-9-]+)`|"([a-z0-9-]+)"', content)
    for match in skill_refs:
        for ref in match:
            if ref and ref != name:
                potential_skill = Path(SKILLS_DIR) / ref
                if potential_skill.exists():
                    if ref not in dependencies:
                        dependencies.append(ref)
    
    # Count resources
    scripts = list((skill_path / "scripts").glob("*")) if (skill_path / "scripts").exists() else []
    references = list((skill_path / "references").glob("*")) if (skill_path / "references").exists() else []
    assets = list((skill_path / "assets").glob("*")) if (skill_path / "assets").exists() else []
    
    return {
        "name": name,
        "path": str(skill_path),
        "description": description[:100] + "..." if len(description) > 100 else description,
        "dependencies": dependencies,
        "resources": {
            "scripts": len(scripts),
            "references": len(references),
            "assets": len(assets),
            "total": len(scripts) + len(references) + len(assets)
        }
    }

def build_dependency_map():
    """Build complete dependency map"""
    skills_path = Path(SKILLS_DIR)
    
    # Find all skill directories
    skill_dirs = [d for d in skills_path.iterdir() if d.is_dir() and d.name not in ['dist', 'archive', '__pycache__', '.git']]
    
    skills = []
    for skill_dir in sorted(skill_dirs):
        info = extract_skill_info(skill_dir)
        if info:
            skills.append(info)
    
    # Calculate dependency stats
    dependent_on = {}
    depended_by = {}
    
    for skill in skills:
        # Who this skill depends on
        dependent_on[skill['name']] = skill['dependencies']
        
        # Who depends on this skill
        for dep in skill['dependencies']:
            if dep not in depended_by:
                depended_by[dep] = []
            depended_by[dep].append(skill['name'])
    
    # Find root skills (no dependencies)
    root_skills = [s['name'] for s in skills if not s['dependencies']]
    
    # Find leaf skills (no one depends on them)
    all_deps = set()
    for deps in dependent_on.values():
        all_deps.update(deps)
    leaf_skills = [s['name'] for s in skills if s['name'] not in all_deps]
    
    # Find standalone skills (no deps, no dependents)
    standalone = [s for s in root_skills if s in leaf_skills]
    
    return {
        "generated_at": datetime.now().isoformat(),
        "total_skills": len(skills),
        "skills": skills,
        "dependency_tree": {
            "dependent_on": dependent_on,
            "depended_by": depended_by
        },
        "analysis": {
            "root_skills": root_skills,
            "leaf_skills": leaf_skills,
            "standalone_skills": standalone,
            "most_dependent": max(depended_by.items(), key=lambda x: len(x[1])) if depended_by else None
        }
    }

def generate_markdown_report(data):
    """Generate human-readable report"""
    report = f"""# Skill Dependency Map

**Generated:** {data['generated_at']}
**Total Skills:** {data['total_skills']}

## Overview

| Metric | Value |
|--------|-------|
| Root Skills (no deps) | {len(data['analysis']['root_skills'])} |
| Leaf Skills (no dependents) | {len(data['analysis']['leaf_skills'])} |
| Standalone Skills | {len(data['analysis']['standalone_skills'])} |

## Root Skills (Foundation)

These skills have no dependencies and form the foundation:

"""
    
    for skill_name in data['analysis']['root_skills'][:10]:
        report += f"- `{skill_name}`\n"
    
    report += "\n## Most Depended Upon\n\n"
    if data['analysis']['most_dependent']:
        skill_name, dependents = data['analysis']['most_dependent']
        report += f"**{skill_name}** - Used by {len(dependents)} skills:\n"
        report += f"```\n{', '.join(dependents[:10])}\n```\n"
    
    report += "\n## Dependency Matrix\n\n| Skill | Dependencies | Dependents | Total Resources |\n|-------|-------------|------------|-----------------|\n"
    
    for skill in sorted(data['skills'], key=lambda x: x['resources']['total'], reverse=True)[:20]:
        deps_count = len(skill['dependencies'])
        dep_by_count = len(data['dependency_tree']['depended_by'].get(skill['name'], []))
        report += f"| {skill['name'][:30]} | {deps_count} | {dep_by_count} | {skill['resources']['total']} |\n"
    
    return report

def main():
    print("=" * 60)
    print("Generating Skill Dependency Map")
    print("=" * 60)
    print()
    
    # Build map
    data = build_dependency_map()
    
    # Save JSON
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✅ JSON saved: {OUTPUT_FILE}")
    
    # Generate markdown report
    report = generate_markdown_report(data)
    report_file = OUTPUT_FILE.replace('.json', '.md')
    with open(report_file, 'w') as f:
        f.write(report)
    print(f"✅ Report saved: {report_file}")
    
    # Summary
    print()
    print("SUMMARY:")
    print(f"  Total Skills: {data['total_skills']}")
    print(f"  Root Skills: {len(data['analysis']['root_skills'])}")
    print(f"  Leaf Skills: {len(data['analysis']['leaf_skills'])}")
    print(f"  Standalone: {len(data['analysis']['standalone_skills'])}")
    
    if data['analysis']['most_dependent']:
        skill, deps = data['analysis']['most_dependent']
        print(f"  Most Depended: {skill} ({len(deps)} dependents)")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()
