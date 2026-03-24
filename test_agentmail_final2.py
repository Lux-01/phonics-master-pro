#!/usr/bin/env python3
"""
Test AgentMail - final attempt with correct API
"""

from agentmail import AgentMail

API_KEY = "am_us_55b6203ca856b8c298adae29bfeb4365b6d84cc90aaf0fcc86b1abaeb498ceb2"
INBOX = "vivaciousguitar330@agentmail.to"

client = AgentMail(api_key=API_KEY)

print("=" * 60)
print("AgentMail Final Test")
print("=" * 60)
print()

# Check all client attributes
print("Client attributes:")
for attr in ['api_keys', 'domains', 'drafts', 'inboxes', 'metrics', 'organizations', 'pods', 'threads', 'webhooks', 'websockets']:
    obj = getattr(client, attr)
    print(f"  {attr}: {type(obj).__name__}")
    
    # Check methods
    methods = [m for m in dir(obj) if not m.startswith('_') and callable(getattr(obj, m, None))]
    if methods:
        print(f"    Methods: {', '.join(methods[:10])}")

print()

# Try client.inboxes.send_email
print("Trying client.inboxes.send_email...")
inbox_client = client.inboxes
print(f"Inbox client type: {type(inbox_client)}")
print(f"Inbox client methods: {[m for m in dir(inbox_client) if not m.startswith('_')]}")

try:
    response = inbox_client.send_email(
        inbox_id=INBOX,
        to=["skux@example.com"],
        subject="Test from LuxTrader",
        body="Test email body"
    )
    print(f"✅ Success: {response}")
except Exception as e:
    print(f"❌ Failed: {e}")

# Try without inbox_id (using inbox object)
print("\nTrying inbox.send_email...")
try:
    inbox_obj = client.inboxes.get(inbox_id=INBOX)
    print(f"Inbox object type: {type(inbox_obj)}")
    
    # Check inbox_obj.inbox
    if hasattr(inbox_obj, 'inbox'):
        inbox_data = inbox_obj.inbox
        print(f"Inbox data type: {type(inbox_data)}")
        print(f"Inbox data methods: {[m for m in dir(inbox_data) if not m.startswith('_')]}")
        
        # Try sending via inbox data
        try:
            response = inbox_data.send_email(
                to=["skux@example.com"],
                subject="Test from Inbox Data",
                body="Test body"
            )
            print(f"✅ Success: {response}")
        except Exception as e:
            print(f"❌ Failed: {e}")
    else:
        print(f"No inbox attribute on response")
        print(f"Response attributes: {[m for m in dir(inbox_obj) if not m.startswith('_')]}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
