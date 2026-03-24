#!/usr/bin/env python3
"""
AOE (Autonomous Opportunity Engine) Monitor
Continuously scans for opportunities and alerts on high scores.
"""

import json
import requests
import time
from datetime import datetime
from pathlib import Path

# Configuration
MIN_SCORE_ALERT = 82  # Immediate alert threshold
MIN_SCORE_QUEUE = 75  # Add to queue threshold
SCORE_COMPONENTS = {
    "potential": 0.25,
    "probability": 0.25,
    "speed": 0.15,
    "fit": 0.15,
    "alpha": 0.20,
    "risk": -0.20,
    "effort": -0.10
}

# File paths
STATE_FILE = Path("/home/skux/.openclaw/workspace/memory/aoe_state.json")
QUEUE_FILE = Path("/home/skux/.openclaw/workspace/memory/aoe_queue.json")
ALERT_LOG = Path("/home/skux/.openclaw/workspace/memory/aoe_alerts.log")

def load_state():
    """Load AOE state"""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "lastCheck": 0,
        "totalScanned": 0,
        "alertsSent": 0,
        "queueSize": 0
    }

def save_state(state):
    """Save AOE state"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def load_queue():
    """Load opportunity queue"""
    if QUEUE_FILE.exists():
        with open(QUEUE_FILE) as f:
            return json.load(f)
    return {"opportunities": [], "lastUpdated": datetime.now().isoformat()}

def save_queue(queue):
    """Save opportunity queue"""
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    queue["lastUpdated"] = datetime.now().isoformat()
    with open(QUEUE_FILE, 'w') as f:
        json.dump(queue, f, indent=2)

def log_alert(message):
    """Log alert to file"""
    ALERT_LOG.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ALERT_LOG, 'a') as f:
        f.write(f"[{timestamp}] {message}\n")

def fetch_dexscreener_boosted():
    """Fetch trending/boosted tokens from DexScreener"""
    try:
        # Get latest token profiles
        resp = requests.get(
            "https://api.dexscreener.com/token-profiles/latest/v1",
            timeout=10
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"Error fetching token profiles: {e}")
    return []

def fetch_solana_pairs():
    """Fetch Solana pairs with filtering"""
    try:
        # Search for Solana pairs with volume
        resp = requests.get(
            "https://api.dexscreener.com/latest/dex/search?q=solana",
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            pairs = data.get("pairs", [])
            
            # Filter for interesting pairs
            interesting = []
            for p in pairs:
                if p.get("chainId") != "solana":
                    continue
                    
                mc = p.get("marketCap", 0) or 0
                vol24 = p.get("volume", {}).get("h24", 0) or 0
                liquidity = p.get("liquidity", {}).get("usd", 0) or 0
                
                # Minimum criteria
                if mc < 500_000 or vol24 < 50_000:
                    continue
                if liquidity < 20_000:
                    continue
                    
                interesting.append({
                    "address": p["baseToken"].get("address", ""),
                    "symbol": p["baseToken"].get("symbol", "X"),
                    "name": p["baseToken"].get("name", ""),
                    "chainId": p.get("chainId"),
                    "dexId": p.get("dexId"),
                    "mc": mc,
                    "vol24": vol24,
                    "liquidity": liquidity,
                    "priceChange": p.get("priceChange", {}),
                    "txns": p.get("txns", {}),
                    "url": p.get("url", "")
                })
            
            # Sort by volume
            interesting.sort(key=lambda x: x["vol24"], reverse=True)
            return interesting[:20]
    except Exception as e:
        print(f"Error fetching pairs: {e}")
    return []

def score_opportunity(token):
    """Score a token opportunity (0-100)"""
    score = 0
    breakdown = {}
    
    mc = token.get("mc", 0)
    vol24 = token.get("vol24", 0)
    liq = token.get("liquidity", 0)
    price_change = token.get("priceChange", {})
    txns = token.get("txns", {})
    
    # 1. Potential (25%)
    # Based on market cap tier
    if mc < 1_000_000:
        potential = 85
    elif mc < 10_000_000:
        potential = 75
    elif mc < 50_000_000:
        potential = 60
    else:
        potential = 45
    breakdown["potential"] = potential
    score += potential * SCORE_COMPONENTS["potential"]
    
    # 2. Probability (25%)
    # Based on volume/mc ratio and transaction health
    vol_mc_ratio = vol24 / mc if mc > 0 else 0
    if vol_mc_ratio > 0.5:
        probability = 85
    elif vol_mc_ratio > 0.2:
        probability = 75
    elif vol_mc_ratio > 0.1:
        probability = 60
    else:
        probability = 45
    breakdown["probability"] = probability
    score += probability * SCORE_COMPONENTS["probability"]
    
    # 3. Speed (15%)
    # Time sensitivity based on momentum
    h1_change = price_change.get("h1", 0)
    h24_change = price_change.get("h24", 0)
    
    if h1_change > 20:
        speed = 90  # Breaking out now
    elif h1_change > 10:
        speed = 80
    elif h1_change > 5:
        speed = 70
    elif h1_change < -5:
        speed = 75  # Dip opportunity
    else:
        speed = 50
    breakdown["speed"] = speed
    score += speed * SCORE_COMPONENTS["speed"]
    
    # 4. Fit (15%)
    # Alignment with user's strategy
    # Mean reversion strategy prefers dips
    if -15 < h1_change < -5:
        fit = 95  # Perfect entry zone
    elif -5 <= h1_change < 5:
        fit = 75  # In consolidation
    elif 5 <= h1_change < 15:
        fit = 60  # Chasing
    else:
        fit = 40
    breakdown["fit"] = fit
    score += fit * SCORE_COMPONENTS["fit"]
    
    # 5. Alpha (20%)
    # Information edge
    liq_mc_ratio = liq / mc if mc > 0 else 0
    if liq_mc_ratio > 0.3 and mc < 10_000_000:
        alpha = 85  # Good liquidity for size
    elif liq_mc_ratio > 0.2:
        alpha = 75
    else:
        alpha = 50
    breakdown["alpha"] = alpha
    score += alpha * SCORE_COMPONENTS["alpha"]
    
    # 6. Risk penalty (-20%)
    risk_factors = []
    
    # High volatility risk
    if abs(h24_change) > 50:
        risk = 90
        risk_factors.append("High volatility")
    elif abs(h24_change) > 30:
        risk = 70
        risk_factors.append("Moderate volatility")
    else:
        risk = 40
    
    # Low liquidity risk
    if liq < 50_000:
        risk += 20
        risk_factors.append("Low liquidity")
    
    breakdown["risk"] = min(100, risk)
    score -= min(100, risk) * abs(SCORE_COMPONENTS["risk"])
    
    # 7. Effort penalty (-10%)
    # Quick trade = low effort
    effort = 20  # All crypto trades are relatively quick
    breakdown["effort"] = effort
    score -= effort * abs(SCORE_COMPONENTS["effort"])
    
    # Normalize to 0-100
    final_score = max(0, min(100, int(score)))
    
    # Determine grade
    if final_score >= 90:
        grade = "A+"
    elif final_score >= 80:
        grade = "A"
    elif final_score >= 70:
        grade = "B+"
    elif final_score >= 60:
        grade = "B"
    elif final_score >= 50:
        grade = "C"
    else:
        grade = "D"
    
    return {
        "score": final_score,
        "grade": grade,
        "breakdown": breakdown,
        "risk_factors": risk_factors,
        "timestamp": datetime.now().isoformat()
    }

def format_alert(opportunity, scoring):
    """Format opportunity alert"""
    score = scoring["score"]
    grade = scoring["grade"]
    token = opportunity
    
    urgency = ""
    if score >= 90:
        urgency = "🚨 URGENT"
    elif score >= 82:
        urgency = "🎯 HIGH"
    else:
        urgency = "📊 MEDIUM"
    
    price_change = token.get("priceChange", {})
    h1 = price_change.get("h1", 0)
    h24 = price_change.get("h24", 0)
    
    alert = f"""
{urgency} AOE OPPORTUNITY ALERT
Score: {score}/100 ({grade})

