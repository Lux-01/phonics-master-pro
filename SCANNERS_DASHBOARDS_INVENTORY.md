# 🎯 CRYPTO SCANNERS & DASHBOARDS INVENTORY

## Generated: 2026-03-20

---

## 🔍 SCANNER COUNT: 32 Total

### **TIER 1: Main Alpha Hunters (7 scanners)**
| # | File | Size | Version | Status |
|---|------|------|---------|--------|
| 1 | `solana_alpha_hunter.py` | 19KB | v1 | Legacy |
| 2 | `solana_alpha_hunter_v4.py` | 13KB | v4 | Legacy |
| 3 | `solana_alpha_hunter_v5.py` | 36KB | v5 | Archived |
| 4 | `solana_alpha_hunter_v51.py` | 37KB | v5.1 | Archived |
| 5 | `solana_alpha_hunter_v53.py` | 48KB | v5.3 | Archived |
| 6 | `solana_alpha_hunter_v54.py` | 47KB | v5.4 | **PRIMARY** ⭐ |
| 7 | `solana_alpha_hunter_v54_enhanced.py` | 48KB | v5.4e | **Backup** |
| 8 | `solana_alpha_hunter_v55.py` | N/A | v5.5 | Chart Analysis |

### **TIER 2: Specialized Scanners (9 scanners)**
| # | File | Purpose |
|---|------|---------|
| 9 | `alpha_scanner_v4.py` | v4 variant |
| 10 | `pump_100k_scanner.py` | Pump >$100K focus |
| 11 | `telegram_pump_scanner.py` | Telegram-integrated |
| 12 | `oscillator_scanner.py` | RSI/MACD patterns |
| 13 | `live_scanner.py` | Real-time monitoring |
| 14 | `wallet_coordination_scanner.py` | Multi-wallet tracking |
| 15 | `breakout_hunter.py` | Breakout detection |
| 16 | `solana_alpha_extended.py` | Extended features |
| 17 | `final_alpha_report.py` | Report generator |

### **TIER 3: AOE v2 Scanners (4 scanners)**
| # | File | Purpose |
|---|------|---------|
| 18 | `aoe_v2/scanner_base.py` | Base class |
| 19 | `aoe_v2/scanner_dexscreener.py` | DexScreener API |
| 20 | `aoe_v2/scanner_pumpfun.py` | Pump.fun specific |
| 21 | `aoe_v2/scanner_birdeye.py` | Birdeye API |

### **TIER 4: Trading Agent Scanners (4 scanners)**
| # | File | Location |
|---|------|----------|
| 22 | `breakout_hunter.py` | agents/lux_trader/ |
| 23 | `breakout_hunter_v2.py` | agents/lux_trader/ |
| 24 | `breakout_hunter_v22.py` | agents/lux_trader/ |
| 25 | `breakout_hunter_v3.py` | agents/lux_trader/ |

### **TIER 5: WebSocket/Real-time Scanners (2 scanners)**
| # | File | Purpose |
|---|------|---------|
| 26 | `agents/websocket_scanner/scanner_v6_simple.py` | WebSocket v6 |
| 27 | `skills/autonomous-opportunity-engine/websocket_scanner.py` | AOE WebSocket |

### **TIER 6: Skill Scanners (4 scanners)**
| # | File | Parent Skill |
|---|------|--------------|
| 28 | `skill-evolution-engine/scanner_evolver.py` | SEE |
| 29 | `code-evolution-tracker/scanner_evolution_logger.py` | CET |
| 30 | `autonomous-code-architect/scanner_architect.py` | ACA |
| 31 | `income-stream-expansion-engine/market_scanner.py` | ISE |

### **TIER 7: Quick Scanners (2 scanners)**
| # | File | Purpose |
|---|------|---------|
| 32 | `quick_scan.py` | Fast DexScreener scan |
| 33 | `birdeye_scan.py` | Birdeye quick check |

---

## 📊 DASHBOARD COUNT: 6 Total

### **Main Dashboard**
| # | File | Size | Features |
|---|------|------|----------|
| 1 | `dashboard.py` | 48KB | **PRIMARY** - Full trading dashboard |

### **Specialized Dashboards**
| # | File | Location | Purpose |
|---|------|----------|---------|
| 2 | `agents/lux_trader/emergency_dashboard.py` | lux_trader/ | Emergency stop + status |
| 3 | `agents/lux_trader/start_dashboard.py` | lux_trader/ | Startup dashboard |
| 4 | `status_dashboard.py` | root | System status only |
| 5 | `generate_dashboard.py` | root | Dashboard generator |
| 6 | `memory/generate_dashboard.py` | memory/ | Memory-focused |

---

## 🏆 RECOMMENDED CONFIGURATION

### For Live Trading (Stage 9):
```
Primary Scanner: v5.4 (solana_alpha_hunter_v54.py)
Chart Overlay: v5.5 (for technical validation)
Backup: v5.4 Enhanced
Quick Scan: quick_scan.py
Dashboard: dashboard.py
```

### For Full System Status:
```
Main Dashboard: dashboard.py
Emergency: agents/lux_trader/emergency_dashboard.py
System Status: status_dashboard.py
```

---

## 📈 SCANNER SUMMARY BY CAPABILITY

| Capability | Best Scanner | Grade Accuracy |
|------------|--------------|----------------|
| Fundamentals | v5.4 | 66.7% A/A+ |
| Chart Analysis | v5.5 | Lower (RSI impacts) |
| Speed | Live Scanner | Real-time |
| Depth | v5.4 Enhanced | Highest |
| Pattern Detection | Protected Multi-Scanner | Best |

---

## 🎮 DASHBOARD FEATURES COMPARISON

| Feature | dashboard.py | emergency_dashboard.py | status_dashboard.py |
|---------|--------------|------------------------|---------------------|
| Trade Status | ✅ | ✅ | ✅ |
| Scanner Results | ✅ | ❌ | ❌ |
| Emergency Stop | ❌ | ✅ | ❌ |
| P&L Tracking | ✅ | ✅ | ✅ |
| System Health | ✅ | ✅ | ✅ |
| Cron Status | ✅ | ❌ | ✅ |
| Wallet Status | ✅ | ✅ | ✅ |

---

Last Updated: 2026-03-20