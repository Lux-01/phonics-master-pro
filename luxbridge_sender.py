#!/usr/bin/env python3
"""
Lux Bridge - Desktop Mate Integration
Sends crypto alerts from OpenClaw to Desktop Mate avatar
"""

import json
import os
import hashlib
from datetime import datetime
from pathlib import Path

# Bridge file location (Windows path from WSL2)
BRIDGE_PATHS = [
    "/mnt/c/Users/HighE/DesktopMateLux/alerts.json",  # Windows user path
    "/mnt/c/Temp/LuxBridge/alerts.json",  # Fallback
    "/tmp/luxbridge/alerts.json",  # WSL fallback
]

class LuxBridge:
    def __init__(self):
        self.bridge_path = None
        self._find_bridge_path()
    
    def _find_bridge_path(self):
        """Find writable bridge path"""
        for path in BRIDGE_PATHS:
            try:
                dir_path = Path(path).parent
                dir_path.mkdir(parents=True, exist_ok=True)
                test_file = Path(path)
                test_file.touch()
                self.bridge_path = path
                print(f"✅ Bridge path: {path}")
                return True
            except Exception as e:
                print(f"❌ Failed: {path} - {e}")
        return False
    
    def send_alert(self, alert_type: str, message: str, display_text: str = None, data: dict = None):
        """Send alert to Desktop Mate"""
        if not self.bridge_path:
            print("❌ No bridge path available")
            return False
        
        alert = {
            "type": alert_type,
            "message": message,
            "display_text": display_text or message[:50],
            "timestamp": datetime.now().isoformat(),
            "data": data or {}
        }
        
        try:
            with open(self.bridge_path, 'w') as f:
                json.dump(alert, f, indent=2)
            print(f"✅ Sent: {alert_type} alert")
            return True
        except Exception as e:
            print(f"❌ Failed to send: {e}")
            return False
    
    def grade_a_alert(self, token_data: dict):
        """Send Grade A token alert"""
        ca = token_data.get('ca', 'unknown')[:20] + "..."
        grade = token_data.get('grade', '?')
        mcap = token_data.get('mcap', 0)
        
        message = f"Grade {grade} token found! MCAP: ${mcap:,.0f}"
        display = f"🚀 Grade {grade}!"
        
        return self.send_alert(
            alert_type="grade_a",
            message=message,
            display_text=display,
            data={
                "ca": ca,
                "mcap": mcap,
                "grade": grade,
                "liquidity": token_data.get('liq', 0),
                "holders": token_data.get('holders', 0)
            }
        )
    
    def checkpoint_alert(self, token_data: dict, checkpoint_hours: int):
        """Send checkpoint alert (6h, 12h, 24h, etc.)"""
        ca = token_data.get('ca', 'unknown')[:20] + "..."
        name = token_data.get('name', '?')
        
        message = f"{name} survived {checkpoint_hours}h checkpoint!"
        display = f"🎯 {checkpoint_hours}h Survivor!"
        
        return self.send_alert(
            alert_type="checkpoint",
            message=message,
            display_text=display,
            data={
                "checkpoint": checkpoint_hours,
                "ca": ca,
                "age_hours": token_data.get('age_hours', 0)
            }
        )
    
    def survivor_alert(self, token_data: dict):
        """Send 24h+ survivor alert"""
        ca = token_data.get('ca', 'unknown')[:20] + "..."
        name = token_data.get('name', '?')
        mcap_change = token_data.get('mcap_change_pct', 0)
        
        emoji = "🚀" if mcap_change > 0 else "📉"
        message = f"{emoji} {name} is a Grade A Survivor! MCAP change: {mcap_change:+.1f}%"
        display = f"🏆 Survivor! {mcap_change:+.0f}%"
        
        return self.send_alert(
            alert_type="survivor",
            message=message,
            display_text=display,
            data={
                "ca": ca,
                "mcap_change_pct": mcap_change,
                "checkpoints": token_data.get('checkpoints', {})
            }
        )
    
    def heartbeat_alert(self):
        """Send periodic heartbeat"""
        return self.send_alert(
            alert_type="heartbeat",
            message="Lux online and monitoring",
            display_text="🦞 Online"
        )
    
    def test_bridge(self):
        """Test the bridge connection"""
        print("\n🧪 Testing Lux Bridge...")
        return self.send_alert(
            alert_type="grade_a",
            message="Bridge test successful! DeskMate integration working.",
            display_text="🎮 Bridge OK!"
        )

# Integration with v5.4 scanner
def integrate_with_v54():
    """Add bridge calls to v5.4 scanner"""
    bridge = LuxBridge()
    
    # This would be called from v5.4 when:
    # - New Grade A found
    # - Checkpoint hit
    # - Survivor identified
    
    return bridge

if __name__ == "__main__":
    print("🦞 Lux Bridge - Desktop Mate Integration")
    print("=" * 50)
    
    bridge = LuxBridge()
    
    if bridge.bridge_path:
        print(f"\n✅ Bridge ready!")
        print(f"📁 Alerts will be written to:")
        print(f"   {bridge.bridge_path}")
        print(f"\n🧪 Running test alert...")
        bridge.test_bridge()
        print(f"\n💡 To use in v5.4:")
        print(f"   from luxbridge_sender import LuxBridge")
        print(f"   bridge = LuxBridge()")
        print(f"   bridge.grade_a_alert(token_data)")
    else:
        print("\n❌ Bridge path not found!")
        print("   Create one of these directories:")
        for p in BRIDGE_PATHS:
            print(f"   - {p}")
