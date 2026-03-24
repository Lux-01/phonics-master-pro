# 🎯 Stage 9: Semi-Autonomous Trading

**Status:** IMPLEMENTED  
**Mode:** SUPERVISED (User approval required)  
**Bridge:** Stage 7 Virtual → Stage 10 Full Auto  

---

## Overview

Stage 9 is the **human-in-the-loop** approach to autonomous trading:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   System    │     │  Proposal   │     │    User     │     │  Execution  │
│   Scouts    │────>│  Generated  │────>│  Approves   │────>│  Automated  │
│Opportunities│     │             │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

**Key Insight:** Before going full auto (Stage 10), the system proves itself through user-approved trades.

---

## How It Works

### 1. Continuous Monitoring
- Agency system scans for Grade A/A+ opportunities
- Validates against safety rules
- Checks if already traded

### 2. Proposal Generation
- Creates detailed trade proposal
- Risk assessment (LOW/MEDIUM/HIGH)
- Entry/exit plan
- Expiration timer (30 minutes)

### 3. User Approval
- System presents proposal to user
- User reviews: token, grade, risk, plan
- User responds: **APPROVE**, **REJECT**, or **MODIFY**

### 4. Automated Execution
- On APPROVE: System executes via Jupiter API
- On REJECT: Opportunity skipped
- Trade tracked until exit

### 5. Outcome Learning
- Trade result logged to ALOE
- Pattern learning from success/failure
- Scanner accuracy improves over time

---

## Safety (CANNOT BE DISABLED)

| Limit | Value | Enforcement |
|-------|-------|-------------|
| Max daily trades | 5 | Hard stop |
| Max daily loss | 0.5 SOL | Hard stop |
| Max position | 0.1 SOL | Per trade |
| Min liquidity | $10,000 | Auto-filter |
| Cooldown | 60 minutes | Between trades |
| Grade requirement | A or A+ | Auto-filter |

---

## Commands

### Check for Opportunities
```bash
cd /home/skux/.openclaw/workspace/agents/lux_trader
./run_stage9.sh check
```
Scans for Grade A/A+ signals and generates proposal if found.

### Approve a Trade
```bash
# Approve specific proposal
./run_stage9.sh approve prop_20260320_164530

# Approve latest pending
./run_stage9.sh approve-latest
```

### Reject a Trade
```bash
./run_stage9.sh reject prop_20260320_164530
```

### Check Status
```bash
./run_stage9.sh status
```
Shows:
- Daily trade count
- Pending proposals
- Recent trade history

---

## Proposal Format

```
======================================================================
🎯 TRADE PROPOSAL - AWAITING APPROVAL
======================================================================

📊 Token: TokenName ($SYMBOL)
   Grade: A+
   Market Cap: $45,000
   Liquidity: $18,000
   Age: 4.5 hours

💰 Trade Details:
   Entry Size: 0.1 SOL
   Target: +15%
   Stop Loss: -7%
   Time Stop: 4 hours

🛡️ Risk Assessment: MEDIUM
   Recommendation: ACCEPTABLE_WITH_LIMITS
   Risks:
     • Token may have passed early momentum phase
   Mitigation: Position size limited to 0.1 SOL, Stop loss at -7%

⏰ Expires: 2026-03-20T17:15:30

======================================================================
💬 Respond with:
   APPROVE - Execute this trade
   REJECT  - Skip this opportunity
   MODIFY  - I want to adjust something
======================================================================
```

---

## Files

| File | Purpose |
|------|---------|
| `luxtrader_stage9_semi.py` | Main Stage 9 implementation (16KB) |
| `run_stage9.sh` | Launcher script |
| `stage9_state.json` | System state |
| `stage9_proposals.json` | Pending + history |
| `stage9_trades.json` | Trade records |
| `logs/stage9.log` | Activity log |

---

## Flow Diagram

```
┌─────────────────┐
│  Agency System  │ (Already running)
│  PID 131061     │
└────────┬────────┘
         │
    ┌────▼────┐
    │  Scan   │ Every cycle
    └────┬────┘
         │
    ┌────▼────┐
    │ Grade   │ A/A+ check
    │ A+?     │
    └────┬────┘
         │
    ┌────▼────┐
    │Generate │ Risk assessment
    │Proposal │ + trade plan
    └────┬────┘
         │
    ┌────▼──────────┐
    │  User Prompt  │ Display proposal
    └────┬──────────┘
         │
    ┌────▼────┐
    │APPROVE? │ ◄── User decision
    └────┬────┘
         │
     ┌───┴───┐
     │       │
     ▼       ▼
┌────────┐  ┌────────┐
│Execute │  │ Skip   │
│ Trade  │  │        │
└───┬────┘  └────────┘
    │
┌───▼────────┐
│Monitor Exit│ Track P&L
│Conditions  │
└───┬────────┘
    │
┌───▼────────┐
│Log Outcome │ → ALOE learning
└────────────┘
```

---

## Roadmap

**Stage 9 (You are here):**
- ✅ Semi-autonomous trading
- ✅ User approval required
- ✅ Auto-execution on approval
- ✅ Full safety enforcement

**Stage 10 (Next):**
- Auto-execution without approval (after threshold)
- Full autonomy with oversight
- Self-modifying parameters

---

## Why Stage 9?

Stage 9 bridges the gap between **virtual testing** and **full autonomy**:

1. **Build Trust:** You see system logic before it acts
2. **Learn Together:** System learns your preferences
3. **Safety Net:** You control execution even after agency is granted
4. **Pattern Proof:** Success rate proven before full auto

**After 10 successful approved trades → Stage 10 unlocks**

---

## Wallet

**Address:** `8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5`

This wallet is connected but Stage 9 only executes with your explicit approval for each trade.

---

**Stage 9 is live and ready for the first approved trade.** 🚀
