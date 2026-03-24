#!/usr/bin/env python3
"""
Test AgentMail API connection
"""

import requests

API_KEY = "am_us_80e7e271117a88cc6e9ea77b53724a3c02b03241c173d92282a9094c9e44062a"
INBOX = "vivaciousguitar330@agentmail.to"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Try different endpoints
endpoints = [
    "https://api.agentmail.to/inboxes",
    "https://api.agentmail.to/v1/inboxes",
    f"https://api.agentmail.to/inboxes/{INBOX}",
    f"https://api.agentmail.to/inboxes/{INBOX}/emails",
    "https://api.agentmail.to/",
]

print("Testing AgentMail API connection...")
print(f"Inbox: {INBOX}")
print("-" * 60)

for url in endpoints:
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"\nURL: {url}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.text[:200]}")
            print("✅ SUCCESS!")
            break
        else:
            print(f"Response: {response.text[:100]}")
    except Exception as e:
        print(f"\nURL: {url}")
        print(f"Error: {e}")

print("\n" + "-" * 60)
print("Connection test complete")
