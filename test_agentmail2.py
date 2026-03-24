#!/usr/bin/env python3
"""
Test AgentMail API with project headers
"""

import requests
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

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "x-project-id": "default",
}

# Try sending a test email
test_email = {
    "to": ["test@example.com"],
    "subject": "AgentMail Test Connection",
    "body": "This is a test email from LuxTrader. If you receive this, the connection is working! ✨",
}

print("Testing AgentMail SEND capability...")
print(f"From: {INBOX}")
print("-" * 60)

url = "https://api.agentmail.to/inboxes/emails"
try:
    response = requests.post(url, headers=headers, json=test_email, timeout=10)
    print(f"URL: {url}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    if response.status_code in [200, 201, 202]:
        print("✅ Send test SUCCESS!")
    else:
        print("❌ Send test failed")
except Exception as e:
    print(f"Error: {e}")

# Try listing inboxes
print("\nTesting AgentMail LIST inboxes...")
url = "https://api.agentmail.to/inboxes"
try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    if response.status_code == 200:
        print("✅ List inboxes SUCCESS!")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "-" * 60)
