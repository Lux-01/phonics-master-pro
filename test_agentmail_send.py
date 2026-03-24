#!/usr/bin/env python3
"""
Test AgentMail send endpoints - systematic approach
"""

import requests

API_KEY = "am_us_55b6203ca856b8c298adae29bfeb4365b6d84cc90aaf0fcc86b1abaeb498ceb2"
INBOX = "vivaciousguitar330@agentmail.to"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

email_data = {
    "to": ["skux@example.com"],
    "subject": "Test from LuxTrader v3.0",
    "body": "This is a test email from LuxTrader! ✨\n\nIf you receive this, the connection is working perfectly."
}

# Test different send endpoints
send_endpoints = [
    # Variations with inbox in path
    f"https://api.agentmail.to/inboxes/{INBOX}/send",
    f"https://api.agentmail.to/inboxes/{INBOX}/emails/send",
    f"https://api.agentmail.to/inboxes/{INBOX}/messages",
    
    # Variations with inbox_id in body
    "https://api.agentmail.to/emails",
    "https://api.agentmail.to/emails/send",
    "https://api.agentmail.to/send",
    "https://api.agentmail.to/messages",
    
    # v1 paths
    "https://api.agentmail.to/v1/emails",
    "https://api.agentmail.to/v1/send",
    f"https://api.agentmail.to/v1/inboxes/{INBOX}/emails",
    f"https://api.agentmail.to/v1/inboxes/{INBOX}/send",
]

print("Testing AgentMail SEND endpoints...")
print(f"Inbox: {INBOX}")
print("=" * 70)

for url in send_endpoints:
    try:
        # First try POST
        response = requests.post(url, headers=headers, json=email_data, timeout=10)
        print(f"\nPOST {url}")
        print(f"Status: {response.status_code}")
        if response.status_code in [200, 201, 202]:
            print(f"Response: {response.text[:200]}")
            print("✅ SUCCESS!")
            break
        else:
            print(f"Response: {response.text[:100]}")
    except Exception as e:
        print(f"\nPOST {url}")
        print(f"Error: {e}")

print("\n" + "=" * 70)
