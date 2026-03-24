#!/usr/bin/env python3
"""
Build script to create OpenClaw Windows Installer executable
"""
import os
import sys
import subprocess
import shutil

# Read the PowerShell installer script
with open('openclaw-gui-installer.ps1', 'r') as f:
    ps_script = f.read()

# Create a Python wrapper that will be compiled to exe
wrapper_code = '''
import subprocess
import sys
import os
import tempfile

# Embedded PowerShell script
PS_SCRIPT = """
''' + ps_script.replace('"""', '""""') + '''
"""

def main():
    # Create temp file for the PowerShell script
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False) as f:
        f.write(PS_SCRIPT)
        ps_path = f.name
    
    try:
        # Run the PowerShell script
        if sys.platform == 'win32':
            # Windows - run PowerShell
            subprocess.run(['powershell.exe', '-ExecutionPolicy', 'Bypass', '-File', ps_path], check=False)
        else:
            print("This installer is for Windows only.")
            print("Please run this on a Windows machine.")
    finally:
        # Cleanup
        try:
            os.unlink(ps_path)
        except:
            pass

if __name__ == '__main__':
    main()
'''

# Write the wrapper
with open('openclaw_installer_wrapper.py', 'w') as f:
    f.write(wrapper_code)

print("Wrapper created. Building executable with PyInstaller...")

# Build with PyInstaller
subprocess.run([
    sys.executable, '-m', 'PyInstaller',
    '--onefile',
    '--name', 'OpenClaw-Installer-v3.1',
    '--icon', 'NONE',
    '--clean',
    'openclaw_installer_wrapper.py'
], check=True)

print("Build complete!")
print("Executable location: dist/OpenClaw-Installer-v3.1.exe")