Token: {token.get('symbol', 'X')}
Address: {token.get('address', 'N/A')[:20]}...

METRICS:
• Market Cap: ${token.get('mc', 0):,.0f}
• 24h Volume: ${token.get('vol24', 0):,.0f}
• Liquidity: ${token.get('liquidity', 0):,.0f}
• Price Change: 1h {h1:+.1f}% | 24h {h24:+.1f}%

SCORE BREAKDOWN:
• Potential: {scoring['breakdown']['potential']}
• Probability: {scoring['breakdown']['probability']}
• Speed: {scoring['breakdown']['speed']}
• Fit: {scoring['breakdown']['fit']}
• Alpha: {scoring['breakdown']['alpha']}
• Risk: -{scoring['breakdown']['risk']}

RISK FACTORS: {', '.join(scoring['risk_factors']) if scoring['risk_factors'] else 'None'}

ACTION: {'Analyze immediately - fits your strategy' if score >= 82 else 'Queue for review'}

View: {token.get('url', 'N/A')}
"""
    return alert

def run_aoe_scan():
    """Main AOE scan function"""
    print("🎯 AOE Opportunity Engine Starting...")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    state = load_state()
    queue = load_queue()
    
    alerts_generated = []
    
    # Fetch opportunities
    print("\n📡 Scanning DexScreener...")
    tokens = fetch_solana_pairs()
    print(f"   Found {len(tokens)} candidates")
    
    # Score each opportunity
    for token in tokens:
        symbol = token.get("symbol", "X")
        print(f"\n   Scoring {symbol}...", end=" ")
        
        scoring = score_opportunity(token)
        score = scoring["score"]
        
        print(f"Score: {score} ({scoring['grade']})")
        
        # Add to results
        opp = {
            "token": token,
            "scoring": scoring,
            "detected": datetime.now().isoformat()
        }
        
        # Check thresholds
        if score >= MIN_SCORE_ALERT:
            # Immediate alert
            alert_msg = format_alert(token, scoring)
            print(f"\n   🚨 ALERT SENT (Score {score})")
            alerts_generated.append(alert_msg)
            log_alert(f"ALERT: {symbol} Score {score}")
            state["alertsSent"] += 1
            
        elif score >= MIN_SCORE_QUEUE:
            # Add to queue
            queue["opportunities"].append(opp)
            print(f"   📥 Added to queue")
            state["queueSize"] += 1
    
    # Keep queue at reasonable size
    queue["opportunities"] = queue["opportunities"][-50:]
    state["queueSize"] = len(queue["opportunities"])
    
    # Update state
    state["lastCheck"] = int(time.time())
    state["totalScanned"] += len(tokens)
    save_state(state)
    save_queue(queue)
    
    print("\n" + "=" * 50)
    print("📊 SCAN SUMMARY")
    print(f"   Tokens scanned: {len(tokens)}")
    print(f"   High alerts: {len(alerts_generated)}")
    print(f"   Queue size: {state['queueSize']}")
    print(f"   Total alerts sent: {state['alertsSent']}")
    print("=" * 50)
    
    return alerts_generated

if __name__ == "__main__":
    alerts = run_aoe_scan()
    
    # Print alerts for cron capture
    if alerts:
        print("\n" + "🚨" * 25)
        for alert in alerts:
            print(alert)
        print("🚨" * 25)
        exit(0)  # Signal that alerts were found
    else:
        print("\n✅ No high-score opportunities found this scan.")
        exit(1)  # Signal no alerts
