#!/usr/bin/env python3
"""
Unified API Manager
Manage all APIs in one place
"""
import os
import sys
sys.path.insert(0, '/home/skux/.openclaw/workspace/agents/apis')

from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class APIConfig:
    """API Configuration"""
    name: str
    key: Optional[str]
    status: str  # active, pending, missing
    cost: str
    priority: str
    
class UnifiedAPIManager:
    """
    Unified API Manager
    
    Manages:
    - Jupiter (trade execution)
    - Twitter/X (audience building)
    - CoinGecko (price data)
    - Birdeye (Solana data - existing)
    - Jito (MEV protection)
    """
    
    def __init__(self):
        self.apis = {}
        self._load_configs()
    
    def _load_configs(self):
        """Load API configurations"""
        # Jupiter
        self.apis['jupiter'] = APIConfig(
            name="Jupiter",
            key=os.getenv("JUPITER_API_KEY"),
            status="pending" if not os.getenv("JUPITER_API_KEY") else "active",
            cost="Free",
            priority="CRITICAL"
        )
        
        # Twitter
        self.apis['twitter'] = APIConfig(
            name="Twitter/X",
            key=os.getenv("TWITTER_BEARER_TOKEN"),
            status="pending" if not os.getenv("TWITTER_BEARER_TOKEN") else "active",
            cost="Free tier",
            priority="HIGH"
        )
        
        # CoinGecko
        self.apis['coingecko'] = APIConfig(
            name="CoinGecko",
            key=os.getenv("COINGECKO_API_KEY"),  # Optional
            status="active",  # Works without key
            cost="Free",
            priority="MEDIUM"
        )
        
        # Birdeye (existing)
        self.apis['birdeye'] = APIConfig(
            name="Birdeye",
            key="6335463fca7340f9a2c73eacd5a37f64",
            status="active",
            cost="Free tier",
            priority="ACTIVE"
        )
        
        # Jito
        self.apis['jito'] = APIConfig(
            name="Jito Labs",
            key=os.getenv("JITO_API_KEY"),
            status="pending" if not os.getenv("JITO_API_KEY") else "active",
            cost="Pay per use",
            priority="MEDIUM"
        )
    
    def get_status(self) -> Dict:
        """Get all API statuses"""
        return {
            name: {
                "key_available": bool(config.key),
                "status": config.status,
                "cost": config.cost,
                "priority": config.priority
            }
            for name, config in self.apis.items()
        }
    
    def get_missing_apis(self) -> list:
        """Get list of missing APIs"""
        return [name for name, config in self.apis.items() 
                if config.status == "pending"]
    
    def get_critical_apis(self) -> list:
        """Get critical APIs that need setup"""
        return [name for name, config in self.apis.items()
                if config.priority == "CRITICAL" and config.status != "active"]
    
    def generate_setup_commands(self) -> str:
        """Generate setup commands for missing APIs"""
        commands = []
        
        commands.append("# API Setup Commands")
        commands.append("# Run these to set up environment variables")
        commands.append("")
        
        for name, config in self.apis.items():
            if config.status != "active":
                commands.append(f"# {name} - {config.priority} priority")
                commands.append(f"# {self._get_signup_url(name)}")
                env_var = name.upper() + "_API_KEY"
                commands.append(f"export {env_var}='YOUR_KEY_HERE'")
                commands.append("")
        
        return "\n".join(commands)
    
    def _get_signup_url(self, api_name: str) -> str:
        """Get signup URL for API"""
        urls = {
            "jupiter": "https://station.jup.ag/docs/apis",
            "twitter": "https://developer.twitter.com/",
            "coingecko": "https://www.coingecko.com/en/api",
            "jito": "https://www.jito.wtf/",
            "birdeye": "https://birdeye.so/"
        }
        return urls.get(api_name, "")
    
    def get_setup_instructions(self) -> Dict:
        """Get detailed setup instructions"""
        return {
            "jupiter": {
                "steps": [
                    "Go to https://station.jup.ag/docs/apis",
                    "Click 'Get API Key'",
                    "Fill in application",
                    "Copy key to environment variable",
                    "Test with: python -m jupiter_client"
                ],
                "time": "5 minutes",
                "impact": "Enables automated trading",
                "docs": "docs/jupiter_integration.md"
            },
            "twitter": {
                "steps": [
                    "Go to https://developer.twitter.com/",
                    "Create developer account",
                    "Create project + app",
                    "Generate Bearer Token",
                    "Fill in twitter_bot.py credentials"
                ],
                "time": "15-30 minutes",
                "impact": "Automated audience building",
                "docs": "agents/apis/twitter_bot.py"
            },
            "coingecko": {
                "steps": [
                    "Go to https://www.coingecko.com/en/api",
                    "Create free account",
                    "Copy API key (optional, works without)",
                    "Test with: python -m coingecko_client"
                ],
                "time": "5 minutes",
                "impact": "Backup price data",
                "docs": "agents/apis/coingecko_client.py"
            }
        }
    
    def estimate_impact(self) -> Dict:
        """Estimate impact of each API"""
        return {
            "jupiter": {
                "current_cap": "$300",
                "potential_cap": "$10,000+",
                "trades_per_day": "2 → 20+",
                "monthly_impact": "$3K+ in Month 1",
                "time_saved": "10 hours/day automation"
            },
            "twitter": {
                "current": "0 followers",
                "target": "300 followers (Month 5)",
                "course_sales": "$2,970 (10 students × $297)",
                "time_investment": "2 hours/week", 
                "monthly_impact": "$500-3000/month (Month 4+)"
            },
            "coingecko": {
                "tokens_caught": "10-15% more",
                "validation_improvement": "Reduce false signals",
                "monthly_impact": "Risk reduction"
            },
            "jito": {
                "slippage_saved": "1-3% per trade",
                "monthly_impact": "$30-100 saved in fees"
            }
        }

