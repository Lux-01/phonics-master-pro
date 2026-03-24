#!/usr/bin/env python3
"""
Telegram Alert Sender for Solana Alpha Hunter v5.1
Sends Grade A/A+ alerts with copyable contract addresses
"""

import json
import requests
import sys

# Telegram bot token (replace with actual token or use env var)
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID = "6610224534"

def load_results():
    try:
        with open('/home/skux/.openclaw/workspace/alpha_results_v51.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load results: {e}")
        return []

def escape_markdown(text):
    """Escape special characters for Telegram MarkdownV2"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

def send_grade_a_alert(token):
    """Send a Grade A alert with copy button for CA"""
    
    ca = token['ca']
    grade_display = token['grade'].replace('✅', 'A').strip()
    
    # Format CA with code block for easy copying
    message_text = f"""🚨 SOLANA ALPHA ALERT

🎯 Grade: {grade_display}
📊 Score: {token['score']}/16
💰 MCAP: ${token['mcap']/1000:.1f}K | Liq: ${token['liq']/1000:.1f}K
👥 Holders: {token['holders']} | Top10: {token['top10_pct']:.1f}%
🛡️ Wallet Health: {token['wallet_health']:.0f}%

Tap to copy CA below 👇

`{ca}`"""

    # Try sending copy button (if supported)
    keyboard = {
        "inline_keyboard": [
            [{
                "text": "📋 Copy CA",
                "copy_text": {"text": ca}
            }]
        ]
    }
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message_text,
        "parse_mode": "Markdown",
        "reply_markup": json.dumps(keyboard),
        "disable_web_page_preview": True
    }
    
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code == 200:
            print(f"✅ Alert sent: {ca[:20]}...")
            return True
        else:
            print(f"⚠️ Failed: {r.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def send_batch_alert(tokens):
    """Send batch summary with clickable CAs"""
    
    header = "🚨 SOLANA ALPHA HUNTER v5.1\n" + "="*60 + "\n\n"
    
    # Build message with each CA formatted
    body = ""
    for i, token in enumerate(tokens, 1):
        grade_display = token['grade'].replace('✅', 'A').replace('🟡', 'B').strip()
        ca = token['ca']
        age_str = f" | Age: {token['age_hours']:.1f}h"
        
        if token['red_flags']:
            age_str += " ⚠️"
        
        body += f"""#{i} | {grade_display} | Score: {token['score']}/16
`{ca}`
MCAP: ${token['mcap']/1000:.1f}K | Liq: ${token['liq']/1000:.1f}K
Holders: {token['holders']} | Wallet Health: {token['wallet_health']:.0f}%{age_str}

"""
    
    # Add copy all button at bottom
    all_cas = "\n".join([t['ca'] for t in tokens[:4]])  # First 4 CAs
    
    keyboard = {
        "inline_keyboard": [[
            {"text": "📋 Copy All CAs", "copy_text": {"text": all_cas}}
        ], [
            {"text": "Copy CA #1", "copy_text": {"text": tokens[0]['ca']}}
        ]]
    }
    
    message_text = header + body + "━━━━━━━━━━━━━━━━━━━━━━━━\n⚠️ DYOR - v5.1 Scan"
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_text[:4096],  # Telegram limit
        "parse_mode": "Markdown",
        "reply_markup": json.dumps(keyboard) if keyboard else None,
        "disable_web_page_preview": True
    }
    
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code == 200:
            print("✅ Batch alert sent")
            return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    results = load_results()
    
    # Filter Grade A/A+
    grade_a = [r for r in results if 'A' in r['grade'] and 'F' not in r['grade']]
    
    if not grade_a:
        print("ℹ️ No Grade A/A+ tokens to alert")
        return
    
    print(f"📱 Sending {len(grade_a)} alerts...")
    
    # Send each individually with copy button
    for token in grade_a:
        send_grade_a_alert(token)
        time.sleep(0.5)  # Rate limit

if __name__ == "__main__":
    import time
    CHAT_ID = "6610224534"
    main()
