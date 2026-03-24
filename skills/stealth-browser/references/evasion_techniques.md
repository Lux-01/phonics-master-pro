# Evasion Techniques Reference

Advanced anti-detection strategies for browser automation.

## Detection Methods Sites Use

### 1. JavaScript Fingerprinting

**Navigator Properties**
- `navigator.webdriver` - Should be undefined (not true)
- `navigator.plugins` - Should return realistic plugin array
- `navigator.languages` - Should return array, not empty
- `navigator.hardwareConcurrency` - 2, 4, 8, or 16 (not 1 or odd numbers)
- `navigator.deviceMemory` - 4, 8, 16, or 32 GB (not 0.5 or 0.25)

**Window Properties**
- `window.outerWidth/Height` - Should match viewport calculations
- `window.devicePixelRatio` - Should match screen scale
- `window.chrome` - Should exist for Chrome UAs
- `window.Buffer` - Should not exist (Node.js leak)

**WebGL Fingerprint**
- Vendor/renderer strings
- Supported extensions
- Canvas hash consistency

### 2. Behavioral Analysis

**Mouse Movements**
- Bots move in straight lines
- Humans have curved, variable paths
- Bots: instant acceleration
- Humans: gradual acceleration

**Key Presses**
- Bots: uniform timing (50ms each)
- Humans: variable timing (80-200ms, occasional pauses)

**Scroll Behavior**
- Bots: instant jumps
- Humans: momentum scrolling with deceleration

### 3. Request Pattern Analysis

**Timing**
- Too fast = bot
- Too regular = bot
- Immediate form submission after page load = bot

**Consistency**
- Same fingerprint across sessions = bot
- Inconsistent fingerprints (UA ≠ platform) = bot

## Evasion Strategies

### Fingerprint Consistency

All properties must be consistent:
- User-Agent platform matches `navigator.platform`
- Screen resolution matches viewport calculations
- WebGL vendor matches OS (Apple GPU only on Mac)
- Chrome version in UA matches `window.chrome` features

### Human Behavior Simulation

```python
# Mouse: curved paths with bezier curves
# Instead of: await page.mouse.move(x, y)

async def human_mouse_move(page, target_x, target_y):
    current = await page.evaluate("() => ({x: window.scrollX, y: window.scrollY})")
    # Use bezier curve for path
    points = generate_bezier_path(current, target_x, target_y, control_points=3)
    for point in points:
        await page.mouse.move(point.x, point.y)
        await asyncio.sleep(random.uniform(0.01, 0.05))

# Typing: variable delays with occasional mistakes
async def human_type(page, selector, text):
    for char in text:
        if random.random() < 0.02:  # 2% typo rate
            wrong_char = random.choice("qwertyuiopasdfghjklzxcvbnm")
            await page.keyboard.press(wrong_char)
            await asyncio.sleep(random.uniform(0.1, 0.3))
            await page.keyboard.press("Backspace")
        await page.keyboard.press(char)
        await asyncio.sleep(random.uniform(0.05, 0.2))
```

### Session Warming

Before sensitive actions:
1. Visit homepage first
2. Scroll naturally
3. Click non-sensitive elements
4. Wait 5-10 seconds
5. Then perform target action

### IP Quality

**Proxy Types (best to worst)**
1. Residential rotating (real home IPs)
2. Mobile rotating (4G/5G IPs)
3. ISP proxies (datacenter but ISP-assigned)
4. Datacenter proxies (easiest to detect)

**IP Rotation**
- Session-based: New IP per session
- Request-based: New IP per request (risky, triggers rate limits)
- Smart rotation: New IP after CAPTCHA or block

## Common Detection Services

### Cloudflare
- Heavy JavaScript challenges
- TLS fingerprinting
- Turnstile CAPTCHA
- **Strategy**: Use stealth browser with real browser TLS, session warming

### DataDome
- Behavioral analysis
- Device fingerprinting
- **Strategy**: Consistent fingerprints, human-like delays, quality proxies

### PerimeterX/Human
- JavaScript challenge
- Behavioral biometrics
- **Strategy**: Same as above, more aggressive session warming

### reCAPTCHA v3
- Invisible scoring
- Analyzes entire session
- **Strategy**: Build site reputation gradually, avoid sudden actions

## Testing Detection

Test your stealth at:
- https://bot.sannysoft.com/ - Comprehensive fingerprint check
- https://browserleaks.com/ - Various leak tests
- https://whoer.net/ - IP and browser check

All tests should show "green" / real browser results.
