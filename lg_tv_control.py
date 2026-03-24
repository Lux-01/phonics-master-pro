#!/usr/bin/env python3
"""
LG TV Controller
Control your webOS LG TV remotely

Usage:
    python3 lg_tv_control.py --discover          # Find TV on network
    python3 lg_tv_control.py --pair <IP>         # Pair with TV (one-time)
    python3 lg_tv_control.py --ip <IP> --command power_off
    python3 lg_tv_control.py --ip <IP> --command volume_up
"""

import argparse
import sys
import os
from pywebostv.discovery import discover
from pywebostv.connection import WebOSClient
from pywebostv.controls import SystemControl, MediaControl, ApplicationControl, InputControl

# Store credentials
CREDENTIALS_FILE = os.path.expanduser("~/.lg_tv_credentials")

def save_credentials(ip, credentials):
    """Save TV credentials for future use"""
    with open(CREDENTIALS_FILE, "w") as f:
        f.write(f"{ip}\n")
        f.write(str(credentials))
    print(f"[+] Credentials saved to {CREDENTIALS_FILE}")

def load_credentials():
    """Load saved credentials"""
    if not os.path.exists(CREDENTIALS_FILE):
        return None, None
    with open(CREDENTIALS_FILE, "r") as f:
        lines = f.readlines()
        ip = lines[0].strip()
        credentials = eval(lines[1])
        return ip, credentials

def discover_tv():
    """Discover LG TVs on network"""
    print("[*] Searching for LG TVs on network...")
    print("[*] Make sure TV is turned on and connected to same network")
    print()
    
    try:
        tvs = discover("ssdp:webostv")
        if tvs:
            print(f"[+] Found {len(tvs)} TV(s):")
            for i, tv in enumerate(tvs, 1):
                print(f"    {i}. {tv['name']} at {tv['ip']}")
            return tvs
        else:
            print("[-] No TVs found. Make sure TV is on and connected.")
            return []
    except Exception as e:
        print(f"[-] Discovery failed: {e}")
        return []

def pair_tv(ip):
    """Pair with TV (one-time setup)"""
    print(f"[*] Connecting to TV at {ip}...")
    print("[*] Please accept the pairing prompt on your TV screen!")
    print()
    
    client = WebOSClient(ip)
    client.connect()
    
    for status in client.register():
        if status == WebOSClient.PROMPTED:
            print("[!] Please accept the connection on your TV...")
        elif status == WebOSClient.REGISTERED:
            print("[+] Successfully paired with TV!")
    
    # Save credentials
    save_credentials(ip, client.credentials)
    
    client.close()
    return True

def connect_to_tv(ip=None):
    """Connect to TV using saved or provided IP"""
    if ip is None:
        ip, credentials = load_credentials()
        if ip is None:
            print("[-] No saved TV found. Use --discover and --pair first.")
            return None
    else:
        _, credentials = load_credentials()
        if credentials is None:
            print("[-] TV not paired. Use --pair first.")
            return None
    
    client = WebOSClient(ip)
    client.connect()
    
    if credentials:
        client.register(credentials)
    else:
        for status in client.register():
            if status == WebOSClient.PROMPTED:
                print("[!] Accept connection on TV...")
            elif status == WebOSClient.REGISTERED:
                print("[+] Connected!")
    
    return client

def send_command(client, command):
    """Send command to TV"""
    system = SystemControl(client)
    media = MediaControl(client)
    app = ApplicationControl(client)
    inp = InputControl(client)
    
    commands = {
        # Power
        'power_off': lambda: system.power_off(),
        
        # Volume
        'volume_up': lambda: media.volume_up(),
        'volume_down': lambda: media.volume_down(),
        'mute': lambda: media.mute(),
        'unmute': lambda: media.unmute(),
        
        # Playback
        'play': lambda: media.play(),
        'pause': lambda: media.pause(),
        'stop': lambda: media.stop(),
        'rewind': lambda: media.rewind(),
        'fast_forward': lambda: media.fast_forward(),
        
        # Apps
        'netflix': lambda: app.launch('netflix'),
        'youtube': lambda: app.launch('youtube.leanback.v4'),
        'prime': lambda: app.launch('amazon'),
        'disney': lambda: app.launch('com.disney.disneyplus'),
        'spotify': lambda: app.launch('spotify'),
        
        # Input
        'home': lambda: inp.home(),
        'back': lambda: inp.back(),
        'ok': lambda: inp.ok(),
        'up': lambda: inp.up(),
        'down': lambda: inp.down(),
        'left': lambda: inp.left(),
        'right': lambda: inp.right(),
        
        # Info
        'info': lambda: print_system_info(system),
    }
    
    if command in commands:
        try:
            commands[command]()
            print(f"[+] Command '{command}' sent successfully")
        except Exception as e:
            print(f"[-] Command failed: {e}")
    else:
        print(f"[-] Unknown command: {command}")
        print(f"[*] Available commands: {', '.join(commands.keys())}")

def print_system_info(system):
    """Print TV system info"""
    try:
        info = system.info()
        print(f"[+] TV Info:")
        print(f"    Model: {info.get('modelName', 'Unknown')}")
        print(f"    Version: {info.get('sdkVersion', 'Unknown')}")
        print(f"    TV Name: {info.get('deviceId', 'Unknown')}")
    except Exception as e:
        print(f"[-] Could not get info: {e}")

def main():
    parser = argparse.ArgumentParser(description='LG TV Controller')
    parser.add_argument('--discover', action='store_true', help='Discover TVs on network')
    parser.add_argument('--pair', metavar='IP', help='Pair with TV at IP address')
    parser.add_argument('--ip', help='TV IP address')
    parser.add_argument('--command', help='Command to send')
    parser.add_argument('--list-commands', action='store_true', help='List available commands')
    
    args = parser.parse_args()
    
    if args.list_commands:
        print("Available commands:")
        print("  Power: power_off")
        print("  Volume: volume_up, volume_down, mute, unmute")
        print("  Playback: play, pause, stop, rewind, fast_forward")
        print("  Apps: netflix, youtube, prime, disney, spotify")
        print("  Navigation: home, back, ok, up, down, left, right")
        print("  Info: info")
        return
    
    if args.discover:
        tvs = discover_tv()
        if tvs:
            print(f"\n[*] To pair: python3 lg_tv_control.py --pair {tvs[0]['ip']}")
        return
    
    if args.pair:
        pair_tv(args.pair)
        return
    
    if args.command:
        client = connect_to_tv(args.ip)
        if client:
            send_command(client, args.command)
            client.close()
        return
    
    # No arguments - show help
    parser.print_help()
    print("\n[*] Quick start:")
    print("  1. python3 lg_tv_control.py --discover")
    print("  2. python3 lg_tv_control.py --pair <TV_IP>")
    print("  3. python3 lg_tv_control.py --command power_off")

if __name__ == '__main__':
    main()
