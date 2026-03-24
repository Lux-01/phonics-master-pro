#!/usr/bin/env python3
"""
Skill Activation Dashboard
Interactive dashboard for skill management and monitoring

ACA Methodology:
1. Requirements: Track skill usage, activation, and performance
2. Architecture: HTML-based dashboard with JSON data backend
3. Data Flow: Read skills → analyze → generate HTML
4. Edge Cases: Missing files, empty skills, permission errors
5. Tool Constraints: Standard Python, no external deps
6. Error Handling: Graceful degradation
7. Testing: Verify all skills appear, links work
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta

SKILLS_DIR = "/home/skux/.openclaw/workspace/skills"
OUTPUT_FILE = "/home/skux/.openclaw/workspace/skill_dashboard.html"

def get_skill_status(skill_path):
    """Determine skill activation status"""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return "invalid"
    
    content = skill_md.read_text()
    
    # Check for resources
    has_scripts = (skill_path / "scripts").exists() and any((skill_path / "scripts").iterdir())
    has_references = (skill_path / "references").exists() and any((skill_path / "references").iterdir())
    has_assets = (skill_path / "assets").exists() and any((skill_path / "assets").iterdir())
    
    # Check for packaged version
    dist_file = Path(SKILLS_DIR) / "dist" / f"{skill_path.name}.skill"
    is_packaged = dist_file.exists()
    
    # Calculate status
    if has_scripts and has_references:
        status = "complete"
    elif has_scripts:
        status = "functional"
    elif has_references:
        status = "documented"
    else:
        status = "minimal"
    
    # Check for recent edits
    try:
        stat = skill_md.stat()
        last_modified = datetime.fromtimestamp(stat.st_mtime)
        days_since_edit = (datetime.now() - last_modified).days
    except (OSError, IOError) as e:
        # File stat failed (permissions, deleted, etc.)
        days_since_edit = 999
    
    # Check if recently active (edited in last 30 days)
    is_recent = days_since_edit < 30
    
    return {
        "path": str(skill_path),
        "has_scripts": has_scripts,
        "has_references": has_references,
        "has_assets": has_assets,
        "is_packaged": is_packaged,
        "status": status,
        "last_modified_days": days_since_edit,
        "is_recent": is_recent
    }

def analyze_skills():
    """Analyze all skills"""
    skills_path = Path(SKILLS_DIR)
    skill_dirs = [d for d in skills_path.iterdir() if d.is_dir() and d.name not in ['dist', 'archive', '__pycache__', '.git']]
    
    skills = []
    for skill_dir in sorted(skill_dirs):
        status = get_skill_status(skill_dir)
        if status:
            skills.append({
                "name": skill_dir.name,
                **status
            })
    
    # Calculate statistics
    stats = {
        "total": len(skills),
        "complete": len([s for s in skills if s['status'] == 'complete']),
        "functional": len([s for s in skills if s['status'] == 'functional']),
        "documented": len([s for s in skills if s['status'] == 'documented']),
        "minimal": len([s for s in skills if s['status'] == 'minimal']),
        "packaged": len([s for s in skills if s['is_packaged']]),
        "recent": len([s for s in skills if s['is_recent']]),
        "with_scripts": len([s for s in skills if s['has_scripts']]),
        "with_references": len([s for s in skills if s['has_references']]),
        "with_assets": len([s for s in skills if s['has_assets']])
    }
    
    return {
        "generated_at": datetime.now().isoformat(),
        "skills": skills,
        "stats": stats
    }

def generate_html(data):
    """Generate HTML dashboard"""
    
    # Status colors
    status_colors = {
        "complete": "#2ecc71",
        "functional": "#3498db",
        "documented": "#f39c12",
        "minimal": "#95a5a6"
    }
    
    status_labels = {
        "complete": "✅ Complete",
        "functional": "🔧 Functional",
        "documented": "📚 Documented",
        "minimal": "⚪ Minimal"
    }
    
    # Generate skill cards
    skill_cards = ""
    for skill in data['skills']:
        color = status_colors.get(skill['status'], '#95a5a6')
        label = status_labels.get(skill['status'], skill['status'])
        
        scripts_icon = "⚙️" if skill['has_scripts'] else "○"
        refs_icon = "📖" if skill['has_references'] else "○"
        package_icon = "📦" if skill['is_packaged'] else "○"
        recent_icon = "🔥" if skill['is_recent'] else "○"
        
        skill_cards += f"""
        <div class="skill-card">
            <div class="skill-header">
                <h3>{skill['name']}</h3>
                <span class="status-badge" style="background: {color}">{label}</span>
            </div>
            <div class="skill-meta">
                <span title="Scripts">{scripts_icon}</span>
                <span title="References">{refs_icon}</span>
                <span title="Packaged">{package_icon}</span>
                <span title="Recently Active">{recent_icon}</span>
            </div>
            <div class="skill-path">{skill['path'].split('/')[-1]}</div>
            <div class="skill-age">Last edited: {skill['last_modified_days']} days ago</div>
        </div>
        """
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>OpenClaw Skill Activation Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a2e;
            color: #eee;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }}
        
        h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            opacity: 0.9;
            font-size: 1.1em;
        }}
        
        .timestamp {{
            font-size: 0.9em;
            opacity: 0.7;
            margin-top: 10px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: #16213e;
            padding: 25px;
            border-radius: 12px;
            border: 1px solid #2a2a4a;
            text-align: center;
            transition: transform 0.2s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            border-color: #667eea;
        }}
        
        .stat-number {{
            font-size: 3em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .stat-label {{
            font-size: 0.95em;
            color: #aaa;
            margin-top: 5px;
        }}
        
        .skills-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .skill-card {{
            background: #16213e;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #2a2a4a;
            transition: all 0.3s;
        }}
        
        .skill-card:hover {{
            border-color: #667eea;
            transform: translateY(-3px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.3);
        }}
        
        .skill-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 15px;
        }}
        
        .skill-header h3 {{
            font-size: 1.2em;
            color: #fff;
            word-break: break-word;
        }}
        
        .status-badge {{
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.75em;
            font-weight: bold;
            white-space: nowrap;
        }}
        
        .skill-meta {{
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
            font-size: 1.2em;
        }}
        
        .skill-meta span {{
            opacity: 0.6;
        }}
        
        .skill-meta span:not(:contains("○")) {{
            opacity: 1;
        }}
        
        .skill-path {{
            font-size: 0.85em;
            color: #888;
            font-family: monospace;
            margin-bottom: 5px;
        }}
        
        .skill-age {{
            font-size: 0.8em;
            color: #666;
        }}
        
        .legend {{
            background: #16213e;
            padding: 20px;
            border-radius: 12px;
            margin-top: 30px;
            border: 1px solid #2a2a4a;
        }}
        
        .legend h3 {{
            margin-bottom: 15px;
        }}
        
        .legend-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }}
        
        footer {{
            text-align: center;
            padding: 30px;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🦞 OpenClaw Skill Activation Dashboard</h1>
            <div class="subtitle">Real-time skill inventory and activation status</div>
            <div class="timestamp">Generated: {data['generated_at']}</div>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{data['stats']['total']}</div>
                <div class="stat-label">Total Skills</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color: #2ecc71">{data['stats']['complete']}</div>
                <div class="stat-label">Complete</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color: #3498db">{data['stats']['functional']}</div>
                <div class="stat-label">Functional</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color: #e74c3c">{data['stats']['recent']}</div>
                <div class="stat-label">Recently Active</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color: #9b59b6">{data['stats']['packaged']}</div>
                <div class="stat-label">Packaged</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{data['stats']['with_scripts']}</div>
                <div class="stat-label">With Scripts</div>
            </div>
        </div>
        
        <h2 style="margin-bottom: 20px;">All Skills</h2>
        <div class="skills-grid">
            {skill_cards}
        </div>
        
        <div class="legend">
            <h3>Legend</h3>
            <div class="legend-grid">
                <div class="legend-item">
                    <div class="legend-color" style="background: #2ecc71;"></div>
                    <span>✅ Complete (scripts + references)</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #3498db;"></div>
                    <span>🔧 Functional (scripts only)</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #f39c12;"></div>
                    <span>📚 Documented (references only)</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #95a5a6;"></div>
                    <span>⚪ Minimal (documentation only)</span>
                </div>
            </div>
            <div style="margin-top: 15px; font-size: 0.9em;">
                <p><strong>Icons:</strong></p>
                <p>⚙️ = Has Scripts | 📖 = Has References | 📦 = Packaged | 🔥 = Active (30 days)</p>
            </div>
        </div>
        
        <footer>
            <p>OpenClaw Workspace Skills | Location: ~/.openclaw/workspace/skills/</p>
        </footer>
    </div>
</body>
</html>
"""
    return html

def main():
    print("=" * 60)
    print("Generating Skill Activation Dashboard")
    print("=" * 60)
    print()
    
    # Analyze skills
    print("Analyzing skills...")
    data = analyze_skills()
    
    # Generate HTML
    print("Generating HTML dashboard...")
    html = generate_html(data)
    
    # Save
    with open(OUTPUT_FILE, 'w') as f:
        f.write(html)
    
    print(f"✅ Dashboard saved: {OUTPUT_FILE}")
    print()
    print("Statistics:")
    print(f"  Total Skills: {data['stats']['total']}")
    print(f"  Complete: {data['stats']['complete']}")
    print(f"  Functional: {data['stats']['functional']}")
    print(f"  Documented: {data['stats']['documented']}")
    print(f"  Minimal: {data['stats']['minimal']}")
    print(f"  Packaged: {data['stats']['packaged']}")
    print(f"  Recently Active: {data['stats']['recent']}")
    print()
    print("=" * 60)
    print()
    print("Open the dashboard in your browser:")
    print(f"  file://{OUTPUT_FILE}")

if __name__ == "__main__":
    main()
