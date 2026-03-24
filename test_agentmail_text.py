#!/usr/bin/env python3
"""
Test AgentMail - correct parameters
"""

from agentmail import AgentMail
import inspect
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

client = AgentMail(api_key=API_KEY)
inboxes = client.inboxes

print("=" * 60)
print("AgentMail: Checking Send Parameters")
print("=" * 60)
print()

# Check send signature
print("inboxes.messages.send signature:")
send_method = inboxes.messages.send
print(f"  {inspect.signature(send_method)}")

# Check create draft signature
print("\ninboxes.drafts.send signature:")
draft_send = inboxes.drafts.send
print(f"  {inspect.signature(draft_send)}")

# Try send with text instead of body
print("\nSending message with 'text' parameter...")
try:
    message = inboxes.messages.send(
        inbox_id=INBOX,
        to="skux@example.com",
        subject="Test from LuxTrader v3.0",
        text="This is a test email sent via AgentMail SDK! ✨"
    )
    print(f"✅ Message sent!")
    print(f"   Message ID: {message.id if hasattr(message, 'id') else message}")
    print(f"   Message attrs: {[m for m in dir(message) if not m.startswith('_')]}")
except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()

# Try drafts.send
print("\nSending draft...")
try:
    draft = inboxes.drafts.send(
        inbox_id=INBOX,
        to="skux@example.com", 
        subject="Test Draft from LuxTrader",
        text="Test draft body"
    )
    print(f"✅ Draft sent!")
    print(f"   Draft: {draft}")
except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
