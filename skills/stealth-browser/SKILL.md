---
name: stealth-browser
description: Stealth web automation with anti-detection. Use when needing to scrape data, automate browser tasks, or bypass basic bot detection. Provides fingerprint randomization, proxy rotation, human-like interactions, and CAPTCHA handling strategies. Works with Playwright for browser control and includes patterns for avoiding detection on sites with basic to moderate anti-bot measures.
---

# Stealth Browser

Anti-detection browser automation using Playwright with stealth patches.

## Quick Start

### Basic Stealth Session

```python
from scripts.stealth_browser import StealthBrowser

browser = StealthBrowser()
page = browser.new_page()

page.goto("https://example.com")
page.screenshot(path="result.png")

browser.close()
```

### With Proxy

```python
browser = StealthBrowser(
    proxy="http://user:pass@proxy:8080",
    headless=False  # Visible browser (more stealthy)
)
```

### Human-Like Navigation

```python
from scripts.stealth_browser import human_like_typing, random_delay

# Type like human (with random delays)
await human_like_typing(page, "#search", "query")

# Random delay between actions
await random_delay(1, 3)  # 1-3 seconds
```

## Anti-Detection Features

### Automatic Fingerprint Randomization

Each browser instance gets unique:
- User-Agent (from real browser list)
- Screen resolution
- Timezone
- WebGL/Canvas fingerprints
- Hardware concurrency
- Device memory

### Human Behavior Patterns

- Random mouse movements
- Variable typing speeds
- Natural scroll behavior
- Random delays between actions

## Advanced Usage

### Session Persistence

```python
# Save session (cookies, localStorage)
browser.save_session("session.json")

# Load existing session
browser = StealthBrowser(session_file="session.json")
```

### Proxy Rotation

```python
from scripts.proxy_rotator import ProxyRotator

proxies = [
    "http://proxy1:8080",
    "http://user:pass@proxy2:8080"
]
rotator = ProxyRotator(proxies)

browser = StealthBrowser(proxy=rotator.get_proxy())
```

### CAPTCHA Handling

When encountering CAPTCHAs, combine with captcha-solver skill:

```python
# 1. Detect CAPTCHA
if page.is_visible(".captcha-image"):
    # 2. Screenshot CAPTCHA
    page.locator(".captcha-image").screenshot(path="captcha.png")
    
    # 3. Solve (requires captcha-solver skill)
    from scripts import solve_image_captcha
    result = solve_image_captcha("captcha.png")
    
    # 4. Enter solution
    page.fill("#captcha-input", result["text"])
```

### Handling reCAPTCHA/hCaptcha

These enterprise CAPTCHAs require different strategies:

1. **Avoid triggering**: Use human-like delays, real mouse movements
2. **Session warming**: Visit site naturally first
3. **Quality proxies**: Residential/mobile IPs work better
4. **Headful mode**: Visible browser is harder to detect

```python
# Maximum stealth config
browser = StealthBrowser(
    headless=False,
    proxy="residential_proxy",
    user_data_dir="/tmp/browser_profile"
)

# Warm up session
page.goto("https://site.com")
page.wait_for_timeout(5000)
page.mouse.move(100, 100)  # Real mouse movement
```

## Configuration Options

```python
browser = StealthBrowser(
    headless=True,              # Headless mode (faster, less stealth)
    proxy=None,                 # HTTP/SOCKS proxy
    user_agent=None,            # Custom UA (or auto-generated)
    viewport=None,              # Custom viewport (or auto-generated)
    locale="en-US",             # Browser locale
    timezone="America/New_York", # Browser timezone
    session_file=None,          # Load/save session
    stealth_level="high"        # "low", "medium", "high"
)
```

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `stealth_browser.py` | Main browser class with anti-detection |
| `proxy_rotator.py` | Proxy rotation and health checking |
| `fingerprint.py` | Fingerprint generation utilities |
| `human_behavior.py` | Human-like interactions |

## Dependencies

```bash
pip install playwright playwright-stealth fake-useragent
playwright install chromium
```

## Limitations

- **Advanced bot detection**: Sites using Cloudflare, DataDome, or PerimeterX may still detect automation
- **Fingerprint consistency**: Some advanced checks track consistency across sessions
- **Rate limiting**: Even stealth browsers hit limits with excessive requests

## References

See `references/evasion_techniques.md` for detailed anti-detection strategies.
