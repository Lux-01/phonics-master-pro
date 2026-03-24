#!/usr/bin/env python3
"""
Test AgentMail SDK - explore correct API
"""

from agentmail import AgentMail
import agentmail
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

print("=" * 60)
print("Testing AgentMail SDK - Exploring API")
print("=" * 60)
print()

# Initialize client
client = AgentMail(api_key=API_KEY)

print(f"SDK Version: {agentmail.__version__}")
print(f"Client type: {type(client)}")
print(f"Client attributes: {[attr for attr in dir(client) if not attr.startswith('_')]}")
print()

# List inboxes
print("Listing inboxes...")
try:
    response = client.inboxes.list()
    print(f"Response type: {type(response)}")
    print(f"Response attributes: {[attr for attr in dir(response) if not attr.startswith('_')]}")
    
    # Try to access inboxes
    if hasattr(response, 'inboxes'):
        inboxes = response.inboxes
        print(f"✅ Found {len(inboxes)} inbox(es)")
        for inbox in inboxes:
            print(f"   - {inbox.inbox_id}")
            print(f"     Attributes: {[attr for attr in dir(inbox) if not attr.startswith('_')]}")
    elif hasattr(response, 'data'):
        print(f"Response data: {response.data}")
    else:
        print(f"Response: {response}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print()

# Get specific inbox
print(f"Getting inbox {INBOX}...")
try:
    inbox_response = client.inboxes.get(inbox_id=INBOX)
    print(f"Response type: {type(inbox_response)}")
    print(f"Response attributes: {[attr for attr in dir(inbox_response) if not attr.startswith('_')]}")
    
    inbox = inbox_response.inbox if hasattr(inbox_response, 'inbox') else inbox_response
    print(f"Inbox type: {type(inbox)}")
    print(f"Inbox attributes: {[attr for attr in dir(inbox) if not attr.startswith('_')]}")
    
    # Check for email methods
    print(f"\nExploring inbox object...")
    for attr in dir(inbox):
        if not attr.startswith('_'):
            print(f"   - {attr}")
    
    # Try sending email
    print(f"\nTrying to send email...")
    try:
        # Method 1 - direct send
        if hasattr(inbox, 'emails'):
            print(f"   Found emails attr: {inbox.emails}")
        if hasattr(inbox, 'send_email'):
            print(f"   Found send_email method")
        if hasattr(inbox, 'send'):
            print(f"   Found send method")
            
        # Method 2 - client.send_email
        if hasattr(client, 'send_email'):
            print(f"   Found client.send_email method")
            
        # Method 3 - client.emails.send
        if hasattr(client, 'emails'):
            print(f"   Found client.emails: {client.emails}")
            
    except Exception as e:
        print(f"   Error: {e}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
