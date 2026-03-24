#!/usr/bin/env python3
"""
Interactive Embodiment Layer Demo
Control simulated IoT devices and see how Lux interacts with the physical world.
"""

import sys
import time
from pathlib import Path

# Add workspace to path
sys.path.insert(0, str(Path.home() / ".openclaw" / "workspace"))
sys.path.insert(0, str(Path.home() / ".openclaw" / "workspace" / "skills" / "embodiment-layer"))

from embodiment_core import EmbodimentLayer


def print_header(text):
    print("\n" + "=" * 50)
    print(f"  {text}")
    print("=" * 50)


def interactive_demo():
    """Run interactive embodiment demo."""
    print_header("🤖 LUX EMBODIMENT LAYER - INTERACTIVE DEMO")
    print("\nThis demo shows how Lux can control physical devices.")
    print("All devices are simulated (demo mode).\n")
    
    # Initialize embodiment layer
    embodiment = EmbodimentLayer(demo_mode=True)
    
    while True:
        print("\n📋 Available Commands:")
        print("  1. List all devices")
        print("  2. Control a device")
        print("  3. Read sensors")
        print("  4. Set trading mode")
        print("  5. Simulate trade alert")
        print("  6. Create automation")
        print("  7. RPA Demo")
        print("  0. Exit")
        
        choice = input("\n👉 Enter choice (0-7): ").strip()
        
        if choice == "0":
            print("\n👋 Goodbye!")
            break
            
        elif choice == "1":
            print_header("📱 CONNECTED DEVICES")
            devices = embodiment.list_devices()
            for i, device in enumerate(devices, 1):
                status = f"{device['state']}"
                if 'brightness' in device:
                    status += f" ({device['brightness']}% brightness)"
                if 'temperature' in device:
                    status += f" ({device['temperature']}°C)"
                print(f"  {i}. {device['id']}")
                print(f"     Type: {device['type']} | Status: {status}")
                print()
                
        elif choice == "2":
            print_header("💡 DEVICE CONTROL")
            print("Available devices:")
            devices = embodiment.list_devices()
            for i, device in enumerate(devices, 1):
                print(f"  {i}. {device['id']} ({device['type']})")
            
            device_num = input("\nSelect device (number): ").strip()
            try:
                device = devices[int(device_num) - 1]
                device_id = device['id']
                
                print(f"\nSelected: {device_id}")
                print("\nActions:")
                print("  1. Turn ON")
                print("  2. Turn OFF")
                print("  3. Set brightness")
                print("  4. Set color")
                
                action_choice = input("\nSelect action: ").strip()
                
                if action_choice == "1":
                    result = embodiment.control_device(device_id, "turn_on")
                    print(f"\n✅ {device_id} turned ON")
                elif action_choice == "2":
                    result = embodiment.control_device(device_id, "turn_off")
                    print(f"\n✅ {device_id} turned OFF")
                elif action_choice == "3":
                    brightness = input("Enter brightness (0-100): ").strip()
                    result = embodiment.control_device(device_id, "set_brightness", 
                                                      brightness=int(brightness))
                    print(f"\n✅ Brightness set to {brightness}%")
                elif action_choice == "4":
                    color = input("Enter color (white/red/green/blue/warm_white): ").strip()
                    result = embodiment.control_device(device_id, "set_color", color=color)
                    print(f"\n✅ Color changed to {color}")
                    
            except (ValueError, IndexError):
                print("\n❌ Invalid selection")
                
        elif choice == "3":
            print_header("📊 SENSOR READINGS")
            sensors = embodiment.read_sensors()
            for sensor_id, data in sensors.items():
                print(f"  • {sensor_id}: {data['value']:.2f} {data['unit']}")
                print(f"    Last updated: {data['timestamp']}")
                print()
                
        elif choice == "4":
            print_header("🎯 TRADING MODE")
            print("Modes:")
            print("  1. focus - Dim lights, trading dashboard")
            print("  2. alert - Visual alerts for trades")
            print("  3. monitor - Keep displays on")
            
            mode_choice = input("\nSelect mode: ").strip()
            modes = {"1": "focus", "2": "alert", "3": "monitor"}
            
            if mode_choice in modes:
                result = embodiment.set_trading_mode(modes[mode_choice])
                print(f"\n✅ Trading mode set to: {modes[mode_choice]}")
                print("\nActions taken:")
                for action in result['actions']:
                    if action.get('success'):
                        print(f"  • {action['device']}: {action['action']}")
            else:
                print("\n❌ Invalid mode")
                
        elif choice == "5":
            print_header("💰 TRADE ALERT")
            symbol = input("Enter token symbol (e.g., SOL): ").strip() or "SOL"
            side = input("Buy or Sell? ").strip().lower() or "buy"
            
            embodiment.alert_trade_executed({
                "symbol": symbol.upper(),
                "side": side,
                "amount": 0.1,
                "price": 150.0
            })
            
            color = "GREEN" if side == "buy" else "RED"
            print(f"\n✅ Office lamp flashed {color} for {side.upper()} signal!")
            
        elif choice == "6":
            print_header("🤖 CREATE AUTOMATION")
            name = input("Automation name: ").strip() or "My Automation"
            
            print("\nTrigger types:")
            print("  1. Time-based (e.g., 09:00)")
            print("  2. Sensor-based (e.g., motion detected)")
            
            trigger_type = input("Select trigger type: ").strip()
            
            if trigger_type == "1":
                time_str = input("Enter time (HH:MM): ").strip() or "09:00"
                trigger = {"type": "time", "at": time_str}
            else:
                trigger = {"type": "motion", "sensor": "motion_detector"}
            
            print("\nAvailable devices:")
            devices = embodiment.list_devices()
            for i, device in enumerate(devices, 1):
                print(f"  {i}. {device['id']}")
            
            device_num = input("\nSelect device to control: ").strip()
            try:
                device_id = devices[int(device_num) - 1]['id']
                action = input("Action (turn_on/turn_off): ").strip() or "turn_on"
                
                rule_id = embodiment.create_automation(name, trigger, 
                                                       {"device": device_id, "action": action})
                print(f"\n✅ Automation '{name}' created!")
                print(f"   Rule ID: {rule_id}")
                
            except (ValueError, IndexError):
                print("\n❌ Invalid selection")
                
        elif choice == "7":
            print_header("🖱️  RPA (ROBOTIC PROCESS AUTOMATION)")
            print("Simulating desktop automation...")
            print()
            
            print("1. Moving mouse to position (500, 300)...")
            embodiment.rpa_click(500, 300)
            time.sleep(0.5)
            
            print("2. Typing message...")
            embodiment.rpa_type("Lux is controlling the computer!")
            time.sleep(0.5)
            
            print("3. Taking screenshot...")
            filename = embodiment.rpa_screenshot()
            print(f"   Screenshot saved: {filename}")
            
            print("\n✅ RPA demo complete!")
            
        else:
            print("\n❌ Invalid choice")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        interactive_demo()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
