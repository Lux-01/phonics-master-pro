#!/usr/bin/env python3
"""
🌐 BROWSER AUTOMATION SELLER
Uses Playwright to automate Jupiter swap UI when APIs fail

⚠️ SECURITY WARNING:
- Browser must be open with wallet connected
- Wallet must be pre-approved for transactions
- Use with caution - browser automation can be brittle

Requirements:
- pip install playwright
- playwright install
- Browser open with wallet extension connected
"""

import asyncio
import time
from typing import Dict, Optional
from datetime import datetime

# Try to import Playwright
try:
    from playwright.async_api import async_playwright, Page, Browser
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️ Playwright not installed. Install with:")
    print("   pip install playwright")
    print("   playwright install")


class BrowserAutomationSeller:
    """Automate Jupiter swap via browser control"""
    
    def __init__(self, wallet_address: str):
        self.wallet = wallet_address
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    async def init_browser(self) -> bool:
        """Initialize browser connection"""
        if not PLAYWRIGHT_AVAILABLE:
            return False
        
        try:
            print("   Launching browser...")
            self.playwright = await async_playwright().start()
            
            # Try to connect to existing Chrome/Edge with remote debugging
            # Or launch new browser
            try:
                self.browser = await self.playwright.chromium.connect_over_cdp(
                    "http://localhost:9222"
                )
                print("   ✅ Connected to existing browser")
            except:
                # Launch new browser
                self.browser = await self.playwright.chromium.launch(
                    headless=False,  # Must be visible for wallet extension
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-web-security',
                        '--disable-features=IsolateOrigins,site-per-process',
                    ]
                )
                print("   ✅ Launched new browser")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Browser init failed: {e}")
            return False
    
    async def navigate_to_jupiter(self, token_address: str) -> bool:
        """Navigate to Jupiter swap page"""
        try:
            # Create new page
            self.page = await self.browser.new_page()
            
            # Construct Jupiter swap URL
            jupiter_url = f"https://jup.ag/swap/{token_address}-SOL"
            
            print(f"   Navigating to Jupiter...")
            await self.page.goto(jupiter_url, wait_until="networkidle")
            
            # Wait for page to load
            await asyncio.sleep(3)
            
            print(f"   ✅ Page loaded: {jupiter_url}")
            return True
            
        except Exception as e:
            print(f"   ❌ Navigation failed: {e}")
            return False
    
    async def check_wallet_connected(self) -> bool:
        """Check if wallet is connected"""
        try:
            # Look for wallet button
            wallet_button = await self.page.query_selector('button:has-text("Connect")')
            if wallet_button:
                print("   ⚠️ Wallet not connected - please connect manually")
                return False
            
            # Check for wallet address display
            wallet_display = await self.page.query_selector('text=/[A-HJ-NP-Za-km-z1-9]{32,44}/')
            if wallet_display:
                print("   ✅ Wallet connected")
                return True
            
            return False
            
        except Exception as e:
            print(f"   ❌ Wallet check failed: {e}")
            return False
    
    async def enter_amount(self, amount: float) -> bool:
        """Enter sell amount"""
        try:
            print(f"   Entering amount: {amount} tokens...")
            
            # Find input field (usually first input on page)
            input_field = await self.page.query_selector('input[type="text"], input[type="number"]')
            
            if not input_field:
                print("   ❌ Could not find input field")
                return False
            
            # Clear and enter amount
            await input_field.click()
            await input_field.fill("")
            await input_field.fill(str(amount))
            
            # Wait for quote
            await asyncio.sleep(2)
            
            print("   ✅ Amount entered")
            return True
            
        except Exception as e:
            print(f"   ❌ Amount entry failed: {e}")
            return False
    
    async def click_swap_button(self) -> bool:
        """Click the swap button"""
        try:
            print("   Looking for swap button...")
            
            # Look for swap button (various selectors)
            selectors = [
                'button:has-text("Swap")',
                'button:has-text("Sell")',
                '[data-testid="swap-button"]',
                'button[class*="swap"]',
            ]
            
            for selector in selectors:
                button = await self.page.query_selector(selector)
                if button:
                    print(f"   Clicking swap button...")
                    await button.click()
                    await asyncio.sleep(1)
                    print("   ✅ Swap button clicked")
                    return True
            
            print("   ❌ Could not find swap button")
            return False
            
        except Exception as e:
            print(f"   ❌ Swap click failed: {e}")
            return False
    
    async def confirm_transaction(self) -> bool:
        """Wait for and confirm transaction in wallet popup"""
        try:
            print("   Waiting for wallet popup...")
            
            # Wait for wallet popup (various wallet extensions)
            await asyncio.sleep(3)
            
            # Look for approve/confirm button in popup
            # This is wallet-specific and may need adjustment
            print("   ⚠️ Please confirm transaction in wallet popup")
            print("   (Auto-confirmation requires wallet pre-approval)")
            
            # Wait for transaction to complete
            print("   Waiting for transaction...")
            await asyncio.sleep(10)
            
            # Check for success message
            success = await self.page.query_selector('text=/success|completed|done/i')
            if success:
                print("   ✅ Transaction confirmed!")
                return True
            
            return False
            
        except Exception as e:
            print(f"   ❌ Confirmation failed: {e}")
            return False
    
    async def execute_browser_sell(self, token_address: str, amount_tokens: float,
                                    token_symbol: str = "UNKNOWN") -> Dict:
        """
        Execute sell via browser automation
        """
        print(f"\n{'='*60}")
        print("🌐 BROWSER AUTOMATION SELL")
        print(f"{'='*60}")
        print(f"Token: {token_symbol}")
        print(f"Amount: {amount_tokens:.6f} tokens")
        print(f"Wallet: {self.wallet}")
        
        if not PLAYWRIGHT_AVAILABLE:
            return {
                "status": "failed",
                "error": "Playwright not installed"
            }
        
        # Step 1: Initialize browser
        if not await self.init_browser():
            return {
                "status": "failed",
                "error": "Could not initialize browser"
            }
        
        try:
            # Step 2: Navigate to Jupiter
            if not await self.navigate_to_jupiter(token_address):
                return {
                    "status": "failed",
                    "error": "Could not navigate to Jupiter"
                }
            
            # Step 3: Check wallet
            if not await self.check_wallet_connected():
                return {
                    "status": "manual_required",
                    "message": "Please connect wallet and try again",
                    "manual_url": f"https://jup.ag/swap/{token_address}-SOL"
                }
            
            # Step 4: Enter amount
            if not await self.enter_amount(amount_tokens):
                return {
                    "status": "failed",
                    "error": "Could not enter amount"
                }
            
            # Step 5: Click swap
            if not await self.click_swap_button():
                return {
                    "status": "failed",
                    "error": "Could not click swap"
                }
            
            # Step 6: Confirm
            if not await self.confirm_transaction():
                return {
                    "status": "manual_required",
                    "message": "Please confirm in wallet",
                    "manual_url": f"https://jup.ag/swap/{token_address}-SOL"
                }
            
            # Success!
            return {
                "status": "executed",
                "method": "browser_automation",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"\n❌ Browser automation failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "failed",
                "error": str(e)
            }
        
        finally:
            # Cleanup
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()


# Synchronous wrapper for convenience
def execute_browser_sell_sync(wallet: str, token_address: str, amount_tokens: float,
                               token_symbol: str = "UNKNOWN") -> Dict:
    """Execute browser sell (sync wrapper)"""
    seller = BrowserAutomationSeller(wallet)
    return asyncio.run(seller.execute_browser_sell(token_address, amount_tokens, token_symbol))


if __name__ == "__main__":
    print("Browser Automation Seller Test")
    print("="*60)
    print("⚠️ This requires:")
    print("   - Playwright installed: pip install playwright")
    print("   - Browser binaries: playwright install")
    print("   - Browser open with wallet extension")
    print("="*60)
    
    wallet = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
    token = "32CdQdBUxbCsLy5AUHWmyidfwhgGUr9N573NBUrDpump"
    
    result = execute_browser_sell_sync(wallet, token, 35.29, "TEST")
    
    print(f"\nResult: {result}")
