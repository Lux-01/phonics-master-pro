#!/usr/bin/env python3
"""
Twitter/X API Bot
Auto-post trade results and build audience
"""
import requests
import json
from datetime import datetime
from typing import Optional, List

class TwitterBot:
    """
    Twitter/X bot for automated posting
    
    Features:
    - Post trade results
    - Thread generation
    - Scheduled posts
    - Engagement tracking
    """
    
    def __init__(self, 
                 bearer_token: str,
                 api_key: str,
                 api_secret: str,
                 access_token: str,
                 access_secret: str):
        self.bearer_token = bearer_token
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_secret = access_secret
        
        self.base_url = "https://api.twitter.com/2"
        self.media_url = "https://upload.twitter.com/1.1/media/upload.json"
        
    def post_tweet(self, 
                   text: str,
                   reply_to: Optional[str] = None) -> dict:
        """
        Post a tweet
        
        Args:
            text: Tweet content (max 280 chars)
            reply_to: Tweet ID to reply to (for threads)
        
        Returns:
            API response with tweet ID
        """
        url = f"{self.base_url}/tweets"
        
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
        
        payload = {"text": text}
        if reply_to:
            payload["reply"] = {"in_reply_to_tweet_id": reply_to}
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def post_trade_result(self,
                         trade_num: int,
                         token: str,
                         profit_pct: float,
                         pnl: float,
                         entry_time: str,
                         exit_time: str,
                         grade: str = "A+") -> dict:
        """
        Post formatted trade result
        
        Template:
        "Trade #1: $TOKEN +15% ✅
        Grade: A+ | Time: 2h 15m
        Entry: $X | Exit: $Y
        Full transparency. Link in bio."
        """
        emoji = "✅" if profit_pct > 0 else "❌"
        profit_str = f"+{profit_pct:.1f}%" if profit_pct > 0 else f"{profit_pct:.1f}%"
        
        text = f"""Trade #{trade_num}: ${token} {profit_str} {emoji}
Grade: {grade} | PnL: ${pnl:.2f}

Entry: {entry_time}
Exit: {exit_time}

Building the dream one trade at a time. 🦞🚀

#Solana #Trading #GoldCoastMasterPlan"""
        
        return self.post_tweet(text)
    
    def post_thread(self, tweets: List[str]) -> List[dict]:
        """
        Post a thread (series of connected tweets)
        
        Args:
            tweets: List of tweet texts
        
        Returns:
            List of tweet results
        """
        results = []
        reply_to = None
        
        for i, tweet in enumerate(tweets):
            # Add numbering if not present
            if not tweet.startswith(f"{i+1}/") and len(tweets) > 1:
                tweet = f"{i+1}/{len(tweets)}\n\n{tweet}"
            
            result = self.post_tweet(tweet, reply_to)
            results.append(result)
            
            # Get tweet ID for next reply
            if "data" in result:
                reply_to = result["data"]["id"]
        
        return results
    
    def post_weekly_recap(self,
                         trades: int,
                         wins: int,
                         total_pnl: float,
                         win_rate: float) -> dict:
        """
        Post weekly trading recap
        
        Template:
        "Weekly Recap:
        Trades: 15 | Wins: 12 (80%) ✅
        Total PnL: +$1,247
        
        Consistency > Big wins
        Next week: Same system, more trades"
        """
        text = f"""📊 Weekly Trading Recap

Trades: {trades}
Wins: {wins} ({win_rate:.0f}%) ✅
Total PnL: ${total_pnl:+.2f}

The system works.
Consistency beats chasing pumps.

Building the Gold Coast dream. 🦞🚀

#Trading #Solana #GoldCoastMasterPlan"""
        
        return self.post_tweet(text)
    
    def post_milestone(self, milestone: str) -> dict:
        """
        Post milestone achievement
        
        Examples:
        - "Trade #50 complete"
        - "Passed $10K profit"
        - "Month 6: $50K reached"
        """
        emojis = ["🎉", "🚀", "💪", "✅", "🦞"]
        emoji = emojis[hash(milestone) % len(emojis)]
        
        text = f"""{emoji} MILESTONE: {milestone}

One step closer to the dream.

Gold Coast Master Plan.
We don't stop. 🦞🚀"""
        
        return self.post_tweet(text)
    
    def get_metrics(self) -> dict:
        """
        Get account metrics
        Requires elevated access
        """
        # This requires user lookup endpoints
        # Implementation depends on access level
        pass

# Pre-written content templates
CONTENT_TEMPLATES = {
    "intro": """🦞 Gold Coast Master Plan

Building the dream:
🏠 Waterfront property
🚗 R35 GTR in garage  
🎮 Kids with epic setups
🏖️ Beach sunset walks

One trade at a time.

Follow along. 🚀""",
    
    "transparency": """🧵 Why I post every trade:

1/ Accountability
Public = I can't hide losses

2/ Proof
Not guru promises, just results

3/ Community
We're building together

4/ Motivation
Wins and losses = learning

Full transparency. Always. 🦞""",
    
    "strategy": """🧵 My trading system:

1/ Scanners run 24/7
Find Grade A+ opportunities only

2/ Strict position sizing
Max 0.02 SOL per trade

3/ Hard exits
+15% profit / -7% stop loss

4/ Document everything
Learn from every trade

No emotion. Just math. 📊""",
    
    "loss": """Trade #X: -7% ❌

Not every trade wins.
System says cut losses.
System followed. ✅

Next trade. Same rules.
#GoldCoastMasterPlan"""
}

# Convenience function
def create_trade_post(trade_num: int, token: str, profit: float, **kwargs):
    """Quick create trade result post"""
    return {
        "type": "trade",
        "content": f"Trade #{trade_num}: ${token} +{profit}% ✅",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("=== Twitter Bot for Gold Coast Master ===")
    print("\nSetup required:")
    print("1. Go to https://developer.twitter.com/")
    print("2. Create developer account")
    print("3. Create app @AgentLuxTheClaw")
    print("4. Get API keys")
    print("\nContent templates ready:")
    for name, content in CONTENT_TEMPLATES.items():
        print(f"\n{name}:")
        print(content[:100] + "...")
    print("\n✅ Twitter bot ready for automation")
