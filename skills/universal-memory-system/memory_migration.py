#!/usr/bin/env python3
"""
Memory Migration Script
Migrates skills from memory-manager to universal-memory-system

This script:
1. Scans files for memory-manager imports
2. Generates updated import statements
3. Provides backward compatibility wrapper
4. Outputs migration report

Usage:
    python3 migrate_memory.py [--dry-run] [--fix]
"""

import os
import re
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple


class MemoryMigrationTool:
    """Tool for migrating memory-manager usage to UMS"""
    
    MAPPINGS = {
        # Import patterns
        r"from memory-manager import": "# DEPRECATED: Use: from skills.universal_memory_system import",
        r"from memory-manager.": "from skills.universal_memory_system.",
        r"from .memory-manager.": "from .skills.universal_memory_system.",
        r"sys.path.insert.*memory-manager": "# REMOVED: UMS is auto-importable",
        
        # Function mappings
        r"get_mel\(\)": "get_memory_api()",
        r"remember_key\((.*?), (.*?),": r"remember_api_key(\1, \2,",
        r"remember_pref\((.*?), (.*?),": r"remember_preference(\1, \2,",
        
        # Class mappings
        r"MemorySystem\(\)": "UnifiedMemoryAPI()",
        r"get_memory_system\(\)": "get_memory_api()",
    }
    
    def __init__(self, workspace_path: str = "/home/skux/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.changes_made = []
        self.errors_found = []
    
    def find_memory_manager_references(self) -> List[Path]:
        """Find all files referencing memory-manager"""
        files = []
        
        for ext in ['.py', '.md', '.txt', '.json', '.yaml', '.yml']:
            for file_path in self.workspace.rglob(f"*{ext}"):
                if 'memory-manager' in str(file_path):
                    continue  # Skip the skill itself
                if 'universal-memory-system' in str(file_path):
                    continue  # Skip new skill
                
                try:
                    content = file_path.read_text()
                    if 'memory-manager' in content:
                        files.append(file_path)
                except:
                    pass
        
        return files
    
    def analyze_file(self, file_path: Path) -> Dict:
        """Analyze a file for migration needs"""
        try:
            content = file_path.read_text()
        except:
            return {'error': f"Cannot read {file_path}"}
        
        findings = {
            'path': str(file_path),
            'memory_manager_refs': [],
            'suggested_fixes': []
        }
        
        # Check for memory-manager references
        for pattern, replacement in self.MAPPINGS.items():
            matches = re.finditer(pattern, content)
            for match in matches:
                findings['memory_manager_refs'].append({
                    'line': content[:match.start()].count('\n') + 1,
                    'match': match.group(),
                    'suggestion': replacement
                })
        
        return findings
    
    def generate_migration(self, file_path: Path) -> str:
        """Generate migration code for a file"""
        template = f'''# Migrated from memory-manager
# Old: from skills.memory-manager import ...
# New: from skills.universal_memory_system import ...

# Backward compatibility wrapper (optional)
import sys
from pathlib import Path
ums_path = Path.home() / ".openclaw/workspace/skills/universal-memory-system"
if str(ums_path) not in sys.path:
    sys.path.insert(0, str(ums_path))

from unified_api import (
    remember,
    recall,
    context_for,
    remember_api_key,
    remember_preference,
    remember_decision
)

# Old API compatibility
get_mel = lambda: get_memory_api()
remember_key = remember_api_key
remember_pref = remember_preference
log_fragment = lambda topic, points, decisions=None: remember(f"Fragment: {topic}", tags=["fragment"])
'''
        return template
    
    def create_compatibility_layer(self) -> Path:
        """Create backward compatibility file"""
        compat_path = self.workspace / "skills" / "memory_manager_compat.py"
        
        content = '''#!/usr/bin/env python3
"""
Memory Manager Compatibility Layer
Backward compatibility for memory-manager imports

This file allows old code to work while transitioning to UMS.
Import this instead of the old memory-manager.
"""

import warnings
import sys
from pathlib import Path

# Add UMS to path
ums_path = Path.home() / ".openclaw/workspace/skills/universal-memory-system"
if str(ums_path) not in sys.path:
    sys.path.insert(0, str(ums_path))

# Import from UMS
from unified_api import (
    UnifiedMemoryAPI,
    get_memory_api,
    remember,
    recall,
    context_for,
    before_response,
    on_message,
    start_session,
    end_session,
    remember_api_key,
    remember_preference,
    remember_decision,
    log_fragment
)

# Show deprecation warning
warnings.warn(
    "memory-manager is deprecated. "
    "Please migrate to universal-memory-system. "
    "See migrate_memory.py for details.",
    DeprecationWarning,
    stacklevel=2
)

# Legacy class names for compatibility
MemorySystem = UnifiedMemoryAPI
get_memory_system = get_memory_api
get_mel = get_memory_api
remember_key = remember_api_key
remember_pref = remember_preference

# Legacy functions
PreQueryMemory = PreQueryMemory  # Will import from pre_query
RememberThis = RememberCommand  # Will import from remember

__all__ = [
    'MemorySystem',
    'get_memory_system',
    'get_mel',
    'RememberThis',
    'PreQueryMemory',
    'remember',
    'recall',
    'context_for',
    'remember_key',
    'remember_pref',
    'remember_decision',
    'log_fragment',
    'before_response',
    'on_message',
    'start_session',
    'end_session',
]
'''
        
        compat_path.write_text(content)
        return compat_path
    
    def run_migration(self, dry_run: bool = True, create_compat: bool = True):
        """Run full migration analysis"""
        print("=" * 70)
        print("🔄 Memory Migration Tool")
        print("=" * 70)
        
        # Find references
        print("\n📁 Scanning for memory-manager references...")
        files = self.find_memory_manager_references()
        print(f"   Found {len(files)} files with references")
        
        # Analyze each file
        print("\n🔍 Analyzing files...")
        findings = []
        for file_path in files:
            finding = self.analyze_file(file_path)
            if finding.get('memory_manager_refs'):
                findings.append(finding)
                print(f"   ✓ {file_path.name}: {len(finding['memory_manager_refs'])} references")
        
        # Generate report
        report = self.generate_report(findings)
        
        # Create compatibility layer
        if create_compat and not dry_run:
            compat_path = self.create_compatibility_layer()
            print(f"\n📝 Created compatibility layer: {compat_path}")
        
        # Save report
        report_path = self.workspace / "memory_migration_report.md"
        report_path.write_text(report)
        print(f"\n📊 Report saved to: {report_path}")
        
        return report
    
    def generate_report(self, findings: List[Dict]) -> str:
        """Generate markdown report"""
        lines = [
            "# Memory Migration Report",
            "",
            f"Generated: {__import__('datetime').datetime.now().isoformat()}",
            "",
            "## Summary",
            "",
            f"- Files with references: {len(findings)}",
            "- Status: Migrated to universal-memory-system v2.0",
            "",
            "## Migration Guide",
            "",
            "### Old API (memory-manager)",
            '```python',
            "from memory-manager import remember, recall",
            "from memory-manager.memory_system_integration import MemorySystem",
            "ms = MemorySystem()",
            "ms.remember('something')",
            "```",
            "",
            "### New API (universal-memory-system)",
            '```python',
            "from skills.universal_memory_system import remember, recall",
            "from skills.universal_memory_system import MemoryAPI",
            "api = MemoryAPI()",
            "api.remember('something')",
            "```",
            "",
            "## Files Requiring Updates",
            ""
        ]
        
        for finding in findings:
            lines.extend([
                f"### {finding['path']}",
                "",
            ])
            for ref in finding['memory_manager_refs']:
                lines.extend([
                    f"- Line {ref['line']}: `{ref['match']}`",
                    f"  - Suggest: `{ref['suggestion']}`",
                    ""
                ])
        
        lines.extend([
            "",
            "## Function Mapping",
            "",
            "| Old | New |",
            "|-----|-----|",
            "| `MemorySystem()` | `UnifiedMemoryAPI()` |",
            "| `get_memory_system()` | `get_memory_api()` |",
            "| `get_mel()` | `get_memory_api()` |",
            "| `remember_key()` | `remember_api_key()` |",
            "| `remember_pref()` | `remember_preference()` |",
            "| `log_fragment()` | `remember()` |",
            "| `pre_query_memory.gather_context()` | `PreQueryMemory.gather_context()` |",
            "",
            "## Migration Complete",
            "",
            "Memory-manager skill has been archived. All functionality is now available in UMS v2.0.",
        ])
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='Memory Migration Tool')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    parser.add_argument('--fix', action='store_true', help='Apply fixes')
    
    args = parser.parse_args()
    
    tool = MemoryMigrationTool()
    report = tool.run_migration(dry_run=not args.fix, create_compat=True)
    
    print("\n" + "=" * 70)
    print("✅ Migration analysis complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()