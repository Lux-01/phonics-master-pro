#!/usr/bin/env python3
"""
DexScreener Token Scraper
Uses stealth browser to extract top tokens
"""
import asyncio
import json
import sys
sys.path.insert(0, '/home/skux/.openclaw/workspace/skills/stealth-browser/scripts')

try:
    from stealth_browser import StealthBrowser
    from playwright.async_api import async_playwright
except ImportError:
    print("❌ Playwright not installed")
    print("Install: pip install playwright playwright-stealth")
    print("Then: playwright install chromium")
    sys.exit(1)

async def scrape_dexscreener():
    """
    Scrape DexScreener for top tokens
    """
    print("=" * 70)
    print("🚀 DexScreener Token Scraper")
    print("=" * 70)
    print()
    print("Initializing stealth browser...")
    
    browser = StealthBrowser(headless=True)
    tokens = []
    
    try:
        page = browser.new_page()
        
        # Navigate to DexScreener Solana
        print("📍 Navigating to dexscreener.com/solana...")
        await page.goto("https://dexscreener.com/solana", wait_until="networkidle")
        
        # Wait for content to load
        print("⏳ Waiting for token data to load...")
        await asyncio.sleep(3)
        
        # Extract token data
        print("🔍 Extracting token data...")
        
        # Try multiple selectors for robustness
        token_cards = await page.query_selector_all("[data-testid='token-card'], .ds-dex-table-row, a[href*='solana']")
        
        print(f"Found {len(token_cards)} potential token elements")
        
        # Extract page content for analysis
        content = await page.content()
        
        # Look for token symbols and addresses in page
        import re
        
        # Find token addresses (base58 Solana format)
        address_pattern = r'[1-9A-HJ-NP-Za-km-z]{32,44}'
        addresses = re.findall(address_pattern, content)
        unique_addresses = list(set(addresses))[:20]
        
        # Look for price data
        price_pattern = r'\$[\d,]+\.?\d*[KM]?'
        prices = re.findall(price_pattern, content)
        
        # Look for volume
        volume_pattern = r'[\d,]+\.?\d*[KM]?\s*\$?[\d,]*'
        
        print()
        print("=" * 70)
        print("📊 SCRAPING RESULTS")
        print("=" * 70)
        print()
        
        if unique_addresses:
            print(f"✅ Found {len(unique_addresses)} token addresses:")
            print()
            for i, addr in enumerate(unique_addresses[:10], 1):
                print(f"  {i}. {addr}")
        
        if prices:
            print()
            print(f"💰 Sample price data found: {prices[:5]}")
        
        # Get page title and metadata
        title = await page.title()
        print()
        print(f"📄 Page Title: {title}")
        
        # Screenshot for verification
        screenshot_path = "/home/skux/.openclaw/workspace/dexscreener_screenshot.png"
        await page.screenshot(path=screenshot_path)
        print(f"📸 Screenshot saved: {screenshot_path}")
        
        # Try to extract from localStorage or window data
        print()
        print("🔍 Checking for window.__INITIAL_STATE__ or API data...")
        
        # Some sites expose data to window object
        window_data = await page.evaluate("() => { return typeof window !== 'undefined' ? Object.keys(window).filter(k => k.includes('token') || k.includes('data')).slice(0,10) : [] }")
        if window_data:
            print(f"Window data keys: {window_data}")
        
        return {
            "status": "success",
            "addresses_found": len(unique_addresses),
            "sample_addresses": unique_addresses[:10],
            "prices_sample": prices[:5] if prices else [],
            "page_title": title,
            "screenshot": screenshot_path
        }
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "error": str(e)
        }
    finally:
        await browser.close()
        print()
        print("=" * 70)
        print("✅ Browser automation complete")
        print("=" * 70)

if __name__ == "__main__":
    result = asyncio.run(scrape_dexscreener())
    
    print()
    print("\n📋 Full Result:")
    print(json.dumps(result, indent=2))
