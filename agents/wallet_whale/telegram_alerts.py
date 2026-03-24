#!/usr/bin/env python3
"""
Telegram Alert Module for Whale Tracker
Sends notifications for whale activity and trade execution
"""

import os
import json
import requests
from datetime import datetime
from typing import Optional, Dict

class TelegramAlerter:
    """Send Telegram alerts for whale tracker events"""
    
    def __init__(self, config: Dict):
        self.enabled = config.get("enabled", False)
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", config.get("bot_token", ""))
        self.chat_id = config.get("chat_id", "")
        self.alert_types = config.get("alerts", {})
        
        if self.enabled and not self.bot_token.startswith("$"):
            print(f"📱 Telegram alerts: ENABLED (chat: {self.chat_id})")
        else:
            print("📱 Telegram alerts: DISABLED (set TELEGRAM_BOT_TOKEN env var)")
    
    def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """Send a Telegram message"""
        if not self.enabled or not self.bot_token or self.bot_token.startswith("$"):
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode,
                "disable_web_page_preview": False
            }
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"⚠️ Telegram send failed: {e}")
            return False
    
    def alert_whale_detected(self, wallet_name: str, token_symbol: str, 
                            token_address: str, buy_count: int, 
                            total_sol: float, confidence: str = "HIGH"):
        """Alert when whale activity detected"""
        if not self.alert_types.get("whale_detected", True):
            return
        
        emoji = "🐳" if confidence == "HIGH" else "🐋"
        message = f"""{emoji} <b>WHALE ALERT</b> {emoji}

<b>Wallet:</b> {wallet_name}
<b>Token:</b> {token_symbol}
<b>Buys:</b> {buy_count} in 30s
<b>Total:</b> {total_sol:.2f} SOL
<b>Confidence:</b> {confidence}

<code>{token_address}</code>

<a href='https://dexscreener.com/solana/{token_address}'>View on DexScreener</a>
<a href='https://jup.ag/swap/{token_address}-SOL'>Quick Buy</a>"""
        
        self.send_message(message)
    
    def alert_multi_whale(self, token_symbol: str, token_address: str,
                         whale_count: int, total_buys: int):
        """Alert when multiple whales buying same token"""
        if not self.alert_types.get("whale_detected", True):
            return
        
        message = f"""🔥 <b>MULTI-WHALE ALERT</b> 🔥

<b>Token:</b> {token_symbol}
<b>Whales:</b> {whale_count} wallets
<b>Total Buys:</b> {total_buys}
<b>Signal:</b> VERY HIGH

<code>{token_address}</code>

<a href='https://dexscreener.com/solana/{token_address}'>View on DexScreener</a>
<a href='https://jup.ag/swap/{token_address}-SOL'>Quick Buy</a>"""
        
        self.send_message(message)
    
    def alert_trade_executed(self, token_symbol: str, token_address: str,
                            entry_size: float, tx_signature: str):
        """Alert when Skylar executes a trade"""
        if not self.alert_types.get("trade_executed", True):
            return
        
        message = f"""✅ <b>TRADE EXECUTED</b>

<b>Token:</b> {token_symbol}
<b>Size:</b> {entry_size} SOL
<b>Strategy:</b> +15% TP / -7% SL

<a href='https://solscan.io/tx/{tx_signature}'>View Transaction</a>
<a href='https://dexscreener.com/solana/{token_address}'>Monitor Price</a>"""
        
        self.send_message(message)
    
    def alert_trade_failed(self, token_symbol: str, reason: str):
        """Alert when trade execution fails"""
        if not self.alert_types.get("trade_failed", True):
            return
        
        message = f"""❌ <b>TRADE FAILED</b>

<b>Token:</b> {token_symbol}
<b>Reason:</b> {reason}

Check logs for details."""
        
        self.send_message(message)
    
    def alert_cooldown_active(self, minutes_remaining: int):
        """Alert about cooldown status"""
        message = f"""⏳ <b>COOLDOWN ACTIVE</b>

Waiting {minutes_remaining} minutes before next trade.
Patience = profit."""
        
        self.send_message(message)
    
    def send_daily_summary(self, trades_count: int, pnl_sol: float, 
                          active_positions: int):
        """Send daily trading summary"""
        if not self.alert_types.get("daily_summary", True):
            return
        
        emoji = "📈" if pnl_sol >= 0 else "📉"
        message = f"""{emoji} <b>DAILY WHALE SUMMARY</b> {emoji}

<b>Trades:</b> {trades_count}
<b>P&L:</b> {pnl_sol:+.3f} SOL
<b>Active:</b> {active_positions} positions

Keep hunting! 🐳"""
        
        self.send_message(message)


# Test function
if __name__ == "__main__":
    # Test with sample config
    test_config = {
        "enabled": True,
        "bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
        "chat_id": "6610224534",
        "alerts": {
            "whale_detected": True,
            "trade_executed": True,
            "trade_failed": True,
            "daily_summary": True
        }
    }
    
    alerter = TelegramAlerter(test_config)
    
    # Test messages
    print("Testing Telegram alerts...")
    alerter.alert_whale_detected(
        "Whale Alpha 1", "TEST", "TEST123", 5, 2.5, "HIGH"
    )
