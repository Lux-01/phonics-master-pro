# Combined Strategy 1-Year Backtest Task

## Objective
Build a combined strategy system that aggregates all 7 strategies over 1 year of data while maintaining active learning.

## Requirements

### Combined Strategy Logic
1. Take signals from all 7 strategies
2. Weight them by historical performance
3. Require 3+ positive signals to trade
4. Use Rug-Radar as safety gatekeeper
5. Use Mean-Reverter for entry timing
6. Use LuxTrader as primary executor

### Data Requirements
- Current: 6 months (~550 trades per strategy)
- Target: 12 months (~1100 trades per strategy)
- Need to generate/synthesize additional 6 months

### Learning Component
- Track which strategy combinations work best
- Adjust signal weights based on win rate
- Log pattern: which strategy mix = wins
- Auto-evolve weights weekly

## Deliverables
- combined_strategy_1year.py (main backtest)
- combined_results.json (results)
- learning_log.json (pattern tracking)
- weight_evolution.json (how weights changed)

## File Location
/home/skux/.openclaw/workspace/agents/lux_trader/

## Existing Files to Reference
- mean_reverter_v3.py (template)
- luxtrader_live.py (entry/exit logic)
- 6month_simulation_results.json (baseline data)

## ACA Steps Applied
1. Requirements: Combine 7 strategies, 1 year backtest, learning active
2. Architecture: SignalAggregator → WeightEngine → EntryLogic → Tracker
3. Data Flow: Load data → Score all strategies → Vote → Trade → Learn
4. Edge Cases: Missing data, low signals, conflicting signals
5. Tool Constraints: Python only, JSON persistence, safe file ops
6. Error Handling: Skip missing data, log errors, continue
7. Testing: Run on 6mo first, verify, then extend to 12mo