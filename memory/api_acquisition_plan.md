# API Acquisition Plan - Gold Coast Master Plan
**Date:** 2026-03-22
**Purpose:** Enable automated systems to reach $3.5-5.5M goal

---

## Priority Matrix

| API | Priority | Cost | Time to Value | ROI | Setup Difficulty |
|-----|----------|------|---------------|-----|------------------|
| Jupiter API | 🔴 CRITICAL | Free | Immediate | 10x | Easy |
| Jito Labs | 🔴 HIGH | Variable | Immediate | 5x | Medium |
| Twitter/X API | 🟡 HIGH | Free/Paid | 1-2 weeks | 8x | Medium |
| CoinGecko | 🟡 MEDIUM | Free | Immediate | 3x | Easy |
| Helius (Full) | 🟡 MEDIUM | Free/Paid | Immediate | 4x | Easy |
| Substack | 🟢 LOW | Free | 1 month | 6x | Easy |
| Stripe | 🟢 LOW | Per-transaction | 2-3 months | 10x | Hard |
| YouTube API | 🟢 LOW | Free | 2-4 weeks | 5x | Hard |

---

## Tier 1: Essential (Get These First)

### 1. Jupiter API [CRITICAL]
**Purpose:** Execute trades programmatically when scanner finds Grade A+
**Impact:** Scale from manual → 20+ trades/day
**Cost:** FREE
**Signup:** https://station.jup.ag/docs/apis

**What it enables:**
- Auto-buy when scanner signals A+
- Auto-sell at +15% profit target
- Scale position sizes automatically
- Reduce emotional trading

**Action Items:**
- [ ] Signup for Jupiter API key
- [ ] Store key: `cd ~/.config/jupiter && echo "key" > api_key`
- [ ] Create execution wrapper
- [ ] Test with 0.001 SOL trade
- [ ] Connect to scanner alerts

---

### 2. Jito Labs [HIGH]
**Purpose:** MEV protection, prevents frontrunning
**Impact:** Save 1-3% per trade in slippage
**Cost:** Usage-based (~0.00002 SOL per tx)
**Signup:** https://www.jito.wtf/

**What it enables:**
- Submit transactions with MEV protection
- Faster execution
- Less slippage on big moves

**Action Items:**
- [ ] Request Jito API access
- [ ] Install jito-py client
- [ ] Test MEV-protected swap
- [ ] Compare slippage vs direct Jupiter

---

## Tier 2: Growth Accelerators

### 3. Twitter/X API [HIGH]
**Purpose:** Auto-post trade results, build audience
**Impact:** Audience → Course sales → $5K-10K/month
**Cost:** Free tier = 500 tweets/month, Basic = $100/month
**Signup:** https://developer.twitter.com/

**What it enables:**
- Post "Trade #1: +15% ✅" automatically
- Build following: Target 300 by Month 5
- Authority = course sales
- Social proof for trading system

**Action Items:**
- [ ] Apply for developer account
- [ ] Create bot @AgentLuxTheClaw
- [ ] Test tweet on Moltbook first
- [ ] Build "transparent trading" content strategy

---

### 4. CoinGecko API [MEDIUM]
**Purpose:** Backup price data source
**Impact:** Catch tokens DexScreener misses
**Cost:** Free tier = 10-30 calls/min
**Signup:** https://www.coingecko.com/en/api

**What it enables:**
- Cross-reference prices
- Get market cap data
- Token metadata

---

### 5. Helius Premium [MEDIUM]
**Purpose:** Enhanced RPC, wallet tracking, events
**Impact:** Better wallet monitoring for Whale Tracker
**Cost:** Free tier available, paid starts at $50/month
**Signup:** https://helius.xyz/

**What it enables:**
- Real-time wallet webhook alerts
- Transaction parsing
- Better than free tier limits

---

## Tier 3: Future Income Streams

### 6. Stripe API [LOW - Phase 2]
**Purpose:** Payment processing for courses
**Impact:** Automated revenue collection
**Cost:** 2.9% + $0.30 per transaction
**Signup:** https://stripe.com/

**Timeline:** Month 4 (Course launch)

---

### 7. Substack API [LOW - Phase 2]
**Purpose:** Newsletter automation
**Impact:** Email list for course marketing
**Cost:** FREE
**Signup:** https://substack.com/

**Timeline:** Month 5 (Audience building)

---

### 8. YouTube API [LOW - Phase 3]
**Purpose:** Auto-upload trade recaps
**Impact:** Authority building, long-term SEO
**Cost:** FREE
**Signup:** https://developers.google.com/youtube/

**Timeline:** Month 5+ (Content creation phase)

---

## Acquisition Schedule

### This Week (March 22-28)
| Day | Task | API |
|-----|------|-----|
| Sunday | Signup + Integration | Jupiter API |
| Monday | Test + Document | Jito Labs |
| Tuesday | Create bot account | Twitter API |

### Month 1 (March-April)
- Jupiter: Execute 10+ automated trades
- Jito: MEV testing complete
- Twitter: Post trades daily

### Month 4+ (June+)
- Stripe: Course payment processing
- Substack: Newsletter launched
- YouTube: First trade recap uploaded

---

## API Key Storage

All keys stored in:
- `~/.config/[service]/api_key` (private)
- Referenced in TOOLS.md (public reference)
- Never committed to git
- Encrypted at rest

---

## Integration Plan

Each API gets:
1. Wrapper module (`apis/jupiter_client.py`)
2. Config file (`config/jupiter.yaml`)
3. Test script (`tests/test_jupiter.py`)
4. Documentation (`docs/jupiter_integration.md`)

---

## Expected ROI

**Trade Execution APIs (Jupiter + Jito):**
- Input: $300 capital
- Output: $3K by Month 1 end
- ROI: 10x via automation + reduced slippage

**Audience Building APIs (Twitter):**
- Input: Time ($100/month opportunity cost)
- Output: 300 followers → 10 course sales = $2,970
- ROI: 30x

**Payment APIs (Stripe):**
- Input: 2.9% fee
- Output: $5K-10K/month automated revenue
- ROI: Indefinite (infinite with scale)

---

## Next Actions

**Start with Jupiter API - this unlocks everything else:**
1. Go to https://station.jup.ag/docs/apis
2. Get free API key
3. Share key with me ([encrypt])
4. I'll build integration tonight

**Then:**
- Jito Labs (MEV protection)
- Twitter bot (audience building)

---

## Questions for You

1. **Jupiter API** - Ready to signup now and share key?
2. **Twitter Bot** - Want me to create account or use existing?
3. **Jito Labs** - Priority or skip for now?
4. **Paid APIs** - Sticking with free tiers until revenue, or invest now?

---

**Status:** Awaiting go-ahead on Jupiter API signup
**Impact:** Unlocks automated trading = fastest path to Gold Coast
