#!/usr/bin/env python3
"""
Test AgentMail - send via threads or emails endpoint
"""

from agentmail import AgentMail

API_KEY = "am_us_55b6203ca856b8c298adae29bfeb4365b6d84cc90aaf0fcc86b1abaeb498ceb2"
INBOX = "vivaciousguitar330@agentmail.to"

client = AgentMail(api_key=API_KEY)

print("=" * 60)
print("Testing AgentMail - Send Methods")
print("=" * 60)
print()

# Method 1: Try client.threads.send
print("Method 1: client.threads.send")
try:
    thread = client.threads.send(
        inbox_id=INBOX,
        to=["skux@example.com"],
        subject="Test from LuxTrader",
        body="This is a test email via threads.send!"
    )
    print(f"✅ Success!")
    print(f"   Thread ID: {thread.id if hasattr(thread, 'id') else thread}")
except Exception as e:
    print(f"❌ Failed: {e}")

print()

# Method 2: Try client.threads.create with message
print("Method 2: threads.create")
try:
    thread = client.threads.create(inbox_id=INBOX)
    print(f"Thread created: {thread}")
    print(f"Thread attributes: {[attr for attr in dir(thread) if not attr.startswith('_')]}")
except Exception as e:
    print(f"❌ Failed: {e}")

print()

# Method 3: Check client.emails
print("Method 3: client.emails")
if hasattr(client, 'emails'):
    print(f"   Found emails: {client.emails}")
    print(f"   Type: {type(client.emails)}")
    print(f"   Attributes: {[attr for attr in dir(client.emails) if not attr.startswith('_')]}")
    
    # Try send
    try:
        email = client.emails.send(
            inbox_id=INBOX,
            to=["skux@example.com"],
            subject="Test from LuxTrader",
            body="This is a test via client.emails.send!"
        )
        print(f"✅ Email sent!")
        print(f"   Response: {email}")
    except Exception as e:
        print(f"❌ Failed: {e}")
else:
    print("   No emails attribute")

print()
print("=" * 60)
print()

# List threads
print("Listing threads...")
try:
    threads = client.threads.list(inbox_id=INBOX)
    print(f"Found {len(threads.threads) if hasattr(threads, 'threads') else threads} threads")
except Exception as e:
    print(f"❌ Failed: {e}")

print()
print("=" * 60)
print("Complete!")
print("=" * 60)
