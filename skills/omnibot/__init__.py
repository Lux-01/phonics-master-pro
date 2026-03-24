"""
Omnibot - Intelligent Task Automation System

A modular AI agent framework for autonomous task execution with
human-in-the-loop oversight and tiered memory management.

Phase 1: Core + Memory Modules
- Orchestrator: Central request routing
- Memory Manager: Hot/Warm/Cold storage tiers
- Checkpoint Manager: Human approval gates
- Intent Parser: Understanding user goals
- Task Planner: Breaking goals into sub-tasks

Usage:
    from omnibot.core.orchestrator import Orchestrator
    
    bot = Orchestrator()
    result = bot.process_request("Create a website for my business")
"""

__version__ = "0.1.0"
__author__ = "OpenClaw"
__phase__ = "1"

from pathlib import Path

# Package paths
PACKAGE_ROOT = Path(__file__).parent
MEMORY_DIR = PACKAGE_ROOT / "memory_store"

# Ensure memory directory exists
MEMORY_DIR.mkdir(parents=True, exist_ok=True)
