#!/usr/bin/env python3
"""
🎯 LUX AUTO-SELL MONITOR v2.0
Enhanced position monitoring with smart retry logic and emergency exits
Integrates with LuxTrader v3.0 and Holy Trinity

Features:
- Multi-strategy sell execution
- Dynamic retry with backoff
- Emergency exit protocols
- Real-time monitoring dashboard
- Telegram/Discord notifications
- Manual override capability
"""

import asyncio
import json
import time
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

# Import enhanced seller
from lux_enhanced_seller import LuxEnhancedSeller, SellResult
from tokenomics_detector import TokenomicsDetector, TokenSecurity

# Configuration
CONFIG = {
    'version': '2.0',
    'check_interval_seconds': 30,
    'emergency_check_interval': 5,
    
    # Exit triggers
    'take_profit_pct': 15,
    'stop_loss_pct': -7,
    'time_stop_hours': 4,
    'trailing_stop_pct': 5,
    
    # Retry settings
    'max_sell_attempts': 5,
    'retry_delay_seconds': 10,
    'backoff_multiplier': 2,
    
    # Files
    'positions_file': '/home/skux/.openclaw/workspace/agents/lux_trader/monitored_positions.json',
    'sell_history_file': '/home/skux/.openclaw/workspace/agents/lux_trader/sell_history.json',
    'state_file': '/home/skux/.openclaw/workspace/agents/lux_trader/monitor_state.json',
    
    # Notifications
    'telegram_bot_token': None,  # Set if using Telegram
    'telegram_chat_id': None,
    'discord_webhook': None,  # Set if using Discord
}


class PositionStatus(Enum):
    """Position monitoring status"""
    ACTIVE = "active"
    MONITORING = "monitoring"
    EXIT_SIGNAL = "exit_signal"
    SELLING = "selling"
    SOLD = "sold"
    FAILED = "failed"
    EMERGENCY = "emergency"


@dataclass
class MonitoredPosition:
    """Position being monitored"""
    token_address: str
    token_symbol: str
    entry_price: float
    entry_sol: float
    entry_time: str
    current_price: float
    current_value: float
    pnl_pct: float
    status: PositionStatus
    exit_reason: Optional[str]
    sell_attempts: int
    last_check: str
    alerts_triggered: List[str]
    tokenomics: Optional[Dict]


