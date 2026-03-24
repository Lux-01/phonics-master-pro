# Memory Migration Report

Generated: 2026-03-23T20:28:55.631849

## Summary

- Files with references: 1
- Status: Migrated to universal-memory-system v2.0

## Migration Guide

### Old API (memory-manager)
```python
from memory-manager import remember, recall
from memory-manager.memory_system_integration import MemorySystem
ms = MemorySystem()
ms.remember('something')
```

### New API (universal-memory-system)
```python
from skills.universal_memory_system import remember, recall
from skills.universal_memory_system import MemoryAPI
api = MemoryAPI()
api.remember('something')
```

## Files Requiring Updates

### /home/skux/.openclaw/workspace/skills/ai-learning-system/ai_learning_system.py

- Line 22: `sys.path.insert(0, '/home/skux/.openclaw/workspace/skills/memory-manager`
  - Suggest: `# REMOVED: UMS is auto-importable`


## Function Mapping

| Old | New |
|-----|-----|
| `MemorySystem()` | `UnifiedMemoryAPI()` |
| `get_memory_system()` | `get_memory_api()` |
| `get_mel()` | `get_memory_api()` |
| `remember_key()` | `remember_api_key()` |
| `remember_pref()` | `remember_preference()` |
| `log_fragment()` | `remember()` |
| `pre_query_memory.gather_context()` | `PreQueryMemory.gather_context()` |

## Migration Complete

Memory-manager skill has been archived. All functionality is now available in UMS v2.0.