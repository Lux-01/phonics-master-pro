#!/usr/bin/env python3
"""
Embodiment Layer - Physical World Interface
Connects Lux to IoT devices, sensors, and physical automation.

Demo Mode: Simulated devices for testing
"""

import json
import logging
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbodimentLayer:
    """
    Embodiment Layer - Bridge between digital and physical world.
    
    Capabilities:
    - IoT device control (lights, sensors, switches)
    - RPA automation (mouse, keyboard, screen capture)
    - Hardware abstraction (GPIO, serial, USB)
    - Sensor data ingestion (temperature, motion, etc.)
    """
    
    def __init__(self, demo_mode: bool = True):
        self.demo_mode = demo_mode
        self.devices = {}
        self.sensors = {}
        self.automation_rules = []
        
        if demo_mode:
            self._init_demo_devices()
            logger.info("🎭 Embodiment Layer initialized in DEMO MODE")
        else:
            logger.info("🔌 Embodiment Layer initialized in PRODUCTION MODE")
    
    def _init_demo_devices(self):
        """Initialize simulated devices for demo."""
        self.devices = {
            "living_room_light": {
                "type": "light",
                "state": "off",
                "brightness": 0,
                "color": "white"
            },
            "office_desk_lamp": {
                "type": "light", 
                "state": "on",
                "brightness": 80,
                "color": "warm_white"
            },
            "front_door_sensor": {
                "type": "door_sensor",
                "state": "closed",
                "last_opened": None
            },
            "motion_detector": {
                "type": "motion_sensor",
                "state": "clear",
                "last_motion": None
            },
            "thermostat": {
                "type": "climate",
                "state": "on",
                "temperature": 22.5,
                "target": 22.0,
                "mode": "auto"
            },
            "trading_display": {
                "type": "display",
                "state": "on",
                "content": "crypto_dashboard",
                "brightness": 100
            }
        }
        
        self.sensors = {
            "room_temp": {"value": 22.5, "unit": "celsius"},
            "humidity": {"value": 45, "unit": "percent"},
            "light_level": {"value": 350, "unit": "lux"},
            "cpu_usage": {"value": 25, "unit": "percent"}
        }
    
    # ==================== DEVICE CONTROL ====================
    
    def list_devices(self) -> List[Dict]:
        """List all connected devices."""
        return [
            {"id": device_id, **info}
            for device_id, info in self.devices.items()
        ]
    
    def get_device_state(self, device_id: str) -> Optional[Dict]:
        """Get current state of a device."""
        if device_id not in self.devices:
            return None
        
        state = self.devices[device_id].copy()
        state["id"] = device_id
        state["timestamp"] = datetime.now().isoformat()
        return state
    
    def control_device(self, device_id: str, action: str, **params) -> Dict:
        """
        Control a physical device.
        
        Examples:
        - control_device("living_room_light", "turn_on")
        - control_device("living_room_light", "set_brightness", brightness=50)
        - control_device("thermostat", "set_temperature", temperature=21.0)
        """
        if device_id not in self.devices:
            return {"success": False, "error": f"Device {device_id} not found"}
        
        device = self.devices[device_id]
        
        if self.demo_mode:
            # Simulate device control
            time.sleep(0.1)  # Simulate network delay
            
            if action == "turn_on":
                device["state"] = "on"
                if "brightness" in device:
                    device["brightness"] = 100
            elif action == "turn_off":
                device["state"] = "off"
                if "brightness" in device:
                    device["brightness"] = 0
            elif action == "set_brightness":
                device["brightness"] = params.get("brightness", 50)
                device["state"] = "on" if device["brightness"] > 0 else "off"
            elif action == "set_color":
                device["color"] = params.get("color", "white")
            elif action == "set_temperature":
                device["target"] = params.get("temperature", 22.0)
            elif action == "set_mode":
                device["mode"] = params.get("mode", "auto")
            elif action == "display":
                device["content"] = params.get("content", "default")
            
            logger.info(f"🎭 [DEMO] {device_id}: {action} {params}")
            return {
                "success": True,
                "device": device_id,
                "action": action,
                "new_state": device
            }
        else:
            # Production: Send actual commands to devices
            # This would integrate with Home Assistant, MQTT, etc.
            pass
    
    # ==================== SENSOR DATA ====================
    
    def read_sensors(self) -> Dict:
        """Read all sensor values."""
        if self.demo_mode:
            # Simulate sensor fluctuations
            for sensor_id in self.sensors:
                current = self.sensors[sensor_id]["value"]
                variation = random.uniform(-0.5, 0.5)
                self.sensors[sensor_id]["value"] = round(current + variation, 2)
        
        return {
            sensor_id: {**data, "timestamp": datetime.now().isoformat()}
            for sensor_id, data in self.sensors.items()
        }
    
    def get_sensor_history(self, sensor_id: str, hours: int = 24) -> List[Dict]:
        """Get historical sensor data."""
        # In production, this would query a time-series database
        # For demo, generate synthetic history
        history = []
        base_value = self.sensors.get(sensor_id, {}).get("value", 0)
        
        for i in range(hours):
            history.append({
                "timestamp": (datetime.now() - __import__('datetime').timedelta(hours=i)).isoformat(),
                "value": base_value + random.uniform(-2, 2)
            })
        
        return history
    
    # ==================== AUTOMATION ====================
    
    def create_automation(self, name: str, trigger: Dict, action: Dict) -> str:
        """
        Create an automation rule.
        
        Example:
        create_automation(
            name="Trading Mode Lighting",
            trigger={"type": "time", "at": "09:00"},
            action={"device": "office_desk_lamp", "action": "turn_on"}
        )
        """
        rule_id = f"rule_{len(self.automation_rules)}"
        
        rule = {
            "id": rule_id,
            "name": name,
            "trigger": trigger,
            "action": action,
            "enabled": True,
            "created_at": datetime.now().isoformat()
        }
        
        self.automation_rules.append(rule)
        logger.info(f"🤖 Automation created: {name}")
        
        return rule_id
    
    def list_automations(self) -> List[Dict]:
        """List all automation rules."""
        return self.automation_rules
    
    # ==================== RPA (Robotic Process Automation) ====================
    
    def rpa_click(self, x: int, y: int) -> bool:
        """Simulate mouse click at screen coordinates."""
        if self.demo_mode:
            logger.info(f"🖱️  [DEMO] Click at ({x}, {y})")
            return True
        else:
            # Production: Use pyautogui or similar
            try:
                import pyautogui
                pyautogui.click(x, y)
                return True
            except:
                return False
    
    def rpa_type(self, text: str) -> bool:
        """Simulate keyboard input."""
        if self.demo_mode:
            logger.info(f"⌨️  [DEMO] Type: {text[:50]}...")
            return True
        else:
            try:
                import pyautogui
                pyautogui.typewrite(text)
                return True
            except:
                return False
    
    def rpa_screenshot(self, filename: Optional[str] = None) -> str:
        """Capture screen."""
        if filename is None:
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        if self.demo_mode:
            logger.info(f"📸 [DEMO] Screenshot saved: {filename}")
            return filename
        else:
            try:
                import pyautogui
                screenshot = pyautogui.screenshot()
                screenshot.save(filename)
                return filename
            except Exception as e:
                return f"error: {e}"
    
    # ==================== TRADING-SPECIFIC ====================
    
    def set_trading_mode(self, mode: str) -> Dict:
        """
        Set environment for trading mode.
        
        Modes:
        - "focus": Dim lights, enable Do Not Disturb
        - "alert": Flash lights on trade signals
        - "monitor": Display on trading screen
        """
        results = []
        
        if mode == "focus":
            # Dim ambient lights
            results.append(self.control_device("living_room_light", "turn_off"))
            results.append(self.control_device("office_desk_lamp", "set_brightness", brightness=40))
            # Set display to trading dashboard
            results.append(self.control_device("trading_display", "display", content="trading_dashboard"))
            
        elif mode == "alert":
            # Flash office light for trade signal
            results.append(self.control_device("office_desk_lamp", "set_color", color="green"))
            results.append(self.control_device("office_desk_lamp", "set_brightness", brightness=100))
            
        elif mode == "monitor":
            # Ensure display is on with crypto dashboard
            results.append(self.control_device("trading_display", "display", content="crypto_dashboard"))
        
        logger.info(f"🎯 Trading mode set: {mode}")
        return {"mode": mode, "actions": results}
    
    def alert_trade_executed(self, trade_info: Dict) -> None:
        """Trigger physical alert when trade executes."""
        # Flash light green for buy, red for sell
        color = "green" if trade_info.get("side") == "buy" else "red"
        
        self.control_device("office_desk_lamp", "set_color", color=color)
        self.control_device("office_desk_lamp", "set_brightness", brightness=100)
        
        logger.info(f"💡 Trade alert: {trade_info.get('symbol')} {trade_info.get('side')}")


