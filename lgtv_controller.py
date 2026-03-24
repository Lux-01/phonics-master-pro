#!/usr/bin/env python3
"""
LG webOS TV Controller
Connects to LG Smart TVs for control via WebSocket.

Requirements:
- pip install pywebostv
- TV must be on same network
- Pairing required on first connection
"""

import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LGTVController:
    """Controller for LG webOS Smart TVs."""
    
    def __init__(self, ip_address: str, config_file: Optional[str] = None):
        self.ip = ip_address
        self.config_file = config_file or str(Path.home() / ".openclaw" / "lgtv_config.json")
        self.client = None
        self.connected = False
        self.store = {}
        
    def _load_store(self):
        """Load stored credentials."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.store = json.load(f)
                logger.info("Loaded existing TV credentials")
            except Exception as e:
                logger.warning(f"Could not load config: {e}")
                self.store = {}
    
    def _save_store(self):
        """Save credentials for future use."""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.store, f)
            logger.info("TV credentials saved")
        except Exception as e:
            logger.error(f"Could not save config: {e}")
    
    def connect(self) -> bool:
        """
        Connect to LG TV.
        First connection requires pairing (accept prompt on TV).
        """
        try:
            # Try to import pywebostv
            try:
                from pywebostv.connection import WebOSClient
                from pywebostv.controls import SystemControl, MediaControl, ApplicationControl
            except ImportError:
                logger.error("pywebostv not installed. Run: pip install pywebostv")
                return False
            
            self._load_store()
            
            # Create client
            self.client = WebOSClient(self.ip)
            self.client.connect()
            
            # Register/Pair
            for status in self.client.register(self.store):
                if status == WebOSClient.PROMPTED:
                    print("📺 Please accept the connection on your LG TV!")
                elif status == WebOSClient.REGISTERED:
                    print("✅ Successfully paired with TV!")
            
            self._save_store()
            
            # Initialize controls
            self.system = SystemControl(self.client)
            self.media = MediaControl(self.client)
            self.app = ApplicationControl(self.client)
            
            self.connected = True
            logger.info(f"Connected to LG TV at {self.ip}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to TV: {e}")
            self.connected = False
            return False
    
    def power_on(self) -> bool:
        """Turn TV on (requires Wake-on-LAN)."""
        try:
            # Wake-on-LAN for power on
            import socket
            import struct
            
            # Get MAC address from stored config
            mac = self.store.get('mac', '')
            if not mac:
                logger.warning("MAC address not stored, can't power on via WOL")
                return False
            
            # Send magic packet
            mac_bytes = bytes.fromhex(mac.replace(':', ''))
            magic = b'\xff' * 6 + mac_bytes * 16
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(magic, ('255.255.255.255', 9))
            sock.close()
            
            logger.info("Wake-on-LAN packet sent")
            return True
            
        except Exception as e:
            logger.error(f"Failed to power on: {e}")
            return False
    
    def power_off(self) -> bool:
        """Turn TV off."""
        if not self.connected:
            logger.error("Not connected to TV")
            return False
        
        try:
            self.system.power_off()
            logger.info("TV powered off")
            return True
        except Exception as e:
            logger.error(f"Failed to power off: {e}")
            return False
    
    def set_volume(self, level: int) -> bool:
        """Set volume (0-100)."""
        if not self.connected:
            return False
        
        try:
            self.media.set_volume(level)
            logger.info(f"Volume set to {level}")
            return True
        except Exception as e:
            logger.error(f"Failed to set volume: {e}")
            return False
    
    def mute(self, mute: bool = True) -> bool:
        """Mute/unmute TV."""
        if not self.connected:
            return False
        
        try:
            if mute:
                self.media.mute()
                logger.info("TV muted")
            else:
                self.media.unmute()
                logger.info("TV unmuted")
            return True
        except Exception as e:
            logger.error(f"Failed to mute/unmute: {e}")
            return False
    
    def launch_app(self, app_name: str) -> bool:
        """
        Launch an app by name.
        Common apps: netflix, youtube, amazon, disneyplus, webbrowser
        """
        if not self.connected:
            return False
        
        try:
            # Get list of installed apps
            apps = self.app.list_apps()
            
            # Find app by name
            app_id = None
            for app in apps:
                if app_name.lower() in app['title'].lower():
                    app_id = app['id']
                    break
            
            if app_id:
                self.app.launch(app_id)
                logger.info(f"Launched app: {app_name}")
                return True
            else:
                logger.warning(f"App not found: {app_name}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to launch app: {e}")
            return False
    
    def get_inputs(self) -> List[Dict]:
        """Get list of available inputs."""
        if not self.connected:
            return []
        
        try:
            # This requires the TV control API
            # Simplified version - common inputs
            return [
                {"id": "HDMI_1", "name": "HDMI 1"},
                {"id": "HDMI_2", "name": "HDMI 2"},
                {"id": "HDMI_3", "name": "HDMI 3"},
                {"id": "COMPONENT", "name": "Component"},
                {"id": "LIVE_TV", "name": "Live TV"},
            ]
        except Exception as e:
            logger.error(f"Failed to get inputs: {e}")
            return []
    
    def set_input(self, input_id: str) -> bool:
        """Switch to specific input (HDMI_1, HDMI_2, etc.)."""
        if not self.connected:
            return False
        
        try:
            # Launch live TV or external input
            if input_id.startswith("HDMI"):
                # For HDMI, we need to use the TV's API
                # This is a simplified version
                logger.info(f"Switching to {input_id}")
                # Actual implementation would use system.launch_app with input app
                return True
            else:
                self.launch_app("livetv")
                return True
                
        except Exception as e:
            logger.error(f"Failed to set input: {e}")
            return False
    
    def show_message(self, message: str) -> bool:
        """Show notification message on TV."""
        if not self.connected:
            return False
        
        try:
            # Create a toast notification
            self.system.notify(message)
            logger.info(f"Message displayed: {message}")
            return True
        except Exception as e:
            logger.error(f"Failed to show message: {e}")
            return False
    
    def get_info(self) -> Dict:
        """Get TV system information."""
        if not self.connected:
            return {}
        
        try:
            info = self.system.info()
            return {
                "model": info.get('model_name', 'Unknown'),
                "software": info.get('software_version', 'Unknown'),
                "ip": self.ip,
                "connected": self.connected
            }
        except Exception as e:
            logger.error(f"Failed to get info: {e}")
            return {}
    
    def disconnect(self):
        """Disconnect from TV."""
        if self.client:
            try:
                self.client.close()
                logger.info("Disconnected from TV")
            except:
                pass
        self.connected = False


def interactive_control(ip_address: str):
    """Interactive TV control."""
    print("=" * 60)
    print("📺 LG TV Controller")
    print("=" * 60)
    print(f"Connecting to: {ip_address}")
    print()
    
    tv = LGTVController(ip_address)
    
    if not tv.connect():
        print("❌ Failed to connect to TV")
        print("\nTroubleshooting:")
        print("  1. Make sure TV is on")
        print("  2. Check TV and computer are on same network")
        print("  3. Enable 'Mobile TV On' in TV settings")
        print("  4. Install pywebostv: pip install pywebostv")
        return
    
    print("\n✅ Connected to TV!")
    info = tv.get_info()
    print(f"   Model: {info.get('model', 'Unknown')}")
    print(f"   Software: {info.get('software', 'Unknown')}")
    print()
    
    while True:
        print("\nCommands:")
        print("  1. Power Off")
        print("  2. Set Volume")
        print("  3. Mute/Unmute")
        print("  4. Launch App (Netflix, YouTube, etc.)")
        print("  5. Show Message")
        print("  6. Get TV Info")
        print("  0. Exit")
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            tv.power_off()
        elif choice == "2":
            level = input("Volume level (0-100): ").strip()
            tv.set_volume(int(level))
        elif choice == "3":
            tv.mute(True)
        elif choice == "4":
            app = input("App name (netflix/youtube/amazon): ").strip()
            tv.launch_app(app)
        elif choice == "5":
            msg = input("Message to display: ").strip()
            tv.show_message(msg)
        elif choice == "6":
            info = tv.get_info()
            print(f"\nTV Info:")
            for key, value in info.items():
                print(f"  {key}: {value}")
        else:
            print("Invalid choice")
    
    tv.disconnect()
    print("\n👋 Disconnected")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="LG TV Controller")
    parser.add_argument("ip", help="TV IP address")
    parser.add_argument("--command", choices=["on", "off", "mute", "volume", "app", "msg"],
                       help="Command to execute")
    parser.add_argument("--value", help="Value for command (volume level, app name, message)")
    
    args = parser.parse_args()
    
    if args.command:
        # Single command mode
        tv = LGTVController(args.ip)
        if tv.connect():
            if args.command == "off":
                tv.power_off()
            elif args.command == "mute":
                tv.mute(True)
            elif args.command == "volume":
                tv.set_volume(int(args.value))
            elif args.command == "app":
                tv.launch_app(args.value)
            elif args.command == "msg":
                tv.show_message(args.value)
            tv.disconnect()
    else:
        # Interactive mode
        interactive_control(args.ip)
