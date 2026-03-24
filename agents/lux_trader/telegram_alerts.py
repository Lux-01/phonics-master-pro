#!/usr/bin/env python3
"""
Telegram Alert System for LuxTrader & Holy Trinity
Sends instant notifications when trading signals are detected
"""

import json
import os
from datetime import datetime

# Telegram Bot Configuration
# You'll need to set these up via @BotFather
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '6610224534')  # Your Telegram ID

def send_telegram_alert(message: str, priority: str = "normal"):
    """Send alert to Telegram"""
    try:
        import requests
        
        if not TELEGRAM_BOT_TOKEN:
            print(f"[{datetime.now()}] Telegram not configured: {message}")
            return False
        
        # Priority emojis
        emoji_map = {
            "high": "🚨",
            "normal": "📊",
            "low": "ℹ️"
        }
        emoji = emoji_map.get(priority, "📊")
        
        # Format message
        full_message = f"{emoji} <b>LuxTrader Alert</b>\n\n{message}\n\n<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": full_message,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
        
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")
        return False

def alert_signal_detected(token: dict, system: str = "LuxTrader"):
    """Alert when a trading signal is detected"""
    symbol = token.get('symbol', 'Unknown')
    grade = token.get('grade', 'N/A')
    score = token.get('score', 0)
    mcap = token.get('mcap', 0)
    
    message = f"""
<b>🎯 TRADING SIGNAL DETECTED</b>

<b>System:</b> {system}
<b>Token:</b> {symbol}
<b>Grade:</b> {grade}
<b>Score:</b> {score}
<b>Market Cap:</b> ${mcap:,.0f}

<b>Action:</b> Trade executing...
"""
    
    return send_telegram_alert(message, priority="high")

def alert_trade_completed(trade: dict, system: str = "LuxTrader"):
    """Alert when a trade completes"""
    symbol = trade.get('symbol', 'Unknown')
    pnl = trade.get('result', {}).get('pnl_pct', 0)
    win = trade.get('result', {}).get('win', False)
    
    emoji = "✅" if win else "❌"
    result = "WIN" if win else "LOSS"
    
    message = f"""
<b>{emoji} TRADE {result}</b>

<b>System:</b> {system}
<b>Token:</b> {symbol}
<b>P&L:</b> {pnl:+.2f}%

<b>Status:</b> Trade closed
"""
    
    return send_telegram_alert(message, priority="high" if win else "normal")

def alert_daily_summary(lux_stats: dict, ht_stats: dict):
    """Send daily trading summary"""
    message = f"""
<b>📈 DAILY TRADING SUMMARY</b>

<b>🔥 LuxTrader v3.0</b>
• Trades: {lux_stats.get('trades', 0)}
• P&L: {lux_stats.get('pnl', 0):+.4f} SOL
• Win Rate: {lux_stats.get('win_rate', 0):.0f}%

<b>⛪ Holy Trinity</b>
• Trades: {ht_stats.get('trades', 0)}
• P&L: {ht_stats.get('pnl', 0):+.4f} SOL
• Win Rate: {ht_stats.get('win_rate', 0):.0f}%

<b>Combined Capital:</b> {lux_stats.get('capital', 0) + ht_stats.get('capital', 0):.4f} SOL
"""
    
    return send_telegram_alert(message, priority="normal")

def alert_error(error_msg: str, system: str = "LuxTrader"):
    """Alert on system errors"""
    message = f"""
<b>⚠️ SYSTEM ERROR</b>

<b>System:</b> {system}
<b>Error:</b> {error_msg}

Please check logs immediately.
"""
    return send_telegram_alert(message, priority="high")

if __name__ == "__main__":
    # Test alerts
    print("Testing Telegram alerts...")
    
    # Test signal alert
    test_token = {
        "symbol": "TEST",
        "grade": "A+",
        "score": 95,
        "mcap": 50000
    }
    
    send_telegram_alert("🧪 Test alert from LuxTrader system", priority="normal")
    print("Test complete. Check Telegram.")
