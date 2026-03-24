#!/usr/bin/env python3
"""
Final AgentMail connection test - various endpoints
"""

import requests

API_KEY = "am_us_80e7e271117a88cc6e9ea77b53724a3c02b03241c173d92282a9094c9e44062a"
INBOX = "vivaciousguitar330@agentmail.to"

# Different auth methods to try
auth_methods = [
    {"Authorization": f"Bearer {API_KEY}"},
    {"x-api-key": API_KEY},
    {"X-API-Key": API_KEY},
]

# Different base URLs
base_urls = [
    "https://api.agentmail.to",
    "https://api.agentmail.to/v1",
]

# Endpoints to test
endpoints = [
    "/inboxes",
    "/emails",
    f"/inboxes/{INBOX}",
    f"/inboxes/{INBOX}/emails",
]

print("Testing all combinations...")
print("=" * 60)

for base in base_urls:
    for auth in auth_methods:
        for endpoint in endpoints:
            url = f"{base}{endpoint}"
            headers = {**auth, "Content-Type": "application/json"}
            
            try:
                response = requests.get(url, headers=headers, timeout=5)
                if response.status_code != 404:
                    print(f"\nURL: {url}")
                    print(f"Auth: {list(auth.keys())[0]}")
                    print(f"Status: {response.status_code}")
                    print(f"Response: {response.text[:100]}")
            except:
                pass

print("\n" + "=" * 60)
print("Test complete. Check logs for successful connection.")
