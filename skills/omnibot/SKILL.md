# Omnibot - Ultimate Autonomous Agent

A comprehensive autonomous agent skill with multi-tier memory, context verification, API management, crypto wallet handling, ACA integration, research engine, error recovery, approval checkpoints, self-monitoring, security, and trust scoring.

## Quick Start

```python
from omnibot import Omnibot

bot = Omnibot()

# Remember something
bot.remember("User prefers dark mode", priority="high")

# Recall information
context = bot.recall("user preferences")

# Run ACA workflow
result = bot.aca_workflow(
    requirements="Build a login system",
    data_flow="User input → Validation → Auth → Session",
    constraints=["Must use HTTPS", "Rate limited"]
)

# Research and design GUI
mockups = bot.research_design(
    topic="coffee shop app",
    screens=["home", "menu", "cart", "checkout"],
    platform="mobile"
)
```

## Core Capabilities

### 1. Memory System
- **Hot Memory**: Current session context (in-memory)
- **Warm Memory**: Daily logs (memory/YYYY-MM-DD.md)
- **Cold Memory**: Curated long-term storage

### 2. Context Verification
- State validation before actions
- Stale data detection
- Outdated reference flagging

### 3. API Management
- Auto-discovery from public sources
- Secure encrypted vault
- Cost tracking and rate limiting

### 4. Crypto Wallet Manager
- Secure key storage
- Auto-injection in code
- Purpose tagging

### 5. ACA Integration
7-step workflow for every code task:
1. Requirements analysis
2. Architecture design
3. Data flow mapping
4. Edge case identification
5. Constraint definition
6. Error handling
7. Testing strategy

### 6. Research Engine (GUI-First)
- Visual design research
- Color psychology analysis
- Layout pattern research
- HTML/CSS mockup generation

### 7. Error Recovery
- Analyze → Hypothesize → Fix → Verify
- Max 3 attempts before escalation
- Pattern learning

### 8. Approval Checkpoints
Configurable permission levels:
- **Auto**: File reading, research, coding
- **Ask First**: External actions, spending, deletion, publishing

### 9. Self-Monitoring
- Task tracking
- Success rate analysis
- Cost monitoring
- Auto-improvement suggestions

### 10. Security Sentinel
- Secret scanning
- Permission validation
- Destructive operation warnings

### 11. Auto Documentation
- USAGE.md for scripts
- README.md for projects
- Decision logs

### 12. Trust Scoring
- Confidence % with every output
- Reasoning transparency
- User trust building

## File Structure

```
omnibot/
├── SKILL.md                    # This file
├── omnibot.py                  # Main entry point
├── core/                       # Core orchestration
├── memory/                     # Memory management
├── reasoning/                  # ACA & error recovery
├── research/                   # Design research & GUI
├── api/                        # API discovery & vault
├── wallet/                     # Crypto wallet management
├── ui/                         # GUI components & renderer
└── meta/                       # Self-monitoring & docs
```

## Special Feature: App Design Workflow

```python
# Initiate comprehensive app design research
design = bot.research_app_design(
    app_type="coffee shop",
    features=["ordering", "loyalty", "payments"],
    target_audience="urban millennials"
)

# Returns:
# - Color palette with psychology rationale
# - Layout patterns from competitors
# - GUI mockups as HTML files
# - Design system documentation
```

## Configuration

Create `omnibot_config.json`:

```json
{
  "auto_approve": ["read", "research", "code"],
  "approval_required": ["external", "spend", "delete", "publish"],
  "max_error_retries": 3,
  "stale_data_threshold_hours": 24,
  "cost_budget_daily": 100.00,
  "trust_confidence_threshold": 75
}
```

## Security Notes

- Never expose API keys or wallet keys in logs
- All secrets are encrypted at rest
- Permission validation before external actions
- Secret scanning on all outputs

## License

MIT - Part of the OpenClaw ecosystem