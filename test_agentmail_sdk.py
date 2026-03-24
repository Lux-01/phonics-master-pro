#!/usr/bin/env python3
"""
Test AgentMail SDK connection and send email
"""

from agentmail import AgentMail

API_KEY = "am_us_55b6203ca856b8c298adae29bfeb4365b6d84cc90aaf0fcc86b1abaeb498ceb2"
INBOX = "vivaciousguitar330@agentmail.to"

print("=" * 60)
print("Testing AgentMail SDK Connection")
print("=" * 60)
print()

# Initialize client
client = AgentMail(api_key=API_KEY)

print(f"Connecting with API key...")
print(f"Inbox: {INBOX}")
print()

# List inboxes
print("Listing inboxes...")
try:
    inboxes = client.inboxes.list()
    print(f"✅ Success! Found {len(inboxes)} inbox(es)")
    for inbox in inboxes:
        print(f"   - {inbox.inbox_id} (ID: {inbox.inbox_id})")
except Exception as e:
    print(f"❌ Error listing inboxes: {e}")
    inboxes = []

print()

# Get specific inbox
print(f"Getting inbox {INBOX}...")
try:
    inbox = client.inboxes.get(inbox_id=INBOX)
    print(f"✅ Inbox found!")
    print(f"   Display Name: {inbox.display_name}")
    print(f"   Created: {inbox.created_at}")
except Exception as e:
    print(f"❌ Error getting inbox: {e}")
    inbox = None

print()

# Send test email
if inbox:
    print("Sending test email...")
    print("-" * 60)
    try:
        email = inbox.emails.send(
            to=["skux@example.com"],
            subject="🧪 Test from LuxTrader v3.0",
            body="""This is a test email from LuxTrader v3.0!

✅ AgentMail SDK connection is working!
✅ API Key is valid
✅ Inbox is configured

This email was sent automatically.

- LuxTheClaw 🦞
"""
        )
        print(f"✅ Email sent successfully!")
        print(f"   To: {email.to}")
        print(f"   Subject: {email.subject}")
        print(f"   ID: {email.id if hasattr(email, 'id') else 'N/A'}")
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        print(f"   Type: {type(e).__name__}")
        
print()
print("=" * 60)
print()

# Fetch emails
print("Fetching emails...")
try:
    emails = inbox.emails.list(limit=5)
    print(f"✅ Found {len(emails)} email(s) in inbox")
    for email in emails[:3]:
        print(f"   - From: {email.from_}")
        print(f"     Subject: {email.subject}")
        print(f"     Date: {email.created_at}")
        print()
except Exception as e:
    print(f"❌ Error fetching emails: {e}")

print("=" * 60)
print("AgentMail SDK test complete!")
print("=" * 60)