class LuxAutoSellMonitor:
    """
    Enhanced auto-sell monitor with retry logic
    """
    
    def __init__(self, wallet_address: str, private_key: Optional[str] = None):
        self.wallet = wallet_address
        self.seller = LuxEnhancedSeller(wallet_address, private_key)
        self.detector = TokenomicsDetector()
        self.positions: Dict[str, MonitoredPosition] = {}
        self.sell_history: List[Dict] = []
        self.running = False
        self.emergency_mode = False
        
        # Statistics
        self.stats = {
            'positions_monitored': 0,
            'positions_sold': 0,
            'positions_failed': 0,
            'emergency_exits': 0,
            'total_pnl_sol': 0.0,
            'avg_sell_time_seconds': 0,
        }
        
        # Load existing state
        self._load_state()
    
    def _load_state(self):
        """Load previous monitor state"""
        try:
            if os.path.exists(CONFIG['state_file']):
                with open(CONFIG['state_file'], 'r') as f:
                    state = json.load(f)
                    self.stats = state.get('stats', self.stats)
                    print(f"📂 Loaded previous state")
        except Exception as e:
            print(f"⚠️ Could not load state: {e}")
    
    def _save_state(self):
        """Save current state"""
        try:
            state = {
                'stats': self.stats,
                'last_save': datetime.now().isoformat(),
            }
            with open(CONFIG['state_file'], 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save state: {e}")
    
    async def add_position(self, token_address: str, token_symbol: str,
                           entry_price: float, entry_sol: float) -> MonitoredPosition:
        """Add a new position to monitor"""
        print(f"\n➕ Adding position: {token_symbol}")
        
        # Analyze tokenomics first
        tokenomics = await self.detector.analyze_token(token_address)
        
        position = MonitoredPosition(
            token_address=token_address,
            token_symbol=token_symbol,
            entry_price=entry_price,
            entry_sol=entry_sol,
            entry_time=datetime.now().isoformat(),
            current_price=entry_price,
            current_value=entry_sol,
            pnl_pct=0.0,
            status=PositionStatus.ACTIVE,
            exit_reason=None,
            sell_attempts=0,
            last_check=datetime.now().isoformat(),
            alerts_triggered=[],
            tokenomics=asdict(tokenomics) if tokenomics else None
        )
        
        self.positions[token_address] = position
        self.stats['positions_monitored'] += 1
        
        print(f"   Entry: {entry_sol:.4f} SOL @ {entry_price:.8f}")
        print(f"   Status: {position.status.value}")
        
        if tokenomics:
            print(f"   Risk: {tokenomics.risk_level.value} ({tokenomics.risk_score}/100)")
        
        self._save_positions()
        return position
    
    async def monitor_loop(self):
        """Main monitoring loop"""
        print(f"\n{'='*70}")
        print(f"🎯 LUX AUTO-SELL MONITOR v{CONFIG['version']}")
        print(f"{'='*70}")
        print(f"Wallet: {self.wallet[:20]}...")
        print(f"Positions: {len(self.positions)}")
        print(f"Check interval: {CONFIG['check_interval_seconds']}s")
        print(f"Emergency interval: {CONFIG['emergency_check_interval']}s")
        print(f"{'='*70}\n")
        
        self.running = True
        check_count = 0
        
        while self.running:
            check_count += 1
            start_time = time.time()
            
            print(f"\n📡 Check #{check_count} - {datetime.now().strftime('%H:%M:%S')}")
            print('-'*70)
            
            # Check each position
            for address, position in list(self.positions.items()):
                if position.status in [PositionStatus.SOLD, PositionStatus.FAILED]:
                    continue
                
                await self._check_position(position)
            
            # Calculate sleep time
            elapsed = time.time() - start_time
            sleep_time = (
                CONFIG['emergency_check_interval'] if self.emergency_mode 
                else CONFIG['check_interval_seconds']
            )
            sleep_time = max(1, sleep_time - elapsed)
            
            remaining = len([p for p in self.positions.values() 
                          if p.status not in [PositionStatus.SOLD, PositionStatus.FAILED]])
            
            if remaining > 0:
                print(f"\n⏳ {remaining} positions active, next check in {sleep_time:.0f}s")
                await asyncio.sleep(sleep_time)
            else:
                print(f"\n✅ All positions closed!")
                break
        
        self._print_final_report()
    
    async def _check_position(self, position: MonitoredPosition):
        """Check a single position for exit signals"""
        try:
            # Update current price
            current_price = await self._get_current_price(position.token_address)
            if not current_price:
                print(f"   ⚠️ {position.token_symbol}: Price unavailable")
                return
            
            position.current_price = current_price
            position.current_value = position.entry_sol * (current_price / position.entry_price)
            position.pnl_pct = ((position.current_value - position.entry_sol) / position.entry_sol) * 100
            position.last_check = datetime.now().isoformat()
            
            # Calculate time held
            entry_time = datetime.fromisoformat(position.entry_time)
            time_held_hours = (datetime.now() - entry_time).total_seconds() / 3600
            
            # Check exit signals
            exit_signal = None
            exit_reason = None
            
            # Take profit
            if position.pnl_pct >= CONFIG['take_profit_pct']:
                exit_signal = 'TAKE_PROFIT'
                exit_reason = f"Take profit triggered: +{position.pnl_pct:.1f}%"
            
            # Stop loss
            elif position.pnl_pct <= CONFIG['stop_loss_pct']:
                exit_signal = 'STOP_LOSS'
                exit_reason = f"Stop loss triggered: {position.pnl_pct:.1f}%"
                self.emergency_mode = True
            
            # Time stop
            elif time_held_hours >= CONFIG['time_stop_hours']:
                exit_signal = 'TIME_STOP'
                exit_reason = f"Time stop: {time_held_hours:.1f}h held"
            
            # Print status
            emoji = "🟢" if position.pnl_pct > 0 else "🔴" if position.pnl_pct < 0 else "⚪"
            print(f"   {emoji} {position.token_symbol}: {position.pnl_pct:+.1f}% | "
                  f"{time_held_hours:.1f}h | Value: {position.current_value:.4f} SOL")
            
            # Execute sell if signal triggered
            if exit_signal:
                print(f"\n   💥 EXIT SIGNAL: {exit_reason}")
                position.status = PositionStatus.EXIT_SIGNAL
                position.exit_reason = exit_reason
                await self._execute_sell_with_retry(position)
            
        except Exception as e:
            print(f"   ❌ Error checking {position.token_symbol}: {e}")
    
    async def _get_current_price(self, token_address: str) -> Optional[float]:
        """Get current token price"""
        try:
            # Use Birdeye API
            import requests
            headers = {"X-API-KEY": "6335463fca7340f9a2c73eacd5a37f64"}
            url = f"https://public-api.birdeye.so/defi/price?address={token_address}"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', {}).get('value', 0)
            return None
        except:
            return None
    
    async def _execute_sell_with_retry(self, position: MonitoredPosition):
        """Execute sell with intelligent retry logic"""
        print(f"\n   🚀 Executing sell with retry logic...")
        
        position.status = PositionStatus.SELLING
        
        for attempt in range(1, CONFIG['max_sell_attempts'] + 1):
            print(f"\n   Attempt {attempt}/{CONFIG['max_sell_attempts']}")
            
            # Build position data for seller
            position_data = {
                'price_change_24h': position.pnl_pct,
                'age_hours': (datetime.now() - datetime.fromisoformat(position.entry_time)).total_seconds() / 3600,
            }
            
            # Execute sell
            result = await self.seller.execute_smart_sell(
                position.token_address,
                position.token_symbol,
                position_data,
                position.exit_reason or "monitor_exit"
            )
            
            position.sell_attempts += 1
            
            if result.success:
                # Success!
                position.status = PositionStatus.SOLD
                self.stats['positions_sold'] += 1
                self.stats['total_pnl_sol'] += (result.amount_received - position.entry_sol)
                
                print(f"\n   ✅ SELL SUCCESSFUL!")
                print(f"      Received: {result.amount_received:.6f} SOL")
                print(f"      PnL: {result.amount_received - position.entry_sol:+.6f} SOL")
                print(f"      Attempts: {result.total_attempts}")
                
                # Record in history
                self._record_sell(position, result)
                
                # Send notification
                await self._send_notification(f"✅ SOLD {position.token_symbol}", 
                                            f"PnL: {position.pnl_pct:+.1f}%")
                
                return
            
            else:
                # Failed - calculate retry delay
                delay = CONFIG['retry_delay_seconds'] * (CONFIG['backoff_multiplier'] ** (attempt - 1))
                delay = min(delay, 300)  # Max 5 minutes
                
                print(f"   ❌ Failed: {result.error_message}")
                print(f"   ⏳ Retrying in {delay}s...")
                
                await asyncio.sleep(delay)
        
        # All attempts failed
        print(f"\n   🚨 ALL SELL ATTEMPTS FAILED!")
        position.status = PositionStatus.FAILED
        self.stats['positions_failed'] += 1
        
        # Try emergency exit
        await self._emergency_exit(position)
    
    async def _emergency_exit(self, position: MonitoredPosition):
        """Emergency exit when normal sells fail"""
        print(f"\n   🚨 EMERGENCY EXIT PROTOCOL")
        
        # Try selling at any price
        try:
            # Use maximum slippage
            result = await self.seller.execute_smart_sell(
                position.token_address,
                position.token_symbol,
                {'price_change_24h': -50, 'age_hours': 24},  # Force emergency params
                "EMERGENCY_EXIT"
            )
            
            if result.success:
                position.status = PositionStatus.EMERGENCY
                self.stats['emergency_exits'] += 1
                print(f"   ✅ Emergency exit successful!")
            else:
                print(f"   ❌ Emergency exit also failed")
                
        except Exception as e:
            print(f"   ❌ Emergency exit error: {e}")
    
    def _record_sell(self, position: MonitoredPosition, result: SellResult):
        """Record sell in history"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'token_symbol': position.token_symbol,
            'token_address': position.token_address,
            'entry_sol': position.entry_sol,
            'exit_sol': result.amount_received,
            'pnl_sol': result.amount_received - position.entry_sol,
            'pnl_pct': position.pnl_pct,
            'exit_reason': position.exit_reason,
            'attempts': result.total_attempts,
            'execution_time_ms': result.execution_time_ms,
            'tokenomics': position.tokenomics,
        }
        
        self.sell_history.append(record)
        
        # Save to file
        try:
            with open(CONFIG['sell_history_file'], 'w') as f:
                json.dump(self.sell_history, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save history: {e}")
    
    async def _send_notification(self, title: str, message: str):
        """Send notification (Telegram/Discord)"""
        # Telegram
        if CONFIG.get('telegram_bot_token') and CONFIG.get('telegram_chat_id'):
            try:
                import requests
                url = f"https://api.telegram.org/bot{CONFIG['telegram_bot_token']}/sendMessage"
                requests.post(url, json={
                    'chat_id': CONFIG['telegram_chat_id'],
                    'text': f"{title}\n\n{message}"
                })
            except Exception as e:
                print(f"⚠️ Telegram notification failed: {e}")
        
        # Discord
        if CONFIG.get('discord_webhook'):
            try:
                import requests
                requests.post(CONFIG['discord_webhook'], json={
                    'content': f"**{title}**\n{message}"
                })
            except Exception as e:
                print(f"⚠️ Discord notification failed: {e}")
    
    def _save_positions(self):
        """Save current positions"""
        try:
            positions_dict = {
                addr: asdict(pos) for addr, pos in self.positions.items()
            }
            with open(CONFIG['positions_file'], 'w') as f:
                json.dump(positions_dict, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save positions: {e}")
    
    def _print_final_report(self):
        """Print final monitoring report"""
        print(f"\n{'='*70}")
        print(f"📊 FINAL MONITOR REPORT")
        print(f"{'='*70}")
        
        print(f"\n📈 Statistics:")
        print(f"   Positions Monitored: {self.stats['positions_monitored']}")
        print(f"   Successfully Sold: {self.stats['positions_sold']}")
        print(f"   Failed Sells: {self.stats['positions_failed']}")
        print(f"   Emergency Exits: {self.stats['emergency_exits']}")
        print(f"   Total PnL: {self.stats['total_pnl_sol']:+.6f} SOL")
        
        if self.sell_history:
            print(f"\n💰 Sell History:")
            for record in self.sell_history:
                emoji = "🟢" if record['pnl_pct'] > 0 else "🔴"
                print(f"   {emoji} {record['token_symbol']}: "
                      f"{record['pnl_pct']:+.1f}% ({record['exit_reason']})")
        
        print(f"{'='*70}\n")
        
        self._save_state()
    
    def stop(self):
        """Stop monitoring"""
        print("\n🛑 Stopping monitor...")
        self.running = False
    
    def get_position(self, token_address: str) -> Optional[MonitoredPosition]:
        """Get specific position"""
        return self.positions.get(token_address)
    
    def get_all_positions(self) -> List[MonitoredPosition]:
        """Get all positions"""
        return list(self.positions.values())
    
    def manual_sell(self, token_address: str) -> bool:
        """Trigger manual sell"""
        position = self.positions.get(token_address)
        if not position:
            print(f"❌ Position not found: {token_address[:20]}...")
            return False
        
        print(f"\n👤 MANUAL SELL TRIGGERED for {position.token_symbol}")
        position.exit_reason = "MANUAL_OVERRIDE"
        position.status = PositionStatus.EXIT_SIGNAL
        
        # Schedule sell
        asyncio.create_task(self._execute_sell_with_retry(position))
        return True


# Convenience functions
async def start_monitoring(wallet_address: str, private_key: Optional[str] = None):
    """Start the auto-sell monitor"""
    monitor = LuxAutoSellMonitor(wallet_address, private_key)
    await monitor.monitor_loop()
    return monitor


if __name__ == "__main__":
    print("🎯 Lux Auto-Sell Monitor v2.0")
    print("\nUsage:")
    print("   from lux_auto_sell_monitor import LuxAutoSellMonitor, start_monitoring")
    print("   monitor = LuxAutoSellMonitor(wallet_address, private_key)")
    print("   await monitor.add_position(token, symbol, entry_price, entry_sol)")
    print("   await monitor.monitor_loop()")
