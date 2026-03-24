#!/usr/bin/env python3
"""
Send OpenClaw installer via AgentMail
"""

from agentmail import AgentMail
import base64
import os
from pathlib import Path

# Load from .env file or environment
def load_env():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ.setdefault(key, value)

load_env()

API_KEY = os.getenv('AGENTMAIL_API_KEY')
if not API_KEY:
    raise ValueError("AGENTMAIL_API_KEY not set. Create .env file with AGENTMAIL_API_KEY=your_key")

INBOX = os.getenv('AGENTMAIL_INBOX', 'vivaciousguitar330@agentmail.to')
TO_EMAIL = os.getenv('TO_EMAIL', 'cjalloh64@gmail.com')

client = AgentMail(api_key=API_KEY)

# Read the installer package
with open("/home/skux/.openclaw/workspace/openclaw-installer-package.tar.gz", "rb") as f:
    attachment_data = f.read()

attachment_base64 = base64.b64encode(attachment_data).decode('utf-8')

# Send email
response = client.inboxes.messages.send(
    inbox_id=INBOX,
    to=TO_EMAIL,
    subject="OpenClaw Windows Installer - Ready to Install!",
    text="""Hi there,

Your OpenClaw installer package is attached!

WHAT'S INCLUDED:
- INSTALL-OPENCLAW.bat (run this as Administrator)
- openclaw-windows-installer.ps1 (the main script)
- INSTALLATION-GUIDE.md (full manual instructions)
- README.md (quick reference)
- INSTRUCTIONS.txt (install + uninstall guide)

QUICK INSTALL:
1. Extract the .tar.gz file (use 7-Zip or WinRAR)
2. Right-click INSTALL-OPENCLAW.bat → "Run as administrator"
3. Wait 20-30 minutes
4. Reboot when prompted
5. Done!

UNINSTALL INSTRUCTIONS are also in INSTRUCTIONS.txt if you need to remove Linux/WSL later.

This installs:
- WSL2 + Ubuntu 22.04
- Ollama AI server
- Kimi-K2.5 model (~4GB)
- OpenClaw gateway

Questions? Ask your coworker who sent this!

Good luck! 🤖

- OpenClaw Team""",
    attachments=[{
        "filename": "openclaw-installer-package.tar.gz",
        "content": attachment_base64,
        "content_type": "application/gzip"
    }]
)

print(f"✅ Email sent to {TO_EMAIL}")
print(f"Message ID: {response.message_id if hasattr(response, 'message_id') else response}")
