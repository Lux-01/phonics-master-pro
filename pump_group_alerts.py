#!/usr/bin/env python3
"""
🚨 PUMP GROUP ALERT SYSTEM
Notifies when new pump groups are detected or when known groups post signals
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Known good pump groups (to be populated over time)
WHITELISTED_GROUPS = [
    # Add groups that prove themselves here
]

# Known scams (avoid these)
BLACKLISTED_GROUPS = [
    "pump_dump_scam",
    "fake_solana_gems"
]

def check_new_groups():
    """Check for new groups found today"""
    today = datetime.now().strftime('%Y%m%d')
    filename = f"telegram_pump_groups_{today}.json"
    
    if not os.path.exists(filename):
        print("No scan results found for today")
        return []
    
    with open(filename) as f:
        data = json.load(f)
    
    groups = data.get('groups', [])
    
    # Filter out existing known groups
    new_groups = []
    for group in groups:
        name = group.get('name', '')
        if name not in WHITELISTED_GROUPS and name not in BLACKLISTED_GROUPS:
            new_groups.append(group)
    
    return new_groups

def generate_alert():
    """Generate alert message for new groups"""
    new_groups = check_new_groups()
    
    if not new_groups:
        return None
    
    alert = f"""
🚨 NEW PUMP GROUPS DETECTED! 🚨

Found {len(new_groups)} new potential pump groups:

"""
    
    for i, group in enumerate(new_groups[:5], 1):
        alert += f"{i}. @{group['name']}\n"
        alert += f"   URL: {group['url']}\n"
        alert += f"   Source: {group['source']}\n\n"
    
    alert += """
⚠️  ACTION REQUIRED:
1. Visit these groups manually
2. Check their recent message history
3. Look for proof of past successful pumps
4. Join 1-2 most promising groups
5. Monitor for 24h before trusting signals

💡 TIP: Best groups have:
- 100-1000 members (not too big)
- Recent successful pump proof (PNL screenshots)
- Entry calls 2-5 mins before price moves
- No paid 'premium' tiers
"""
    
    return alert

def save_alert(alert_text):
    """Save alert to file for delivery"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    filename = f"pump_alert_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write(alert_text)
    
    return filename

if __name__ == "__main__":
    print("🚨 Checking for new pump groups...")
    
    alert = generate_alert()
    
    if alert:
        print(alert)
        filename = save_alert(alert)
        print(f"📢 Alert saved: {filename}")
        
        # Return exit code 1 if new groups found (for cron detection)
        exit(1)
    else:
        print("✅ No new groups found today")
        exit(0)
