---
name: workspace-organizer
description: Organize cluttered workspaces by auto-categorizing files, detecting duplicates, suggesting archives, and maintaining clean directory structures. Use when workspace has many files, finding things is hard, or cleanup is needed.
---

# Workspace Organizer

Keep the workspace clean, organized, and easy to navigate.

## When to Use

- Workspace has 100+ files
- Hard to find what you need
- Old projects clutter active work
- Duplicate files suspected
- "Organize my workspace" request

## Core Functions

### File Categorization

Auto-categorize files by type and age:

```markdown
## File Analysis

Active (modified < 7 days):
- main.py, strategy.py, config.json

Recent (7-30 days):
- old_version.py, backup.sql

Stale (> 30 days):
- experiment_v1.py, draft.md
- SUGGEST: Move to archive/

Unknown/Unclassified:
- temp.txt, untitled_1.py
- SUGGEST: Review and categorize
```

### Duplicate Detection

Find and flag duplicates:

```markdown
## Duplicates Found
⚠️ config.json and config_backup.json are identical
⚠️ utils.py in /src and /lib are 95% similar

Suggested actions:
- [ ] Delete config_backup.json
- [ ] Merge utils.py files
```

### Archive Suggestions

Identify old work for archiving:

| Project | Last Modified | Size | Action |
|---------|--------------|------|--------|
| old-trading-bot/ | 2026-01-15 | 2MB | Suggest archive |
| experiments/ | 2026-02-28 | 5MB | Keep - recently used |
| temp/ | 2026-03-01 | 500KB | Suggest cleanup |

## Directory Structure Recommendations

Standard structure to suggest:

```
workspace/
├── active/           # Current work
├── archive/          # Old projects (by date)
│   ├── 2026-01/
│   └── 2026-02/
├── assets/           # Images, fonts, etc
├── scripts/          # Utility scripts
├── temp/             # Temporary (auto-cleanup > 7 days)
└── templates/        # Reusable boilerplate
```

## Scripts

Use `scripts/analyze_workspace.py` to scan and report:

```bash
python3 scripts/analyze_workspace.py
# Outputs: file inventory, duplicates, stale files
```

Use `scripts/organize.py` to auto-organize:

```bash
python3 scripts/organize.py --dry-run  # Preview changes
python3 scripts/organize.py --execute  # Execute organization
```

## Workflow

### Weekly Cleanup

```
1. Run analyze_workspace.py
2. Review stale files (> 30 days)
3. Suggest archive or delete
4. Get user confirmation
5. Execute cleanup
```

### On "Organize My Workspace"

```
1. Scan entire workspace
2. Categorize all files
3. Detect duplicates
4. Propose directory structure
5. Create archive/ and temp/ if missing
6. Move files with user confirmation
```

## Integration

Store organization state in `memory/workspace_state.json`:

```json
{
  "lastScan": "2026-03-08T18:00:00",
  "fileCount": 150,
  "categories": {
    "active": 45,
    "recent": 30,
    "stale": 75
  },
  "duplicates": ["config.json", "config_backup.json"],
  "suggestedActions": [...]
}
```
