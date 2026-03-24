# 🚀 LuxTrader Enhanced Sell System v1.0

Complete autonomous selling solution with retry logic, tokenomics detection, and emergency controls.

## 📦 Components

### 1. **lux_enhanced_seller.py** (27KB)
Smart sell execution with dynamic slippage and multi-attempt fallbacks.

**Features:**
- Pre-sell safety checks
- Dynamic slippage calculation (1% → 10%)
- Multi-attempt execution (5 retries)
- Tokenomics integration
- Emergency exit protocols
- Detailed execution logging

### 2. **tokenomics_detector.py** (17KB)
Analyzes token contracts for risks and constraints.

**Features:**
- Transfer tax detection
- Honeypot detection
- Sell limit analysis
- LP lock verification
- Risk scoring (0-100)
- Batch analysis support

### 3. **lux_auto_sell_monitor.py** (19KB)
Enhanced position monitoring with intelligent retry logic.

**Features:**
- Real-time price monitoring
- Multi-strategy exit signals
- Intelligent retry with backoff
- Emergency exit protocols
- Telegram/Discord notifications
- Manual override capability

### 4. **emergency_dashboard.py** (22KB)
Web-based control panel for manual intervention.

**Features:**
- Real-time position display
- One-click emergency sells
- Risk level indicators
- System health status
- Mobile-responsive design

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd /home/skux/.openclaw/workspace/agents/lux_trader

# Install required packages
pip3 install --user --break-system-packages solders base58 requests websockets
```

### Step 2: Test Tokenomics Detector

```python
import asyncio
from tokenomics_detector import quick_check

# Analyze a token
async def main():
    security = await quick_check("TOKEN_ADDRESS_HERE")
    if security:
        print(f"Risk: {security.risk_level.value}")
        print(f"Tax: {security.sell_tax}%")
        print(f"Honeypot: {security.is_honeypot}")

asyncio.run(main())
```

### Step 3: Test Enhanced Seller

```python
import asyncio
from lux_enhanced_seller import quick_sell

# Sell a token
async def main():
    result = await quick_sell(
        token_address="TOKEN_ADDRESS",
        token_symbol="TOKEN",
        wallet_address="YOUR_WALLET",
        private_key="YOUR_PRIVATE_KEY",
        exit_reason="take_profit"
    )
    
    if result.success:
        print(f"Sold! Received: {result.amount_received} SOL")
    else:
        print(f"Failed: {result.error_message}")

asyncio.run(main())
```

### Step 4: Start Auto-Sell Monitor

```python
import asyncio
from lux_auto_sell_monitor import LuxAutoSellMonitor

async def main():
    # Create monitor
    monitor = LuxAutoSellMonitor(
        wallet_address="YOUR_WALLET",
        private_key="YOUR_PRIVATE_KEY"
    )
    
    # Add a position
    await monitor.add_position(
        token_address="TOKEN_ADDRESS",
        token_symbol="TOKEN",
        entry_price=0.0001,
        entry_sol=0.01
    )
    
    # Start monitoring
    await monitor.monitor_loop()

asyncio.run(main())
```

### Step 5: Start Emergency Dashboard

```python
from emergency_dashboard import start_dashboard
from lux_auto_sell_monitor import LuxAutoSellMonitor

# Create monitor
monitor = LuxAutoSellMonitor("YOUR_WALLET", "YOUR_PRIVATE_KEY")

# Start dashboard
dashboard = start_dashboard(
    wallet_address="YOUR_WALLET",
    port=7777,
    monitor=monitor
)

# Keep running
import time
while True:
    time.sleep(1)
```

Then open: **http://localhost:7777**

---

## 📊 Configuration

### Exit Triggers (in lux_auto_sell_monitor.py)

```python
CONFIG = {
    'take_profit_pct': 15,      # Sell at +15%
    'stop_loss_pct': -7,        # Sell at -7%
    'time_stop_hours': 4,       # Sell after 4 hours
    'trailing_stop_pct': 5,     # Trailing stop
}
```

### Retry Settings

```python
CONFIG = {
    'max_sell_attempts': 5,           # 5 attempts
    'retry_delay_seconds': 10,        # Start with 10s delay
    'backoff_multiplier': 2,          # Double each retry
    'slippage_increment': 100,        # +1% slippage per retry
}
```

### Notifications (Optional)

```python
CONFIG = {
    'telegram_bot_token': 'YOUR_BOT_TOKEN',
    'telegram_chat_id': 'YOUR_CHAT_ID',
    'discord_webhook': 'YOUR_WEBHOOK_URL',
}
```

---

## 🎯 Usage Examples

### Example 1: Quick Token Check

```python
from tokenomics_detector import TokenomicsDetector
import asyncio

detector = TokenomicsDetector()

async def check():
    security = await detector.analyze_token("TOKEN_ADDRESS")
    
    if security.risk_score > 50:
        print("⚠️ High risk token!")
    
    if security.is_honeypot:
        print("🚨 HONEYPOT - DO NOT BUY!")
    
    if security.sell_tax > 10:
        print(f"⚠️ High sell tax: {security.sell_tax}%")

asyncio.run(check())
```

### Example 2: Smart Sell with Fallbacks

```python
from lux_enhanced_seller import LuxEnhancedSeller
import asyncio

seller = LuxEnhancedSeller("WALLET_ADDRESS", "PRIVATE_KEY")

