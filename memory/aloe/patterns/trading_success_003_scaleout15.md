---
pattern_id: trading_success_003
pattern_name: Early Scale-Out at 15%
confidence: 0.91
uses: 86
success_rate: 0.826
created: 2026-03-09
category: trading_exit
domain: crypto_meme_coins
---

# Pattern: Early Scale-Out at 15%

**Type:** Profit-Taking Strategy  
**Confidence:** 91% (86 uses, 82.6% win rate)  
**Source:** Strategy evolution from backtest

## Pattern Description

Exit 100% of position at +15% profit rather than holding for higher targets. This outperforms trailing stops and bag-holding for meme coin momentum plays.

## Why It Works

1. **Meme Coin Reality:** Most moves are quick pumps followed by dumps
2. **Risk/Reward:** +15% compound beats waiting for +50% that reverses
3. **Volatility:** Reduces drawdown exposure

## Recognition Criteria

```yaml
exit_conditions:
  profit_target: "+15% from entry"
  exit_percentage: "100%"
  
  alternative_triggers:
    time_stop: "4 hours"
    stop_loss: "-7%"
    
  momentum_check:
    if: "volume_declining"
    action: "exit_immediately"
```

## Success Statistics

- **Sample Size:** 86 occurrences  
- **Win Rate:** 82.6% when exited at +15%
- **Compare to Trailing:** +156% total vs +89% with trailing
- **Average Hold:** 4 hours
- **Risk/Reward:** 2.14:1

## When to Apply

✅ **Use:**
- Meme coins with pump potential
- Quick momentum plays
- Lower conviction setups

⚠️ **Consider Holding:**
- Strong narrative confirmed
- Whale accumulation pattern
- Volume still increasing

## Psychology Note

"The fear of selling too early often leads to selling too late. The backtest proved +15% is the sweet spot for meme coins."

## ALOE Learned

```
User tendency to hold for bigger gains hurt performance.
Switching to early scale-out improved results significantly.
Greedy exits reduced from 40% of trades to 15%.
```
