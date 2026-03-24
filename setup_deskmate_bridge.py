#!/usr/bin/env python3
"""
Desktop Mate Bridge Setup
Creates the Lua folder and script for Desktop Mate integration
"""

import os
import shutil
from pathlib import Path

# Configuration
SOURCE_LUA = "/home/skux/.openclaw/workspace/LuxBridge.lua"
BRIDGE_PATH = "/mnt/c/Users/HighE/DesktopMateLux"

def find_deskmate_lua_folder():
    """Try to find Desktop Mate's Lua folder"""
    potential_paths = [
        Path("/mnt/c/Users/HighE/AppData/Roaming/DesktopMate/_USER/Mods/Lua"),
        Path("/mnt/c/Users/HighE/AppData/Local/DesktopMate/Scripts/Lua"),
        Path("/mnt/c/Program Files (x86)/Steam/steamapps/common/DesktopMate/Mods/Lua"),
        Path("/mnt/c/Program Files/DesktopMate/Scripts/Lua"),
        Path("/mnt/c/Users/HighE/Documents/DesktopMate/Lua"),
        Path("/mnt/c/Users/HighE/DesktopMate/Scripts/Lua"),
        Path("/mnt/c/Steam/steamapps/common/DesktopMate/Mods/Lua"),
    ]
    
    found_paths = []
    for p in potential_paths:
        if p.exists():
            print(f"✅ Found existing Lua folder: {p}")
            found_paths.append(p)
        elif p.parent.exists() and "DesktopMate" in str(p):
            print(f"⚠️ DesktopMate partially found: {p.parent}")
    
    return found_paths

def create_lua_folder(base_path):
    """Create DesktopMate Lua folder structure"""
    lua_path = Path(base_path) / "_USER" / "Mods" / "Lua"
    try:
        lua_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created Lua folder: {lua_path}")
        return lua_path
    except Exception as e:
        print(f"❌ Failed to create Lua folder: {e}")
        return None

def install_lua_script(source, target_dir):
    """Copy Lua script to DesktopMate folder"""
    target_file = Path(target_dir) / "LuxBridge.lua"
    try:
        shutil.copy2(source, target_file)
        print(f"✅ Installed Lua script: {target_file}")
        return True
    except Exception as e:
        print(f"❌ Failed to install: {e}")
        return False

def verify_bridge_path():
    """Ensure bridge directory exists"""
    bridge_path = Path("/mnt/c/Users/HighE/DesktopMateLux")
    try:
        bridge_path.mkdir(parents=True, exist_ok=True)
        with open(bridge_path / "alerts.json", 'w') as f:
            f.write('')
        print(f"✅ Bridge directory ready: {bridge_path}")
        return True
    except Exception as e:
        print(f"❌ Bridge directory issue: {e}")
        return False

def main():
    print("="*80)
    print("  DESKTOP MATE BRIDGE SETUP")
    print("="*80)
    print()
    
    # Step 1: Verify bridge directory
    print("[1/4] Setting up bridge directory...")
    if verify_bridge_path():
        print("✓ Bridge path ready")
    else:
        print("⚠️ Bridge path may have issues")
    print()
    
    # Step 2: Find DesktopMate
    print("[2/4] Searching for DesktopMate Lua folder...")
    found_paths = find_deskmate_lua_folder()
    
    target_lua_folder = None
    if found_paths:
        print(f"\nFound {len(found_paths)} existing Lua folder(s)")
        lua_path = found_paths[0]  # Use first one
        print(f"Using: {lua_path}")
    else:
        print("\n❌ DesktopMate Lua folder not found")
        print("Creating recommended location...")
        # Create in AppData (common location)
        base = Path("/mnt/c/Users/HighE/AppData/Roaming/DesktopMate/_USER/Mods")
        lua_path = create_lua_folder(base)
        target_lua_folder = lua_path
    print()
    
    # Step 3: Install Lua script
    print("[3/4] Installing LuxBridge.lua...")
    if target_lua_folder:
        if install_lua_script(SOURCE_LUA, target_lua_folder):
            print("✓ Installation complete")
        else:
            print("⚠️ Check permissions and try again")
    print()
    
    # Step 4: Summary
    print("[4/4] Setup Summary:")
    print(f"  Bridge file: C:\\Users\\HighE\\DesktopMateLux\\alerts.json")
    if target_lua_folder:
        print(f"  Lua script: {target_lua_folder}\\LuxBridge.lua")
    print()
    print("Next steps:")
    print("  1. Start Desktop Mate (if not running)")
    print("  2. The script should auto-load")
    print("  3. Send a test alert:")
    print("     python3 /home/skux/.openclaw/workspace/demo_bridge.py")
    print()
    print("="*80)

if __name__ == "__main__":
    main()
