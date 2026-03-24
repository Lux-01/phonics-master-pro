#!/usr/bin/env python3
"""
🚀 ISEE Summary Report
Top income opportunities from Income Stream Expansion Engine
"""

import json
from datetime import datetime

# Load opportunities
with open('/home/skux/.openclaw/workspace/memory/isee/opportunities.json', 'r') as f:
    data = json.load(f)

opportunities = data.get('opportunities', [])

# Filter by status and sort by potential
active = [o for o in opportunities if o.get('status') in ['proposed', 'analyzed']]
top = sorted(active, key=lambda x: x.get('potential_monthly', 0), reverse=True)[:15]

print("="*80)
print("🔥 ISEE - TOP INCOME OPPORTUNITIES")
print("="*80)
print(f"Total Opportunities: {len(opportunities)}")
print(f"Active/Proposed: {len(active)}")
print(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("="*80)

print("\n📊 TOP 15 OPPORTUNITIES BY MONTHLY POTENTIAL:\n")

for i, opp in enumerate(top, 1):
    status_emoji = {
        'proposed': '📝',
        'analyzed': '🔍',
        'discovered': '💡',
        'built': '🔨',
        'active': '✅'
    }.get(opp.get('status'), '❓')
    
    cat_emoji = {
        'services': '🛠️',
        'digital-products': '💾',
        'content': '📝',
        'crypto': '₿',
        'ai': '🤖'
    }.get(opp.get('category'), '📦')
    
    print(f"{i}. {status_emoji} {cat_emoji} {opp.get('name', 'N/A')}")
    print(f"   Category: {opp.get('category', 'N/A').upper()}")
    print(f"   Potential: ${opp.get('potential_monthly', 0):,}/mo | Confidence: {opp.get('confidence', 0)}%")
    print(f"   Time to Revenue: {opp.get('time_to_revenue', 'N/A')} | Effort: {opp.get('effort_required', 'N/A')}")
    print(f"   Skills: {', '.join(opp.get('skill_requirements', [])[:3])}")
    print(f"   Status: {opp.get('status', 'N/A')}")
    print()

# Summary by category
print("\n" + "="*80)
print("📈 SUMMARY BY CATEGORY:")
print("="*80)

from collections import defaultdict
by_cat = defaultdict(lambda: {'count': 0, 'potential': 0})
for opp in active:
    cat = opp.get('category', 'unknown')
    by_cat[cat]['count'] += 1
    by_cat[cat]['potential'] += opp.get('potential_monthly', 0)

for cat, data in sorted(by_cat.items(), key=lambda x: x[1]['potential'], reverse=True):
    print(f"{cat.upper():20} | {data['count']:3} ops | ${data['potential']:,}/mo potential")

total_potential = sum(o.get('potential_monthly', 0) for o in active)
print("="*80)
print(f"TOTAL POTENTIAL: ${total_potential:,}/mo from {len(active)} opportunities")
print("="*80)

print("\n💡 NEXT STEPS:")
print("   1. Pick 2-3 high-confidence opportunities")
print("   2. Run: python3 isee.py --mode deep --id ISEE-XXXXX")
print("   3. Build workflow: python3 isee.py --mode build --id ISEE-XXXXX")
print("\n🚀 Ready to expand your income!")
