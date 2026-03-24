#!/usr/bin/env python3
"""
LG TV + Embodiment Layer Integration
Connects your LG TV to Lux's physical world interface.
"""

import sys
import time
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path.home() / ".openclaw" / "workspace"))
sys.path.insert(0, str(Path.home() / ".openclaw" / "workspace" / "skills" / "embodiment-layer"))

from embodiment_core import EmbodimentLayer
from lgtv_controller import LGTVController


class EmbodimentWithTV(EmbodimentLayer):
    """Extended Embodiment Layer with LG TV support."""
    
    def __init__(self, tv_ip: str, demo_mode: bool = False):
        super().__init__(demo_mode=demo_mode)
        self.tv_ip = tv_ip
        self.tv = None
        
        if not demo_mode:
            self._connect_tv()
    
    def _connect_tv(self):
        """Connect to LG TV."""
        print(f"📺 Connecting to LG TV at {self.tv_ip}...")
        self.tv = LGTVController(self.tv_ip)
        
        if self.tv.connect():
            print("✅ TV connected!")
            # Add TV to devices
            self.devices["lg_tv"] = {
                "type": "smart_tv",
                "state": "on",
                "ip": self.tv_ip,
                "connected": True
            }
        else:
            print("❌ Could not connect to TV (demo mode active)")
            self.tv = None
    
    def control_device(self, device_id: str, action: str, **params) -> dict:
        """Override to handle TV control."""
        if device_id == "lg_tv" and self.tv:
            # Handle TV-specific actions
            if action == "turn_on":
                self.tv.power_on()
                return {"success": True, "device": "lg_tv", "action": "power_on"}
            elif action == "turn_off":
                self.tv.power_off()
                return {"success": True, "device": "lg_tv", "action": "power_off"}
            elif action == "set_volume":
                self.tv.set_volume(params.get("level", 50))
                return {"success": True, "device": "lg_tv", "action": "set_volume"}
            elif action == "mute":
                self.tv.mute(params.get("mute", True))
                return {"success": True, "device": "lg_tv", "action": "mute"}
            elif action == "launch_app":
                self.tv.launch_app(params.get("app", "netflix"))
                return {"success": True, "device": "lg_tv", "action": "launch_app"}
            elif action == "show_message":
                self.tv.show_message(params.get("message", "Hello from Lux!"))
                return {"success": True, "device": "lg_tv", "action": "show_message"}
        
        # Fall back to parent class
        return super().control_device(device_id, action, **params)
    
    def set_trading_mode(self, mode: str) -> dict:
        """Override to include TV in trading mode."""
        results = super().set_trading_mode(mode)
        
        if self.tv and mode == "focus":
            # Launch trading dashboard on TV
            print("📺 Launching trading view on TV...")
            self.tv.launch_app("browser")  # Or your trading app
            self.tv.show_message("Trading Mode Activated - Lux is monitoring")
            results["tv_action"] = "launched_trading_view"
        
        return results
    
    def alert_trade_executed(self, trade_info: dict) -> None:
        """Override to show trade alerts on TV."""
        super().alert_trade_executed(trade_info)
        
        if self.tv:
            symbol = trade_info.get("symbol", "")
            side = trade_info.get("side", "")
            amount = trade_info.get("amount", 0)
            
            message = f"💰 {side.upper()} {amount} {symbol}"
            self.tv.show_message(message)
            print(f"📺 Alert shown on TV: {message}")


def demo_with_tv(tv_ip: str = None):
    """Demo embodiment layer with TV."""
    print("=" * 60)
    print("🤖 LUX EMBODIMENT LAYER + LG TV")
    print("=" * 60)
    print()
    
    if tv_ip:
        print(f"Connecting to TV at: {tv_ip}")
        print("Note: First connection requires accepting prompt on TV")
        print()
        embodiment = EmbodimentWithTV(tv_ip, demo_mode=False)
    else:
        print("No TV IP provided - running in DEMO mode")
        print("To connect to real TV: python3 embodiment_with_tv.py <TV_IP>")
        print()
        embodiment = EmbodimentWithTV("", demo_mode=True)
    
    # Show all devices including TV
    print("\n📱 Connected Devices:")
    print("-" * 40)
    for device in embodiment.list_devices():
        status = device.get('state', 'unknown')
        if device['id'] == 'lg_tv':
            status = f"📺 {status} ({device.get('ip', 'N/A')})"
        print(f"  • {device['id']}: {status}")
    print()
    
    # Demo trading mode with TV
    print("🎯 Trading Mode Demo:")
    print("-" * 40)
    result = embodiment.set_trading_mode("focus")
    print(f"  ✅ Trading focus mode activated")
    if "tv_action" in result:
        print(f"  📺 TV: {result['tv_action']}")
    print()
    
    # Demo trade alert on TV
    print("💰 Trade Alert Demo:")
    print("-" * 40)
    embodiment.alert_trade_executed({
        "symbol": "SOL",
        "side": "buy",
        "amount": 0.1,
        "price": 150.0
    })
    print(f"  ✅ Alert shown on office lamp (GREEN)")
    if embodiment.tv:
        print(f"  ✅ Alert shown on TV")
    print()
    
    # Interactive control
    if embodiment.tv:
        print("📺 TV Controls:")
        print("-" * 40)
        print("  1. Power Off TV")
        print("  2. Launch Netflix")
        print("  3. Show Message")
        print("  4. Set Volume")
        print("  0. Skip")
        
        choice = input("\nSelect action: ").strip()
        
        if choice == "1":
            embodiment.tv.power_off()
            print("  ✅ TV powered off")
        elif choice == "2":
            embodiment.tv.launch_app("netflix")
            print("  ✅ Netflix launched")
        elif choice == "3":
            msg = input("Message: ").strip()
            embodiment.tv.show_message(msg)
            print(f"  ✅ Message displayed: {msg}")
        elif choice == "4":
            vol = input("Volume (0-100): ").strip()
            embodiment.tv.set_volume(int(vol))
            print(f"  ✅ Volume set to {vol}")
    
    print("\n" + "=" * 60)
    print("✨ Demo Complete!")
    print("=" * 60)
    
    if embodiment.tv:
        embodiment.tv.disconnect()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Embodiment Layer with LG TV")
    parser.add_argument("tv_ip", nargs="?", help="LG TV IP address")
    
    args = parser.parse_args()
    
    try:
        demo_with_tv(args.tv_ip)
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
