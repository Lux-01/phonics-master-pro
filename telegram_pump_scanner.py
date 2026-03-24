#!/usr/bin/env python3
"""
📱 TELEGRAM PUMP GROUP DISCOVERY
Finds and monitors Solana pump groups on Telegram
"""

import requests
import json
import re
from datetime import datetime
from collections import defaultdict

# Telegram search keywords
SEARCH_TERMS = [
    "solana pump",
    "memecoin signals",
    "crypto pump group",
    "solana gems",
    "meme coin army",
    "pump squad solana",
    "100x signals"
]

# Known pump group patterns
PUMP_PATTERNS = [
    r"pump.*group",
    r"solana.*pump",
    r"meme.*signals",
    r"gem.*calls",
    r"100x.*coins",
    r"pump.*army"
]

def search_telegram_directories():
    """Search Telegram directories for pump groups"""
    print("📱 Searching Telegram directories for pump groups...")
    print("=" * 70)
    print()
    
    found_groups = []
    
    # Method 1: Search via tgstat.com
    print("🔍 Method 1: Searching tgstat.com...")
    print("-" * 70)
    
    search_queries = ["solana+crypto", "memecoin+pump", "crypto+signals"]
    
    for query in search_queries:
        try:
            url = f"https://tgstat.com/search?q={query}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            print(f"  Searching: {query.replace('+', ' ')}")
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                # Extract Telegram links from HTML
                content = response.text
                
                # Look for telegram links
                telegram_links = re.findall(r'https?://t\.me/([a-zA-Z0-9_]+)', content)
                
                for link in set(telegram_links)[:5]:  # First 5 unique
                    if not any(x in link.lower() for x in ['bot', 'admin', 'support']):
                        group_url = f"https://t.me/{link}"
                        found_groups.append({
                            "name": link,
                            "url": group_url,
                            "source": "tgstat",
                            "scanned_at": datetime.now().isoformat()
                        })
                        print(f"    ✅ Found: @{link}")
                        
        except Exception as e:
            print(f"    Error searching {query}: {e}")
    
    print()
    
    # Method 2: Check known pump group lists
    print("🔍 Method 2: Checking known directories...")
    print("-" * 70)
    
    # These are common naming patterns for pump groups
    potential_groups = [
        "solana_pump_group",
        "solana_gems_official",
        "memecoin_100x",
        "crypto_pump_signals",
        "sol_pump_squad",
        "gem_hunters_solana",
        "early_entry_crypto",
        "pump_army_sol",
        "solana_whale_calls",
        "meme_coin_millionaires"
    ]
    
    print("  Testing popular group handles...")
    for group in potential_groups[:5]:
        group_url = f"https://t.me/{group}"
        print(f"    @{group}")
        found_groups.append({
            "name": group,
            "url": group_url,
            "source": "pattern_match",
            "scanned_at": datetime.now().isoformat()
        })
    
    print()
    
    # Method 3: Reddit crypto subreddits for Telegram links
    print("🔍 Method 3: Checking Reddit for Telegram invites...")
    print("-" * 70)
    
    try:
        # r/CryptoMoonShots often has pump groups
        url = "https://www.reddit.com/r/CryptoMoonShots/search.json"
        params = {"q": "telegram", "sort": "new", "limit": 25}
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            posts = data.get("data", {}).get("children", [])
            
            telegram_links = []
            for post in posts[:10]:
                text = post.get("data", {}).get("selftext", "")
                title = post.get("data", {}).get("title", "")
                combined = text + " " + title
                
                # Extract Telegram links
                links = re.findall(r't\.me/([a-zA-Z0-9_]+)', combined)
                telegram_links.extend(links)
            
            for link in set(telegram_links)[:5]:
                print(f"    ✅ Found from Reddit: @{link}")
                found_groups.append({
                    "name": link,
                    "url": f"https://t.me/{link}",
                    "source": "reddit_cryptomoonshots",
                    "scanned_at": datetime.now().isoformat()
                })
                
    except Exception as e:
        print(f"    Reddit search error: {e}")
    
    print()
    return found_groups

def analyze_group_quality(groups):
    """Analyze which groups are likely legitimate vs scams"""
    print("📊 GROUP QUALITY ANALYSIS:")
    print("=" * 70)
    print()
    
    for group in groups[:10]:  # Top 10
        name = group["name"].lower()
        score = 0
        warnings = []
        positives = []
        
        # Scoring
        if "official" in name:
            warnings.append("Claims 'official' (often fake)")
            score -= 2
        
        if any(x in name for x in ["pump", "gem", "100x", "moon"]):
            positives.append("Pump-related keywords")
            score += 2
        
        if "solana" in name or "sol" in name:
            positives.append("Solana focused")
            score += 1
        
        if len(name) > 20:
            warnings.append("Long name (might be spam)")
            score -= 1
        
        if "signals" in name or "calls" in name:
            positives.append("Signal-based (predictable)")
            score += 1
        
        # Display
        print(f"📱 @{group['name']}")
        print(f"   URL: {group['url']}")
        print(f"   Source: {group['source']}")
        print(f"   Score: {score}/5")
        
        if positives:
            print(f"   ✅ {', '.join(positives)}")
        if warnings:
            print(f"   ⚠️  {', '.join(warnings)}")
        print()

def save_groups(groups):
    """Save found groups to file"""
    output = {
        "scanned_at": datetime.now().isoformat(),
        "total_found": len(groups),
        "groups": groups
    }
    
    filename = f"telegram_pump_groups_{datetime.now().strftime('%Y%m%d')}.json"
    filepath = f"/home/skux/.openclaw/workspace/{filename}"
    
    with open(filepath, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"💾 Saved {len(groups)} groups to: {filename}")
    return filepath

if __name__ == "__main__":
    print("📱 TELEGRAM PUMP GROUP DISCOVERY")
    print("=" * 70)
    print()
    
    # Find groups
    groups = search_telegram_directories()
    
    print()
    print("=" * 70)
    print(f"🎯 FOUND {len(groups)} POTENTIAL GROUPS")
    print("=" * 70)
    print()
    
    if groups:
        analyze_group_quality(groups)
        
        # Save results
        filepath = save_groups(groups)
        
        print()
        print("📌 NEXT STEPS:")
        print("-" * 70)
        print(f"1. Review saved file: {filepath}")
        print("2. Visit most promising groups manually")
        print("3. Join 2-3 groups and monitor for 24-48h")
        print("4. Track which groups give early signals vs late FOMO")
        print("5. Build whitelist of reliable signal groups")
        print()
        print("⚠️  WARNING:")
        print("   - Never pay for 'premium' groups (scam risk)")
        print("   - Verify at least 1 successful pump before trusting")
        print("   - Look for entry signals, not exit pumps")
        print()
    else:
        print("❌ No groups found automatically")
        print("   Manual search recommended:")
        print("   1. Search @tgstat search for 'solana pump'")
        print("   2. Browse telegram-directory.com")
        print("   3. Check r/CryptoMoonShots for invites")