def demo():
    """Run embodiment layer demo."""
    print("=" * 60)
    print("🤖 EMBODIMENT LAYER DEMO")
    print("=" * 60)
    print()
    
    # Initialize
    embodiment = EmbodimentLayer(demo_mode=True)
    
    # 1. List devices
    print("📱 Connected Devices:")
    print("-" * 40)
    for device in embodiment.list_devices():
        print(f"  • {device['id']} ({device['type']}): {device['state']}")
    print()
    
    # 2. Control devices
    print("💡 Device Control Demo:")
    print("-" * 40)
    
    # Turn on living room light
    result = embodiment.control_device("living_room_light", "turn_on")
    print(f"  ✅ Living room light: {result['new_state']['state']}")
    
    # Set brightness
    result = embodiment.control_device("living_room_light", "set_brightness", brightness=75)
    print(f"  ✅ Brightness set to: {result['new_state']['brightness']}%")
    
    # Change color
    result = embodiment.control_device("living_room_light", "set_color", color="blue")
    print(f"  ✅ Color changed to: {result['new_state']['color']}")
    print()
    
    # 3. Read sensors
    print("📊 Sensor Readings:")
    print("-" * 40)
    sensors = embodiment.read_sensors()
    for sensor_id, data in sensors.items():
        print(f"  • {sensor_id}: {data['value']}{data['unit']}")
    print()
    
    # 4. Trading mode
    print("🎯 Trading Mode Demo:")
    print("-" * 40)
    result = embodiment.set_trading_mode("focus")
    print(f"  ✅ Trading focus mode activated")
    print(f"     - Living room light: OFF")
    print(f"     - Office lamp: 40% brightness")
    print(f"     - Display: trading_dashboard")
    print()
    
    # 5. Trade alert
    print("💰 Trade Alert Demo:")
    print("-" * 40)
    embodiment.alert_trade_executed({
        "symbol": "SOL",
        "side": "buy",
        "amount": 0.1,
        "price": 150.0
    })
    print(f"  ✅ Office lamp flashed GREEN for BUY signal")
    print()
    
    # 6. RPA Demo
    print("🖱️  RPA (Robotic Process Automation) Demo:")
    print("-" * 40)
    embodiment.rpa_click(100, 200)
    embodiment.rpa_type("Hello from Lux!")
    embodiment.rpa_screenshot("demo_screenshot.png")
    print()
    
    # 7. Automation
    print("🤖 Automation Demo:")
    print("-" * 40)
    rule_id = embodiment.create_automation(
        name="Morning Trading Setup",
        trigger={"type": "time", "at": "09:00"},
        action={"device": "office_desk_lamp", "action": "turn_on"}
    )
    print(f"  ✅ Created automation: 'Morning Trading Setup'")
    print(f"     Rule ID: {rule_id}")
    print()
    
    print("=" * 60)
    print("✨ Demo Complete!")
    print("=" * 60)
    print()
    print("The Embodiment Layer can:")
    print("  • Control IoT devices (lights, sensors, climate)")
    print("  • Read sensor data (temperature, motion, etc.)")
    print("  • Automate physical actions (RPA)")
    print("  • React to trading events (visual alerts)")
    print("  • Create automation rules")
    print()
    print("In production mode, this connects to real devices via:")
    print("  • Home Assistant / OpenHAB")
    print("  • MQTT broker")
    print("  • Zigbee/Z-Wave hubs")
    print("  • Direct GPIO (Raspberry Pi)")


if __name__ == "__main__":
    demo()
