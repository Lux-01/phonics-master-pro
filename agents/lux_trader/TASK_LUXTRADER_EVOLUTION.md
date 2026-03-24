# LuxTrader Evolution Task

## Objective
Build LuxTrader v3.1 (Evolved) with adaptive features using Skill methodology.

## Step-by-Step Plan (ACA + Skills)

### Step 1: OBSERVE (Autonomous Agent Skill)
- Read existing LuxTrader v3.0 code
- Read Holy Trinity Evolved for patterns
- Identify evolution opportunities

### Step 2: ORIENT (Analysis)
- Analyze current strengths/weaknesses
- Identify 5 evolution features to add
- Map integration points

### Step 3: DECIDE (Decision Matrix)
| Feature | Impact | Risk | Selected |
|---------|--------|------|----------|
| Streak tracking | High | Low | ✅ |
| Dynamic sizing | High | Low | ✅ |
| Market cycle | Med | Med | ✅ |
| Pattern learning | Med | Med | ✅ |
| Rug-Radar | High | Low | ✅ |

### Step 4: ACT (Code Evolution Skill Applied)
- Write luxtrader_evolved.py
- Document changes in EVO-001
- Create evolution entry

### Step 5: VALIDATE (Testing)
- Run backtest
- Compare to v3.0
- Log results

## Files In
- /agents/lux_trader/luxtrader_live.py
- /agents/lux_trader/holy_trinity_evolved.py
- /skills/autonomous-agent/SKILL.md
- /skills/code-evolution-tracker/SKILL.md

## Files Out
- /agents/lux_trader/luxtrader_evolved.py
- /memory/code_evolution/entries/EVO-001-luxtrader-evolution.md

## Expected Results
- +30-60% performance improvement
- Adaptive position sizing
- Streak awareness
- Better risk management