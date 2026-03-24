---
name: autonomous-scheduler
description: Cron-like task scheduler with dependency management, retry logic, and execution tracking. Persistent task runner for daily, weekly, and monthly automation.
---

# Autonomous Scheduler

**"Set it and forget it — with intelligence."**

Persistent task scheduling with dependency chains, retry logic, and full execution history.

## Capabilities

- **Schedule tasks:** hourly, daily, weekly, monthly
- **Dependency management:** Tasks wait for prerequisites
- **Retry logic:** 3 attempts with exponential backoff
- **Execution tracking:** Log all runs with success/failure
- **Persistent state:** Survives restarts

## Usage

```bash
python3 autonomous_scheduler.py --mode add --name "Daily Backup" --command "backup.sh" --schedule daily

python3 autonomous_scheduler.py --mode run

python3 autonomous_scheduler.py --mode report
```

## Features

- Task dependency chains
- Exponential backoff on failure
- State persistence in JSON
- Execution log (last 100 runs)
- Timeout protection (5 min default)
