#!/usr/bin/env python3
"""
AOE v2.0 - Alert System
Telegram alerting for high-score opportunities.
"""

import json
import requests
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
import logging

from scanner_base import Token
from scorer import ScoreBreakdown


@dataclass
class Alert:
    """Alert data structure."""
    token: Token
    score: float
    breakdown: ScoreBreakdown
    level: str  # "urgent", "queue", "log"
    timestamp: str
    message: str
    action: str


class AlertManager:
    """
    Alert management system.
    
    Alert Levels:
    - URGENT (>=82): Send Telegram immediately
    - QUEUE (75-81): Add to queue for review
    - SILENT (<75): Log only
    """
    
    # Thresholds
    URGENT_THRESHOLD = 82
    QUEUE_THRESHOLD = 75
    
    def __init__(self, 
                 telegram_token: Optional[str] = None,
                 telegram_chat_id: Optional[str] = None,
                 queue_file: Optional[Path] = None,
                 log_file: Optional[Path] = None):
        """
        Initialize alert manager.
        
        Args:
            telegram_token: Bot token
            telegram_chat_id: Chat ID for alerts
            queue_file: Path to queue file
            log_file: Path to alert log
        """
        self.telegram_token = telegram_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = telegram_chat_id or os.getenv('TELEGRAM_CHAT_ID')
        
        self.queue_file = queue_file or Path("/home/skux/.openclaw/workspace/memory/aoe_queue.json")
        self.log_file = log_file or Path("/home/skux/.openclaw/workspace/memory/aoe_alerts.log")
        
        self.logger = logging.getLogger("aoe.alerts")
        
        # Ensure directories exist
        self.queue_file.parent.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def process_opportunity(self, 
                          token: Token, 
                          score: float, 
                          breakdown: ScoreBreakdown) -> str:
        """
        Process a scored opportunity and route to appropriate channel.
        
        Args:
            token: Scored token
            score: Total score
            breakdown: Score breakdown
            
        Returns:
            Action taken: "alerted", "queued", "logged", "ignored"
        """
        timestamp = datetime.now().isoformat()
        
        # Determine level
        if score >= self.URGENT_THRESHOLD:
            level = "urgent"
            action = self._generate_action(token, breakdown, "urgent")
            alert = Alert(token, score, breakdown, level, timestamp, "", action)
            
            # Send Telegram
            success = self._send_telegram(alert)
            self._log_alert(alert, success)
            
            if success:
                self.logger.info(f"🚨 URGENT Alert sent: {token.symbol} ({score:.0f})")
                return "alerted"
            else:
                self.logger.warning(f"Failed to send alert, queued: {token.symbol}")
                self._add_to_queue(token, score, breakdown)
                return "queued"
        
        elif score >= self.QUEUE_THRESHOLD:
            level = "queue"
            action = self._generate_action(token, breakdown, "queue")
            alert = Alert(token, score, breakdown, level, timestamp, "", action)
            
            self._add_to_queue(token, score, breakdown)
            self._log_alert(alert, True)
            
            self.logger.info(f"📋 Queued: {token.symbol} ({score:.0f})")
            return "queued"
        
        else:
            # Just log
            level = "log"
            action = "Monitor"
            alert = Alert(token, score, breakdown, level, timestamp, "", action)
            self._log_alert(alert, True)
            return "logged"
    
    def process_batch(self, 
                    opportunities: List[tuple],
                    dry_run: bool = False) -> Dict[str, int]:
        """
        Process a batch of opportunities.
        
        Args:
            opportunities: List of (token, score, breakdown) tuples
            dry_run: If True, don't actually send alerts
            
        Returns:
            Stats dict
        """
        stats = {"alerted": 0, "queued": 0, "logged": 0, "ignored": 0}
        
        for token, score, breakdown in opportunities:
            if dry_run:
                self.logger.info(f"[DRY RUN] {token.symbol}: {score:.0f} - Would: {self._determine_action(score)}")
                continue
            
            action = self.process_opportunity(token, score, breakdown)
            stats[action] = stats.get(action, 0) + 1
        
        return stats
    
    def _determine_action(self, score: float) -> str:
        """Determine what action would be taken."""
        if score >= self.URGENT_THRESHOLD:
            return "alert"
        elif score >= self.QUEUE_THRESHOLD:
            return "queue"
        else:
            return "log"
    
    def _send_telegram(self, alert: Alert) -> bool:
        """Send alert via Telegram."""
        if not self.telegram_token or not self.telegram_chat_id:
            self.logger.warning("Telegram not configured")
            return False
        
        # Build message
        message = self._format_telegram_message(alert)
        
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send Telegram: {e}")
            return False
    
    def _format_telegram_message(self, alert: Alert) -> str:
        """Format alert for Telegram."""
        t = alert.token
        b = alert.breakdown
        
        # Score emoji
        if alert.score >= 90:
            score_emoji = "🔥🔥"
        elif alert.score >= 85:
            score_emoji = "🔥"
        else:
            score_emoji = "⚡"
        
        # Price change indicators
        if t.price_change_1h <= -10:
            dip_emoji = "🩸"
        elif t.price_change_1h < 0:
            dip_emoji = "📉"
        else:
            dip_emoji = "📈"
        
        # Narrative tags
        narratives = t.__dict__.get('narratives', [])
        tags = " ".join([f"#{n.upper()}" for n in narratives[:3]])
        
        message = f"""{score_emoji} **AOE OPPORTUNITY ALERT** {score_emoji}

**{t.name}** (${t.symbol})
📊 Score: **{alert.score:.0f}/100** | Level: {alert.level.upper()}

💰 Market Cap: ${t.market_cap:,.0f}
💵 Price: ${t.price:.6f}
{dip_emoji} 1h Change: {t.price_change_1h:+.1f}%

📈 Volume 24h: ${t.volume_24h:,.0f}
🔄 Transactions: {t.txns_24h:,}
💧 Liquidity: ${t.liquidity:,.0f}

{tags}

**Score Breakdown:**
• Potential: {b.potential:.0f}
• Probability: {b.probability:.0f}
• Speed: {b.speed:.0f}
• Fit: {b.fit:.0f}
• Alpha: {b.alpha:.0f}
• Risk: {b.risk:.0f}
• Effort: {b.effort:.0f}

**Why This Opportunity:**
{self._explain_opportunity(t, b)}

**Recommended Action:**
{alert.action}

```
Address: {t.address}
Sources: {', '.join(t.sources)}
Detected: {t.discovered_at.strftime('%H:%M') if t.discovered_at else 'Unknown'}
```

_Note: This is an AI-generated alert for informational purposes only. Not financial advice._
"""
        return message
    
    def _explain_opportunity(self, token: Token, breakdown: ScoreBreakdown) -> str:
        """Generate explanation of why this is an opportunity."""
        explanations = []
        
        # Mean reversion specific
        if token.price_change_1h <= -10 and token.price_change_1h >= -20:
            explanations.append(f"Price dipped {token.price_change_1h:.0f}% in last hour - potential mean reversion setup")
        
        # Volume spike
        vol_spike = token.__dict__.get('vol_spike_5m', 0)
        if vol_spike > 3:
            explanations.append(f"Volume spiked {vol_spike:.0f}x above average in last 5m")
        
        # Narrative
        narratives = token.__dict__.get('narratives', [])
        if narratives:
            explanations.append(f"Strong {', '.join(narratives)} narrative alignment")
        
        # Early detection
        if token.__dict__.get('age_hours', 99) < 6:
            explanations.append(f"Recently launched ({token.__dict__['age_hours']:.0f}h ago) - early entry window")
        
        # High probability signals
        if breakdown.probability > 70:
            explanations.append("High volume/transaction activity suggests strong interest")
        
        return "\n".join(f"• {e}" for e in explanations[:3]) if explanations else "Multi-factor positive alignment"
    
    def _generate_action(self, token: Token, breakdown: ScoreBreakdown, level: str) -> str:
        """Generate recommended action."""
        actions = []
        
        if level == "urgent":
            actions.append(f"⚡ **Act within 10-30 min** - Score {breakdown.total:.0f} is very high")
        elif level == "queue":
            actions.append(f"📋 **Review within 2 hours** - Good opportunity but not urgent")
        
        # Size recommendation based on risk
        if breakdown.risk > 60:
            actions.append("💰 Size: Small position (0.1-0.2 SOL) - Higher risk")
        elif breakdown.risk > 40:
            actions.append("💰 Size: Medium position (0.25-0.5 SOL)")
        else:
            actions.append("💰 Size: Standard position (0.5 SOL) - Lower risk")
        
        # Entry strategy
        if token.price_change_1h < -10:
            actions.append(f"🎯 Entry: Price already dipped {token.price_change_1h:.0f}% - consider small DCA")
        elif token.price_change_1h > 5:
            actions.append("🎯 Entry: Wait for pullback to 5-10% dip")
        else:
            actions.append("🎯 Entry: Current price acceptable")
        
        # Exit strategy
        actions.append("🚪 Exit: Scale 50% at +8%, remainder with trailing stop")
        
        return "\n".join(actions)
    
    def _add_to_queue(self, token: Token, score: float, breakdown: ScoreBreakdown):
        """Add opportunity to review queue."""
        queue = self._load_queue()
        
        # Check if already in queue
        for opp in queue.get('opportunities', []):
            if opp.get('address') == token.address:
                # Update score if higher
                if score > opp.get('score', 0):
                    opp['score'] = score
                    opp['breakdown'] = breakdown.to_dict()
                    opp['timestamp'] = datetime.now().isoformat()
                break
        else:
            # New entry
            queue['opportunities'].append({
                'address': token.address,
                'symbol': token.symbol,
                'name': token.name,
                'score': score,
                'breakdown': breakdown.to_dict(),
                'timestamp': datetime.now().isoformat(),
                'status': 'pending_review'
            })
        
        # Keep only last 50
        queue['opportunities'] = sorted(
            queue['opportunities'], 
            key=lambda x: x['score'], 
            reverse=True
        )[:50]
        
        queue['lastUpdated'] = datetime.now().isoformat()
        
        # Save
        with open(self.queue_file, 'w') as f:
            json.dump(queue, f, indent=2)
    
    def _load_queue(self) -> Dict:
        """Load opportunity queue."""
        if self.queue_file.exists():
            try:
                with open(self.queue_file) as f:
                    return json.load(f)
            except:
                pass
        return {"opportunities": [], "lastUpdated": None}
    
    def _log_alert(self, alert: Alert, delivered: bool):
        """Log alert to file."""
        log_entry = {
            'timestamp': alert.timestamp,
            'symbol': alert.token.symbol,
            'address': alert.token.address,
            'score': alert.score,
            'level': alert.level,
            'delivered': delivered,
            'sources': alert.token.sources
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")


if __name__ == "__main__":
    # Test alerts
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("🧪 Testing Alert System v2.0...")
    print("=" * 60)
    
    from scorer import OpportunityScorer
    
    # Create test token
    test_token = Token(
        address="TEST123456789",
        symbol="AOL",
        name="AI Opportunity Lab",
        chain_id="solana",
        price=0.00045,
        market_cap=450_000,
        liquidity=120_000,
        volume_24h=180_000,
        price_change_1h=-14,
        price_change_24h=35,
        txns_24h=650,
        buys_24h=420,
        sells_24h=230,
        source="dexscreener"
    )
    test_token.__dict__['narratives'] = ['ai', 'meme']
    test_token.__dict__['age_hours'] = 4
    test_token.__dict__['vol_spike_5m'] = 3.5
    
    # Score
    scorer = OpportunityScorer()
    score, breakdown = scorer.score(test_token)
    
    # Test alert (dry run)
    alerts = AlertManager()
    
    print(f"\n📊 Token: {test_token.name} ({test_token.symbol})")
    print(f"   Score: {score:.0f}")
    print(f"   Would be: {alerts._determine_action(score)}")
    
    print("\n📝 Telegram Message Preview:")
    alert = Alert(test_token, score, breakdown, "urgent", datetime.now().isoformat(), "", "")
    msg = alerts._format_telegram_message(alert)
    print(msg[:800] + "...")
