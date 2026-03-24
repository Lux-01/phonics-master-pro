---
name: autonomous-tool-builder
description: Generate new tools from usage patterns and user requests. Creates Python scripts, shell automation, and utility functions based on detected needs.
---

# Autonomous Tool Builder (ATB)

**"Builds tools when it sees patterns."**

Detects repetitive tasks and automatically generates tools to handle them.

## Capabilities

- **Pattern detection:** Identifies repeated work
- **Auto-generation:** Creates tools from templates
- **Smart defaults:** Sensible starting points
- **Self-documenting:** Generated code includes docs
- **Integration ready:** Works with the skill system

## Usage

```bash
python3 atb.py --detect-patterns

python3 atb.py --build-tool "CSV processor"

python3 atb.py --from-pattern "data-transformation"
```

## Generated Tool Template

Every tool gets:
- Argument parsing
- Error handling
- Logging
- Configuration file support
- Test scaffolding
