# Decision Log

**Last Updated:** 2026-03-11

---

## Index

| ID | Date | Topic | Status |
|----|------|-------|--------|
| DEC-001 | 2026-02-27 | Go Live Trading | Active |
| DEC-002 | 2026-03-08 | Solana for Trading Bot | Active |
| **DEC-003** | **2026-03-11** | **ACA for All Builds** | **Active** |

---

## DEC-001: Go Live Trading

**Date:** 2026-02-27
**Context:** Skylar strategy ready after 5-month backtest
**Decision:** Deploy live trading with real SOL

**Why:**
- +285% backtested returns with evolved rules
- 84.6% win rate
- Rules validated in 24h and 1-month tests

---

## DEC-002: Solana Over Ethereum

**Date:** 2026-03-08
**Context:** Building crypto trading bot
**Decision:** Use Solana ecosystem

**Why:**
- Lower fees ($0.001 vs $5-50)
- Faster finality (400ms vs 12s)
- Better meme coin ecosystem

---

## **DEC-003: Use ACA Methodology for All Code Builds** ⭐ NEW

**Date:** 2026-03-11
**Context:** Building Windows installer, Tem requested formal methodology
**Decision:** Use ACA for every code build

**What is ACA:**
7-step planning workflow:
1. Requirements gathering
2. Architecture design
3. Data flow planning
4. Edge case identification
5. Tool constraints analysis
6. Error handling strategy
7. Testing plan

**Why:**
- Better quality code on first attempt
- Reduces bugs and rework
- Ensures proper error handling
- Forces thinking before coding

**Consequences:**
- Takes longer initially
- Fewer bugs
- Better documentation
- Higher quality deliverables

**Reversible:** Yes  
**Revisit:** 2026-06-11

---

*Decisions tracked in memory/decisions/*
