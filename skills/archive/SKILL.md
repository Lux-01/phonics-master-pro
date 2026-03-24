---
name: archive
description: Archived skills storage. Contains superseded or deprecated skills that are no longer actively maintained but kept for reference. Use when looking for historical skill versions or legacy implementations.
---

# Skills Archive

Storage location for deprecated and archived skills.

## Purpose

This directory contains skills that have been:
- **Superseded** by newer versions
- **Deprecated** in favor of better implementations
- **Merged** into other skills
- **Temporarily disabled** for maintenance

## Current Archive Contents

| Skill | Status | Reason |
|-------|--------|--------|
| income-optimizer | Archived | Merged into kpi-performance-tracker |
| integration-compatibility-engine | Archived | Merged into integration-orchestrator |
| multi-agent-orchestration-engine | Archived | Merged into multi-agent-coordinator |

## Usage

Skills in this directory are **not automatically loaded** by OpenClaw.

To use an archived skill:
1. Copy it to the main `skills/` directory
2. Update references to use current skill names
3. Test before relying on it

## Cleanup Policy

Archived skills may be removed after 6 months of non-use.
Check last modified date before depending on archived content.

---

*Skills in this directory are not maintained. Use at your own risk.*