async def sell():
    position = {
        'price_change_24h': 20,
        'age_hours': 2,
    }
    
    result = await seller.execute_smart_sell(
        token_address="TOKEN_ADDRESS",
        token_symbol="TOKEN",
        position=position,
        exit_reason="take_profit"
    )
    
    print(f"Success: {result.success}")
    print(f"Attempts: {result.total_attempts}")
    print(f"Time: {result.execution_time_ms}ms")
    
    if result.tokenomics:
        print(f"Tax paid: {result.tokenomics.sell_tax}%")

asyncio.run(sell())
```

### Example 3: Batch Token Analysis

```python
from tokenomics_detector import TokenomicsDetector
import asyncio

detector = TokenomicsDetector()

tokens = [
    "TOKEN1_ADDRESS",
    "TOKEN2_ADDRESS",
    "TOKEN3_ADDRESS",
]

async def analyze_all():
    results = await detector.batch_analyze(tokens)
    
    for security in results:
        safe = detector.is_safe_to_trade(security, max_risk="medium")
        print(f"{security.symbol}: {security.risk_level.value} - Safe: {safe}")

asyncio.run(analyze_all())
```

### Example 4: Emergency Manual Sell

```python
from lux_auto_sell_monitor import LuxAutoSellMonitor
import asyncio

monitor = LuxAutoSellMonitor("WALLET", "PRIVATE_KEY")

# Add position
async def setup():
    await monitor.add_position("TOKEN", "SYMBOL", 0.0001, 0.01)
    
    # Later... emergency sell!
    monitor.manual_sell("TOKEN_ADDRESS")

asyncio.run(setup())
```

---

## 🛡️ Safety Features

### Pre-Sell Checks

Every sell attempt includes:
1. ✅ Token account exists
2. ✅ Has balance (accounting for transfer tax)
3. ✅ Token is tradeable (not honeypot)
4. ✅ Sufficient liquidity
5. ✅ Price fetchable
6. ✅ Tokenomics safe

### Dynamic Slippage

Slippage adjusts based on:
- Token volatility
- Liquidity level
- Transfer taxes
- Token age
- Market conditions

**Range:** 1% → 10% (configurable)

### Emergency Exit Strategies

If normal sell fails:
1. Try selling to USDC instead of SOL
2. Try selling 50% instead of 100%
3. Try selling 25% instead of 100%
4. Use maximum slippage (10%)
5. Use highest priority fee

---

## 📈 Monitoring & Alerts

### Dashboard Access

```
http://localhost:7777
```

**Features:**
- Real-time position P&L
- Risk level indicators
- One-click sell buttons
- Emergency sell all
- System status

### Telegram Notifications

Set in config:
```python
CONFIG['telegram_bot_token'] = 'YOUR_BOT_TOKEN'
CONFIG['telegram_chat_id'] = 'YOUR_CHAT_ID'
```

**Alerts sent:**
- Position sold
- Emergency exit triggered
- Sell failed after all retries
- System errors

### Discord Notifications

Set in config:
```python
CONFIG['discord_webhook'] = 'YOUR_WEBHOOK_URL'
```

---

## 🔧 Troubleshooting

### Issue: "No module named 'solders'"

```bash
pip3 install --user --break-system-packages solders
```

### Issue: "Private key not found"

Create secure key storage:
```python
from secure_key_manager import SecureKeyManager

manager = SecureKeyManager()
manager.save_key("YOUR_PRIVATE_KEY")
```

### Issue: "Quote failed"

- Check token has liquidity
- Increase slippage tolerance
- Try again later (network congestion)

### Issue: "Sell failed after 5 attempts"

- Token may be honeypot
- Check tokenomics detector output
- Try emergency exit via dashboard
- May need to wait for liquidity

---

## 📊 Performance Metrics

### Target Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Sell Success Rate | >95% | ~60% |
| Avg Slippage | <3% | ~1% |
| Avg Sell Time | <30s | >2min |
| Emergency Exits | <5% | N/A |

### Statistics Tracked

- Total sells attempted
- Successful sells
- Failed sells
- Emergency exits
- Average slippage used
- Average attempts per sell
- Total P&L
- Success rate by token type

---

## 🔐 Security Notes

1. **Never share your private key**
2. **Use secure key storage** (secure_key_manager.py)
3. **Test on small amounts first**
4. **Monitor all transactions**
5. **Keep dashboard behind firewall**

---

## 📝 Files Created

| File | Size | Purpose |
|------|------|---------|
| lux_enhanced_seller.py | 27KB | Smart sell execution |
| tokenomics_detector.py | 17KB | Token risk analysis |
| lux_auto_sell_monitor.py | 19KB | Position monitoring |
| emergency_dashboard.py | 22KB | Web control panel |
| SELL_SYSTEM_README.md | This file | Documentation |

---

## 🎓 Next Steps

1. **Test on paper trading first**
2. **Start with small amounts (0.001 SOL)**
3. **Monitor success rates**
4. **Adjust slippage settings**
5. **Scale up gradually**

---

## 💡 Tips

- **Always check tokenomics before buying**
- **Set realistic slippage (2-3% for meme coins)**
- **Use trailing stops in volatile markets**
- **Keep emergency dashboard open during trading**
- **Review failed sells to improve strategy**

---

## 🆘 Support

If you encounter issues:
1. Check logs in `monitor_state.json`
2. Review `sell_history.json`
3. Test token with `tokenomics_detector.py`
4. Try manual sell via dashboard

---

**Ready to trade smarter! 🚀**
