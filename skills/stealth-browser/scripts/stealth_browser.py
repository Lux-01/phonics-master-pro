#!/usr/bin/env python3
"""
Stealth Browser - Anti-detection web automation
Wraps Playwright with stealth patches and fingerprint randomization
"""

import json
import random
import os
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from playwright.async_api import async_playwright, Page, Browser, BrowserContext
    from playwright_stealth import stealth_async
    from fake_useragent import UserAgent
except ImportError:
    print("Install: pip install playwright playwright-stealth fake-useragent")
    print("Then: playwright install chromium")
    raise


# Realistic viewport sizes
VIEWPORTS = [
    {"width": 1920, "height": 1080},  # Full HD
    {"width": 1366, "height": 768},   # Laptop
    {"width": 1440, "height": 900},   # MacBook
    {"width": 1536, "height": 864},   # Windows laptop
    {"width": 1280, "height": 720},   # Small laptop
]

# Timezone mappings
TIMEZONES = [
    "America/New_York",
    "America/Chicago",
    "America/Los_Angeles",
    "Europe/London",
    "Europe/Paris",
    "Europe/Berlin",
    "Asia/Tokyo",
    "Asia/Shanghai",
    "Australia/Sydney",
]


class StealthBrowser:
    """
    Stealth browser with anti-detection features.
    """
    
    def __init__(
        self,
        headless: bool = True,
        proxy: Optional[str] = None,
        user_agent: Optional[str] = None,
        viewport: Optional[Dict[str, int]] = None,
        locale: str = "en-US",
        timezone: Optional[str] = None,
        session_file: Optional[str] = None,
        stealth_level: str = "high",
        user_data_dir: Optional[str] = None
    ):
        self.headless = headless
        self.proxy = proxy
        self.locale = locale
        self.stealth_level = stealth_level
        self.session_file = session_file
        self.user_data_dir = user_data_dir
        
        # Generate or use provided fingerprints
        self.ua = UserAgent()
        self.user_agent = user_agent or self.ua.random
        self.viewport = viewport or random.choice(VIEWPORTS)
        self.timezone = timezone or random.choice(TIMEZONES)
        
        # Internal state
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
    
    async def _init(self):
        """Initialize browser with stealth settings."""
        self._playwright = await async_playwright().start()
        
        # Browser launch args for stealth
        args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-web-security",
            "--disable-features=IsolateOrigins,site-per-process",
            "--disable-site-isolation-trials",
        ]
        
        if self.stealth_level == "high":
            args.extend([
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
            ])
        
        # Proxy configuration
        proxy_config = None
        if self.proxy:
            proxy_config = {"server": self.proxy}
        
        # Launch browser
        browser_type = self._playwright.chromium
        self._browser = await browser_type.launch(
            headless=self.headless,
            args=args,
            proxy=proxy_config
        )
        
        # Context with fingerprint
        context_options = {
            "viewport": self.viewport,
            "user_agent": self.user_agent,
            "locale": self.locale,
            "timezone_id": self.timezone,
            "permissions": ["notifications"],
            "color_scheme": "light",
        }
        
        # Load session if exists
        if self.session_file and os.path.exists(self.session_file):
            with open(self.session_file, "r") as f:
                storage_state = json.load(f)
                context_options["storage_state"] = storage_state
        
        self._context = await self._browser.new_context(**context_options)
        
        # Apply stealth patches
        await self._apply_stealth_scripts()
    
    async def _apply_stealth_scripts(self):
        """Inject stealth scripts to avoid detection."""
        
        # Override navigator.webdriver
        await self._context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        # Hide automation flags
        await self._context.add_init_script("""
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
        
        # High stealth: more advanced evasion
        if self.stealth_level == "high":
            await self._context.add_init_script("""
                // Override canvas fingerprint
                const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
                HTMLCanvasElement.prototype.toDataURL = function(type) {
                    if (this.width > 16 && this.height > 16) {
                        // Add subtle noise to canvas
                        const ctx = this.getContext('2d');
                        const imageData = ctx.getImageData(0, 0, this.width, this.height);
                        const data = imageData.data;
                        for (let i = 0; i < data.length; i += 4) {
                            if (Math.random() < 0.001) {
                                data[i] = data[i] + (Math.random() > 0.5 ? 1 : -1);
                            }
                        }
                        ctx.putImageData(imageData, 0, 0);
                    }
                    return originalToDataURL.apply(this, arguments);
                };
            """)
    
    def new_page(self) -> Page:
        """Create new page with stealth applied."""
        if not self._context:
            asyncio.get_event_loop().run_until_complete(self._init())
        
        # Create page
        self._page = asyncio.get_event_loop().run_until_complete(
            self._context.new_page()
        )
        
        # Apply playwright-stealth
        asyncio.get_event_loop().run_until_complete(
            stealth_async(self._page)
        )
        
        return self._page
    
    def save_session(self, filepath: Optional[str] = None):
        """Save browser session (cookies, localStorage)."""
        if not self._context:
            return
        
        path = filepath or self.session_file
        if not path:
            return
        
        storage_state = asyncio.get_event_loop().run_until_complete(
            self._context.storage_state()
        )
        
        with open(path, "w") as f:
            json.dump(storage_state, f, indent=2)
    
    def close(self):
        """Close browser and save session."""
        if self.session_file:
            self.save_session()
        
        if self._context:
            asyncio.get_event_loop().run_until_complete(self._context.close())
        if self._browser:
            asyncio.get_event_loop().run_until_complete(self._browser.close())
        if self._playwright:
            asyncio.get_event_loop().run_until_complete(self._playwright.stop())
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False


async def human_like_typing(page: Page, selector: str, text: str, min_delay: float = 0.05, max_delay: float = 0.2):
    """
    Type text with human-like variable delays.
    
    Args:
        page: Playwright page
        selector: Input field selector
        text: Text to type
        min_delay: Minimum delay between keystrokes
        max_delay: Maximum delay between keystrokes
    """
    await page.click(selector)
    await page.wait_for_timeout(random.randint(100, 300))
    
    for char in text:
        await page.keyboard.press(char)
        delay = random.uniform(min_delay, max_delay) * 1000
        await page.wait_for_timeout(int(delay))


async def random_delay(min_seconds: float = 1.0, max_seconds: float = 3.0):
    """Random delay between actions."""
    delay = random.uniform(min_seconds, max_seconds) * 1000
    await asyncio.sleep(delay / 1000)


async def human_like_scroll(page: Page, direction: str = "down", amount: int = 300):
    """Scroll with human-like behavior."""
    steps = random.randint(3, 8)
    step_size = amount // steps
    
    for _ in range(steps):
        if direction == "down":
            await page.mouse.wheel(0, step_size)
        else:
            await page.mouse.wheel(0, -step_size)
        await asyncio.sleep(random.uniform(0.1, 0.3))


# Convenience functions for sync usage
def create_stealth_browser(**kwargs) -> StealthBrowser:
    """Create and initialize stealth browser."""
    return StealthBrowser(**kwargs)
