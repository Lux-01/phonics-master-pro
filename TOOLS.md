# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod

### Email

- **Service:** AgentMail.to (https://www.agentmail.to/)
- **API Key:** `am_us_80e7e27111...` (stored in auth.json)
- **Inbox:** vivaciousguitar330@agentmail.to
- **Use:** AI agent email communication

### Search

- **Service:** Brave Search API (https://api.search.brave.com/)
- **API Key:** `BSAP6iq...` (stored in auth.json)
- **Use:** Web search capabilities

### Crypto Data

- **Service:** Birdeye API (https://public-api.birdeye.so/)
- **API Key:** `6335463fca7340f9a2c73eacd5a37f64` (stored in auth.json)
- **Use:** Solana token prices, OHLCV, historical data
- **Note:** Free tier has limitations; some new tokens may not have full historical data
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

---

# 🔐 MEMORY ENHANCEMENT SYSTEM - STORED CREDENTIALS

## API Keys & Credentials

### AgentMail.to (Email Service)
- **Inbox:** vivaciousguitar330@agentmail.to
- **API Key:** `am_us_80e7e27111b69fc18da22e9d4c8c3b0a` (full key in auth.json)
- **Purpose:** AI agent email communication
- **Status:** Active
- **Added:** 2026-03-22

### Brave Search API
- **API Key:** `BSAP6iqM4YZKfmuFB5C2RY2kB17ZJ` (placeholder)  
- **Purpose:** Web search capabilities
- **Note:** Requires actual API key from brave.com
- **Status:** Needs setup

### Birdeye (Solana Crypto Data)
- **API Key:** `6335463fca7340f9a2c73eacd5a37f64`
- **Purpose:** Solana token prices, OHLCV, historical data
- **Status:** Active
- **Limitations:** Free tier, some new tokens lack full history

### DexScreener
- **Type:** Free API (no key required)
- **Purpose:** Token screening, market data
- **Status:** Active

### Helius (Solana RPC)
- **API Key:** (in trading configs)
- **Purpose:** Wallet tracking, transactions
- **Status:** Active

### GitHub
- **Token:** `TOKEN_HIDDEN` (Option B - full scope)
- **Username:** Lux-01
- **Repo:** phonics-master-pro
- **Status:** Active ✅

---

## Preferences

### Communication
- **Name:** Tem
- **Pronouns:** Not specified
- **Timezone:** Australia/Sydney (GMT+11)
- **Location:** Sydney, Australia

### Trading
- **Preferred Position Size:** 0.01-0.02 SOL (scaling up)
- **Max Position:** 0.5 SOL
- **Stop Loss:** -7%
- **Take Profit:** +15%
- **Time Stop:** 4 hours
- **Scanner Grade:** A+ only for live trading
- **Best Hours:** 12am-8am Sydney (US market)

### Moltbook
- **Username:** LuxTheClaw
- **Profile:** https://www.moltbook.com/u/LuxTheClaw
- **Posting Style:** Casual, personal updates, crypto commentary
- **Frequency:** Infrequent but quality

---

## Important Decisions

| Date | Decision | Context | Reversible |
|------|----------|---------|------------|
| 2026-03-11 | Use ACA methodology for all code | Better quality, fewer bugs | Yes |
| 2026-03-14 | Gold Coast Master Plan | 48-month roadmap to $3.5-5M | No |
| 2026-03-20 | Activate all 5 Phase skills | Full ecosystem operational | Yes |
| 2026-03-22 | Implement Memory Enhancement Layer | Solve forgetting problem | Yes |

---

## Active Projects

| Project | Status | Key Files | Last Updated |
|---------|--------|-----------|--------------|
| Gold Coast Master Plan | ACTIVE | memory/gold_coast_master_plan.md | 2026-03-14 |
| PhonicsMaster Pro | PENDING | phonics_app/ | 2026-03-21 |
| Solana Trading | LIVE | agents/skylar/, agents/wallet_whale/ | 2026-03-20 |
| CEL Implementation | COMPLETE | skills/cognitive-enhancement-layer/ | 2026-03-22 |
| Memory Enhancement | ACTIVE | This file | 2026-03-22 |

---

## Quick Reference

### GitHub Repo URLs
- **PhonicsMaster Pro:** https://github.com/Lux-01/phonics-master-pro
- **OpenClaw Workspace:** /home/skux/.openclaw/workspace

### Important Directories
- **Skills:** /home/skux/.openclaw/workspace/skills/
- **Memory:** /home/skux/.openclaw/workspace/memory/
- **Agents:** /home/skux/.openclaw/workspace/agents/
- **Trading Data:** /home/skux/.openclaw/workspace/aoe_v2/data/

### Wallet Addresses
- **Solana Trading:** 8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5
- **Whale Wallet (Tracking):** JBhVoSaXknLocuRGMUAbuWqEsegHA8eG1wUUNM2MBYiv

---

*Last updated: 2026-03-22 by Memory Enhancement Layer*


---

## NEW API Integrations (2026-03-22)

### Jupiter API - Trade Execution
- **Purpose:** Automated trade execution based on scanner signals
- **Status:** PENDING - Need API key
- **Signup:** https://station.jup.ag/docs/apis
- **Cost:** FREE
- **Impact:** 10x trade scalability
- **Integration:** agents/apis/jupiter_client.py

### Twitter/X API - Audience Building  
- **Purpose:** Auto-post trade results, build following
- **Status:** PENDING - Need developer account
- **Signup:** https://developer.twitter.com/
- **Cost:** Free tier (500 tweets/month)
- **Impact:** 300 followers → K/month course sales
- **Integration:** agents/apis/twitter_bot.py

### CoinGecko API - Price Data Backup
- **Purpose:** Cross-reference token prices
- **Status:** PENDING (optional - works without key)
- **Signup:** https://www.coingecko.com/en/api
- **Cost:** Free tier
- **Impact:** Catch 10-15% more tokens
- **Integration:** agents/apis/coingecko_client.py

### Jito Labs API - MEV Protection
- **Purpose:** Protect trades from frontrunning
- **Status:** PENDING - Request access
- **Signup:** https://www.jito.wtf/
- **Cost:** Usage-based (~0.00002 SOL/tx)
- **Impact:** Save 1-3% slippage per trade

---

## API Impact Summary

| API | Current | With API | Impact |
|-----|---------|----------|--------|
| Jupiter | Manual | Auto | +,700/mo |
| Twitter | 0 followers | 300 followers | +,000/mo |
| CoinGecko | DexScreener only | Dual validation | Risk reduce |

Total Potential: ,800/month

Setup Priority:
1. Jupiter (5 min) → Trade execution
2. Twitter (30 min) → Audience building
3. CoinGecko (5 min) → Backup data
4. Jito (15 min) → MEV protection

---

## API Files Created (35KB)

- agents/apis/jupiter_client.py (9.6KB)
- agents/apis/twitter_bot.py (6.9KB)
- agents/apis/coingecko_client.py (7.6KB)
- agents/apis/api_manager.py (8.8KB)
- memory/api_acquisition_plan.md (5.8KB)

---

*Last updated: 2026-03-22 by API Integration System*
