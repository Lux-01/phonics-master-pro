#!/usr/bin/env python3
"""
Test AgentMail - send via messages or drafts
"""

from agentmail import AgentMail

API_KEY = "am_us_55b6203ca856b8c298adae29bfeb4365b6d84cc90aaf0fcc86b1abaeb498ceb2"
INBOX = "vivaciousguitar330@agentmail.to"

client = AgentMail(api_key=API_KEY)
inboxes = client.inboxes

print("=" * 60)
print("AgentMail: Testing Messages and Drafts")
print("=" * 60)
print()

# Method 1: Try inboxes.messages
print("Method 1: inboxes.messages")
print(f"  Type: {type(inboxes.messages)}")
print(f"  Methods: {[m for m in dir(inboxes.messages) if not m.startswith('_')]}")

try:
    # List messages first
    messages = inboxes.messages.list(inbox_id=INBOX)
    print(f"  ✅ Messages listed: {len(messages) if hasattr(messages, '__len__') else messages}")
except Exception as e:
    print(f"  ❌ Failed to list: {e}")

# Try send message
print("\n  Trying to send message...")
try:
    message = inboxes.messages.send(
        inbox_id=INBOX,
        to="skux@example.com",
        subject="Test from LuxTrader v3.0",
        body="This is a test email sent via AgentMail SDK! ✨"
    )
    print(f"  ✅ Message sent!")
    print(f"     Message: {message}")
except Exception as e:
    print(f"  ❌ Failed: {e}")

print()

# Method 2: Try inboxes.drafts  
print("Method 2: inboxes.drafts")
print(f"  Type: {type(inboxes.drafts)}")
print(f"  Methods: {[m for m in dir(inboxes.drafts) if not m.startswith('_')]}")

try:
    # Create draft
    draft = inboxes.drafts.create(
        inbox_id=INBOX,
        to=["skux@example.com"],
        subject="Test Draft from LuxTrader",
        body="This is a test draft"
    )
    print(f"  ✅ Draft created: {draft}")
except Exception as e:
    print(f"  ❌ Failed: {e}")

print()

# Method 3: Try inboxes.threads
print("Method 3: inboxes.threads")
print(f"  Type: {type(inboxes.threads)}")
print(f"  Methods: {[m for m in dir(inboxes.threads) if not m.startswith('_')]}")

try:
    threads = inboxes.threads.list(inbox_id=INBOX)
    print(f"  ✅ Threads listed: {len(threads.threads) if hasattr(threads, 'threads') else threads}")
except Exception as e:
    print(f"  ❌ Failed: {e}")

print()
print("=" * 60)
