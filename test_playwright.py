#!/usr/bin/env python3
"""Test Playwright Installation"""
from playwright.sync_api import sync_playwright

print("Testing Playwright...")

try:
    with sync_playwright() as p:
        print("✅ Playwright initialized")
        
        # Try to launch browser
        browser = p.chromium.launch(headless=True)
        print("✅ Chromium launched")
        
        # Create page
        page = browser.new_page()
        print("✅ Page created")
        
        # Navigate
        page.goto("https://example.com", timeout=10000)
        print("✅ Navigation successful")
        
        # Get title
        title = page.title()
        print(f"✅ Title: {title}")
        
        # Close
        browser.close()
        print("✅ Browser closed")
        
        print("\n🎉 Playwright is fully operational!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