def show_setup_guide():
    """Display setup guide"""
    manager = UnifiedAPIManager()
    
    print("=" * 70)
    print("🚀 GOLD COAST MASTER PLAN - API SETUP GUIDE")
    print("=" * 70)
    print()
    
    # Status
    print("📊 Current API Status:")
    print("-" * 70)
    
    for name, status in manager.get_status().items():
        emoji = "✅" if status["key_available"] else "❌"
        print(f"{emoji} {name.upper():12} | Status: {status['status']:10} | Priority: {status['priority']}")
    
    print()
    
    # Critical missing
    critical = manager.get_critical_apis()
    if critical:
        print("🔴 CRITICAL APIs Missing:")
        print("-" * 70)
        for api in critical:
            print(f"  • {api.upper()}: {manager._get_signup_url(api)}")
        print()
    
    # Setup instructions
    print("📋 Detailed Setup Instructions:")
    print("-" * 70)
    
    instructions = manager.get_setup_instructions()
    for api_name, info in instructions.items():
        print(f"\n{api_name.upper()}:")
        print(f"  Time: {info['time']}")
        print(f"  Impact: {info['impact']}")
        print(f"  Steps:")
        for i, step in enumerate(info['steps'], 1):
            print(f"    {i}. {step}")
    
    print("\n" + "=" * 70)
    print("💰 IMPACT ANALYSIS:")
    print("=" * 70)
    
    impact = manager.estimate_impact()
    for api, data in impact.items():
        print(f"\n{api.upper()}:")
        for key, value in data.items():
            print(f"  • {key.replace('_', ' ').title()}: {value}")
    
    print("\n" + "=" * 70)
    print("⚡ QUICK START:")
    print("=" * 70)
    print("1. Start with Jupiter API (5 min, massive impact)")
    print("2. Add Twitter API (30 min, audience building)")
    print("3. CoinGecko as backup (5 min, nice to have)")
    print("4. Jito later when trading bigger (optional)")
    print()
    print("Ready to start? Say: 'setup Jupiter API'")
    print("=" * 70)

# Export
manager = UnifiedAPIManager()

if __name__ == "__main__":
    show_setup_guide()
