# ALOE Pattern Templates

## Success Pattern Template

```json
{
  "pattern_id": "PAT-001",
  "category": "success",
  "name": "Parallel API Fetching",
  "description": "Fetching multiple URLs in parallel improves speed",
  "confidence": 0.95,
  "conditions": {
    "when": ["multiple_urls", "independent_fetches", "network_io"],
    "apply_to": ["web_fetch", "api_calls"]
  },
  "actions": {
    "parallelize": true,
    "max_concurrent": 10
  },
  "metrics": {
    "uses": 45,
    "success_rate": 0.98,
    "avg_time_saved": "80%"
  },
  "examples": [
    {
      "task": "Research 5 APIs",
      "before": "10s sequential",
      "after": "2s parallel"
    }
  ],
  "created": "2026-03-01",
  "last_applied": "2026-03-08"
}
```

## Failure Pattern Template

```json
{
  "pattern_id": "PAT-002",
  "category": "failure",
  "name": "Direct File Overwrite Risk",
  "description": "Overwriting files without backup causes data loss",
  "confidence": 0.90,
  "conditions": {
    "when": ["file_write", "_existing_file", "production_path"],
    "danger_level": "high"
  },
  "actions": {
    "create_backup": true,
    "ask_confirmation": true
  },
  "metrics": {
    "encountered": 3,
    "prevented": 3
  },
  "examples": [
    {
      "task": "Update config.json",
      "incident": "Accidentally overwrote",
      "recovery": "Restored from backup"
    }
  ],
  "created": "2026-03-05"
}
```

## Efficiency Pattern Template

```json
{
  "pattern_id": "PAT-003",
  "category": "efficiency",
  "name": "Memory Before File Read",
  "description": "Check memory before re-reading files",
  "confidence": 0.88,
  "conditions": {
    "when": ["file_read_requested", "file_already_read"],
    "apply_to": ["read"]
  },
  "actions": {
    "check_memory_first": true,
    "offer_summary": true
  },
  "metrics": {
    "uses": 120,
    "token_savings": "30%"
  },
  "examples": [
    {
      "task": "Re-read config.json",
      "before": "Full file read (500 tokens)",
      "after": "Used cached summary (50 tokens)"
    }
  ],
  "created": "2026-03-02"
}
```

## User Preference Pattern

```json
{
  "pattern_id": "PREF-001",
  "category": "preference",
  "name": "Concise Output Preference",
  "description": "User prefers brief responses with key info",
  "confidence": 0.85,
  "observed_from": [
    "Positive feedback on brief summaries",
    "User said 'concise' 12 times",
    "Skipped verbose sections"
  ],
  "actions": {
    "default_format": "bullet_points",
    "max_detail": "summary_first",
    "expandable": true
  },
  "metrics": {
    "uses": 200,
    "satisfaction": 0.92
  },
  "created": "2026-03-01"
}
```

## Risk Pattern Template

```json
{
  "pattern_id": "RISK-001",
  "category": "risk",
  "name": "Crypto Trading Risk",
  "description": "Financial transactions need explicit confirmation",
  "confidence": 0.95,
  "conditions": {
    "when": ["crypto", "trading", "real_money"],
    "danger_level": "critical"
  },
  "actions": {
    "require_confirmation": true,
    "show_details": true,
    "log_decision": true
  }
}
```
