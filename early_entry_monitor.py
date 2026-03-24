#!/usr/bin/env python3
"""
Early Entry Monitor v1.0
Scans for fresh token launches (0-1h) every 5 minutes
Alerts on Grade A candidates via Telegram
"""

import requests
import json
import time
import os
from datetime import datetime, timedelta

# Config
MIN_ALERT_SCORE = 8  # Only alert Grade A/B+
CHECK_INTERVAL = 300  # 5 minutes
SEEN_TOKENS_FILE = "/home/skux/.openclaw/workspace/memory/seen_tokens.json"
ALERT_LOG_FILE = "/home/skux/.openclaw/workspace/memory/early_alerts.json"
TELEGRAM_CHAT_ID = "6610224534"

def load_seen_tokens():
    try:
        with open(SEEN_TOKENS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_seen_tokens(seen):
    with open(SEEN_TOKENS_FILE, 'w') as f:
        json.dump(seen, f, indent=2)

def log_alert(token_data):
    try:
        with open(ALERT_LOG_FILE, 'r') as f:
            alerts = json.load(f)
    except:
        alerts = []
    
    alerts.append({
        'timestamp': datetime.now().isoformat(),
        'token': token_data
    })
    
    with open(ALERT_LOG_FILE, 'w') as f:
        json.dump(alerts, f, indent=2)

def send_telegram_alert(token):
    """Send alert to Telegram using OpenClaw messaging"""
    try:
        emoji = "🌟" if token['score'] >= 12 else "🟢" if token['score'] >= 8 else "🟡"
        
        message = f"""{emoji} **EARLY ENTRY ALERT** {emoji}

**{token['name']}** ({token['symbol']})
⚡ Grade: {'A+' if token['score'] >= 12 else 'A' if token['score'] >= 8 else 'B+'}
📊 Score: {token['score']}/20

⏰ Age: **{token['age_hours']:.2f}h** (ULTRA FRESH)
💰 MCAP: ${token['mcap']:,.0f}
📈 Vol 5m: ${token['vol_m5']:,.0f}
💧 Liq: ${token['liq']:,.0f}
💹 5m Chg: {token['m5']:+.1f}%
🛒 Buy/Sell: {token['buys']}/{token['sells']}

✅ Positives: {', '.join(token['badges'][:5])}
⚠️ Risks: {', '.join(token['risks']) if token['risks'] else 'None flagged'}

🔗 CA: `{token['ca']}`

**⚡ ACTION**: Check on RugCheck.xyz before buying!
**⏱️ Window**: Next 30-60 minutes critical
        """
        
        # Write alert file for OpenClaw to pick up
        alert_file = "/home/skux/.openclaw/workspace/memory/pending_telegram_alert.json"
        with open(alert_file, 'w') as f:
            json.dump({
                'chat_id': TELEGRAM_CHAT_ID,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"[ALERT] Queued for Telegram: {token['name']}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to queue alert: {e}")
        return False

def scan_early_tokens():
    """Scan for fresh token launches"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Scanning for early entries...")
    
    candidates = []
    
    # Get trending profiles
    try:
        url = "https://api.dexscreener.com/token-profiles/latest/v1"
        resp = requests.get(url, timeout=10)
        
        if resp.status_code == 200:
            profiles = resp.json()
            solana = [p for p in profiles if p.get('chainId') == 'solana'][:20]
            
            seen = load_seen_tokens()
            new_tokens = []
            
            for prof in solana:
                ca = prof.get('tokenAddress', '')
                if not ca or ca in seen:
                    continue
                
                try:
                    # Get pair data
                    pair_url = f"https://api.dexscreener.com/latest/dex/tokens/SOL:{ca}"
                    presp = requests.get(pair_url, timeout=5)
                    
                    if presp.status_code == 200:
                        pdata = presp.json()
                        pairs = pdata.get('pairs', [])
                        
                        if pairs and len(pairs) > 0:
                            pair = pairs[0]
                            created = pair.get('pairCreatedAt', 0)
                            
                            if created:
                                age_hours = (time.time() - created/1000) / 3600
                                
                                # ULTRA EARLY: 0-2 hours
                                if age_hours <= 2:
                                    base = pair.get('baseToken', {})
                                    name = base.get('name', '?')
                                    symbol = base.get('symbol', '?')
                                    
                                    mcap = pair.get('marketCap', 0)
                                    vol = pair.get('volume', {})
                                    vol_m5 = vol.get('m5', 0)
                                    vol_h1 = vol.get('h1', 0)
                                    liq = pair.get('liquidity', {}).get('usd', 0)
                                    
                                    pchg = pair.get('priceChange', {})
                                    m5 = pchg.get('m5', 0)
                                    h1 = pchg.get('h1', 0)
                                    
                                    tx = pair.get('txns', {})
                                    m5_buys = tx.get('m5', {}).get('buys', 0)
                                    m5_sells = tx.get('m5', {}).get('sells', 0)
                                    h1_buys = tx.get('h1', {}).get('buys', 0)
                                    h1_sells = tx.get('h1', {}).get('sells', 0)
                                    
                                    # Quick score
                                    score = 0
                                    badges = []
                                    risks = []
                                    
                                    # Age (most important for early entry)
                                    if age_hours <= 0.5:
                                        score += 5
                                        badges.append("just_launched")
                                    elif age_hours <= 1:
                                        score += 4
                                        badges.append("ultra_fresh")
                                    elif age_hours <= 2:
                                        score += 3
                                        badges.append("fresh")
                                    
                                    # Volume activity
                                    if vol_m5 > 1000:
                                        score += 4
                                        badges.append("very_hot")
                                    elif vol_m5 > 500:
                                        score += 3
                                        badges.append("heating")
                                    elif vol_m5 > 100:
                                        score += 2
                                        badges.append("warming")
                                    
                                    # Liquidity
                                    if liq > 15000:
                                        score += 3
                                        badges.append("deep_liq")
                                    elif liq > 8000:
                                        score += 2
                                        badges.append("good_liq")
                                    elif liq > 3000:
                                        score += 1
                                        badges.append("decent_liq")
                                    else:
                                        risks.append("thin_liq")
                                    
                                    # Price momentum
                                    if m5 > 50:
                                        score += 4
                                        badges.append("mooning")
                                    elif m5 > 20:
                                        score += 3
                                        badges.append("strong")
                                    elif m5 > 5:
                                        score += 2
                                        badges.append("rising")
                                    elif m5 < -20:
                                        score -= 2
                                        risks.append("early_dump")
                                    
                                    # Buy pressure
                                    if m5_buys > m5_sells * 3 and m5_buys > 10:
                                        score += 3
                                        badges.append("buy_frenzy")
                                    elif m5_buys > m5_sells * 2:
                                        score += 2
                                        badges.append("buyers_dominant")
                                    elif m5_buys > m5_sells:
                                        score += 1
                                        badges.append("buyers_win")
                                    elif m5_buys < m5_sells:
                                        score -= 1
                                        risks.append("sellers_active")
                                    
                                    # Hourly activity
                                    if vol_h1 > 10000:
                                        score += 2
                                        badges.append("high_vol")
                                    elif h1_buys > h1_sells * 1.5:
                                        score += 1
                                        badges.append("hourly_buyers")
                                    
                                    # MCAP sweet spot for early
                                    if 8000 < mcap < 80000:
                                        score += 2
                                        badges.append("good_size")
                                    elif mcap < 8000:
                                        score += 1
                                        badges.append("micro_cap")
                                    elif mcap > 200000:
                                        score -= 1
                                        badges.append("getting_big")
                                    
                                    # Red flag check - too volatile
                                    if abs(m5) > 200:
                                        score -= 3
                                        risks.append("extreme_vol")
                                    elif abs(m5) > 100:
                                        score -= 1
                                        risks.append("very_volatile")
                                    
                                    token_data = {
                                        'name': name,
                                        'symbol': symbol,
                                        'ca': ca,
                                        'age_hours': age_hours,
                                        'mcap': mcap,
                                        'vol_m5': vol_m5,
                                        'vol_h1': vol_h1,
                                        'liq': liq,
                                        'm5': m5,
                                        'h1': h1,
                                        'buys': m5_buys,
                                        'sells': m5_sells,
                                        'h1_buys': h1_buys,
                                        'h1_sells': h1_sells,
                                        'score': score,
                                        'badges': badges,
                                        'risks': risks,
                                        'dex': pair.get('dexId', '?')
                                    }
                                    
                                    new_tokens.append(token_data)
                                    
                                    # Mark as seen
                                    seen[ca] = {
                                        'name': name,
                                        'first_seen': datetime.now().isoformat(),
                                        'alerted': score >= MIN_ALERT_SCORE
                                    }
                                    
                                    # Alert immediately if high score
                                    if score >= MIN_ALERT_SCORE:
                                        print(f"🚨 GRADE A CANDIDATE: {name} (Score: {score})")
                                        send_telegram_alert(token_data)
                                        log_alert(token_data)
                                        
                except Exception as e:
                    pass
            
            # Save seen tokens
            save_seen_tokens(seen)
            
            # Print summary
            if new_tokens:
                print(f"✅ Found {len(new_tokens)} fresh tokens")
                for t in new_tokens:
                    status = "🚨 ALERTED" if t['score'] >= MIN_ALERT_SCORE else "📊 Logged"
                    print(f"   {status}: {t['name']} (Score: {t['score']}, Age: {t['age_hours']:.1f}h)")
            else:
                print("   No new launches")
                
    except Exception as e:
        print(f"[ERROR] Scan failed: {e}")

def run_monitor():
    """Main monitor loop"""
    print("=" * 80)
    print("🦞 EARLY ENTRY MONITOR v1.0 STARTED")
    print("=" * 80)
    print(f"\nCheck interval: Every 5 minutes")
    print(f"Alert threshold: Score >= {MIN_ALERT_SCORE}")
    print(f"Target window: 0-2 hours after launch")
    print(f"Telegram alerts: ENABLED")
    print(f"\nStarting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    scan_early_tokens()
    
    print("\n✅ Initial scan complete.")
    print("   Set up cron job to run every 5 minutes:")
    print("   */5 * * * * cd /home/skux/.openclaw/workspace && python3 early_entry_monitor.py")
    print("\nOr run manually: ./run_early_monitor.sh")

if __name__ == "__main__":
    run_monitor()
