# Solana Alpha Hunter v4.0 - Social Sentiment Edition

## What's New in v4.0

### 📱 Social Sentiment Velocity (NEW)
**Tracks social momentum to spot viral early**

**Components:**
1. **Social Presence Score** (0-3)
   - Website: +1
   - Twitter: +1  
   - Telegram: +1

2. **Volume-Attention Ratio** (bonus points)
   - High volume + social presence = viral signal
   - Volume >$200K = +2
   - Early viral (high vol / low MCAP) = +3

3. **Grade Scale:**
   - **A+ 🚀** (9-10): Viral momentum - strong buy
   - **A ✅** (7-8): Strong social - good buy
   - **B 🟡** (5-6): Moderate - okay
   - **C ⚠️** (3-4): Weak - caution
   - **D ❌** (0-2): No presence - skip

### Full Criteria (Now 12 Checks)

1. MCAP < $250K
2. Market Cap (primary)
3. Liquidity > $15K
4. Slippage simulation
5. 5m Volume > $5K
6. Mint revoked
7. LP locked >95%
8. Top 10 < 30%
9. Wallet Clustering
10. Holder Count
11. **Website Quality** ✅
12. **Social Sentiment Velocity** ✅ (NEW)

### Output Format

```
🎯 [TOKEN] Grade [X]/12
CA: xxx...

📊 MARKET:
  MCAP: $XXX | Age: Xh
  Price Velocity: +/-X%
  Liquidity: $XXX | Slippage $2K: X%

👥 HOLDERS:
  Count: XXX | Top 10: X%
  Cluster Risk: X/10

📱 SOCIAL VELOCITY (NEW):
  Website: ✅ URL
  Twitter: ✅ URL  
  Telegram: ❌
  Score: X/10 | Grade: A+ 🚀 VIRAL

📈 VOLUME:
  5m: $XXX | 1h: $XXX | 24h: $XXX
  Heatmap: 🔥🔥🔥

🔒 SECURITY:
  Mint: Revoked ✅
  LP: X% locked ✅
  Cluster: X/10

💡 SOCIAL SIGNALS:
  ✅ Website live
  ✅ Twitter active
  🚀 High volume + Twitter present
  🔥 Early viral indicator

🎯 FINAL: Grade X/12 [Letter]
   Recommendation: [APE/BUY/CAUTION/SKIP]
```

### Example - LUMO

```
🎯 LUMO Grade 9/12

📱 SOCIAL VELOCITY:
  Website: ✅ https://thevibeofcode.com/
  Twitter: ✅ https://x.com/... (Community)
  Score: 10/10
  Grade: A+ 🚀 VIRAL
  
  Signals:
    ✅ Website live
    ✅ Twitter active  
    🚀 High volume + social overlap
    🔥 Early viral (high vol / low cap)

  Viral momentum detected - socials
  matching trading volume acceleration
```

## Integration

Add to `solana_alpha_hunter.py`:

```python
from social_sentiment import SocialSentimentTracker

# In scan function:
sentiment = tracker.calculate_sentiment_velocity(
    ca, symbol, name, mcap, volume_24h
)

# Add to score calculation:
passed += 1 if sentiment['sentiment_score'] >= 7 else 0
```

## Files

- `social_sentiment.py` - Core tracker module
- `solana_alpha_hunter_v4.py` - Integrated scanner

---
Created: 2026-02-15
Version: 4.0 Social Sentiment
