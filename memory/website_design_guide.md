# Website Design Guide
*Compiled from multiple authoritative sources*

---

## 1. Color Schemes & Design

### Color Theory Basics

#### The Color Wheel
- **Primary**: Red, Blue, Yellow
- **Secondary**: Green, Orange, Purple (mix of primaries)
- **Tertiary**: Red-orange, yellow-green, blue-purple, etc.

#### Color Harmonies
| Scheme | Description | Use Case |
|--------|-------------|----------|
| **Monochromatic** | Single hue, varying saturation/lightness | Clean, professional, minimal |
| **Analogous** | Adjacent colors on wheel (e.g., blue + blue-green) | Calm, harmonious, nature-like |
| **Complementary** | Opposite colors (e.g., blue + orange) | High contrast, call-to-action |
| **Split-Complementary** | One color + two adjacent to its complement | Contrast without harshness |
| **Triadic** | Three evenly spaced colors (e.g., red, yellow, blue) | Vibrant, balanced, playful |
| **Tetradic** | Four colors in rectangle on wheel | Rich, complex, diverse |

### Modern Web Color Schemes

#### Dark Mode Design
```css
/* CSS custom properties for theming */
:root {
  --bg-primary: #0d1117;
  --bg-secondary: #161b22;
  --text-primary: #c9d1d9;
  --text-secondary: #8b949e;
  --accent: #58a6ff;
  --border: #30363d;
}

/* Light theme */
[data-theme="light"] {
  --bg-primary: #ffffff;
  --bg-secondary: #f6f8fa;
  --text-primary: #24292f;
  --text-secondary: #57606a;
  --accent: #0969da;
}
```

**Dark Mode Best Practices:**
- Use color-scheme CSS property for UA stylesheet integration
- Don't use pure black (#000000) — causes eye strain
- Reduce saturation in dark themes (colors appear more vibrant on dark)
- Maintain contrast ratio of at least 4.5:1 for text

#### Popular Professional Palettes
1. **Corporate Blue**: #0066CC, #ffffff, #333333, #66b3ff
2. **Tech Startup**: #6366f1, #8b5cf6, #ec4899, #f3f4f6
3. **Nature/Organic**: #059669, #10b981, #f59e0b, #f3f4f6
4. **High Contrast**: #000000, #ffffff, #ff0000 (accessibility-focused)

### Accessibility (A11y) Requirements

#### Contrast Ratios
| Element | Minimum | Enhanced |
|---------|---------|----------|
| Normal text | 4.5:1 | 7:1 |
| Large text (18pt+) | 3:1 | 4.5:1 |
| UI components | 3:1 | 4.5:1 |

#### Tools for Color Validation
- WebAIM Contrast Checker
- Stark plugin for Figma/Sketch
- Chrome DevTools Lighthouse audit

---

## 2. Web Security Fundamentals

### Core Principles

#### Defense in Depth
Multiple layers of security — if one fails, others protect:
1. **Network layer**: HTTPS, firewalls
2. **Application layer**: Input validation, sanitization
3. **Data layer**: Encryption, access controls
4. **Session layer**: Secure cookies, JWT tokens

#### OWASP Top 10 (2025)
1. **Broken Access Control** — Unauthorized data access
2. **Cryptographic Failures** — Weak or missing encryption
3. **Injection** — SQL, NoSQL, OS command injection
4. **Insecure Design** — Fundamental design flaws
5. **Security Misconfiguration** — Default configs, verbose errors
6. **Vulnerable Components** — Outdated dependencies
7. **Authentication Failures** — Weak passwords, session hijacking
8. **Data Integrity Failures** — Insecure deserialization
9. **Logging Failures** — Insufficient monitoring
10. **Server-Side Request Forgery** — SSRF attacks

### Same-Origin Policy (SOP)

**What it does:** Restricts scripts from one origin accessing data from another

**Origin = Protocol + Domain + Port**
- `https://example.com:443` can access `https://example.com/images/`
- `https://example.com` CANNOT access `https://api.other.com`

**Relaxing SOP with CORS:**
```http
Access-Control-Allow-Origin: https://trusted-site.com
Access-Control-Allow-Methods: GET, POST
Access-Control-Allow-Headers: Content-Type, Authorization
```

### Content Security Policy (CSP)

The ultimate XSS protection — whitelist what can execute:

```http
Content-Security-Policy: 
  default-src 'self';
  script-src 'self' 'nonce-random123' https://trusted-cdn.com;
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https://trusted-images.com;
  connect-src 'self' https://api.example.com;
  frame-ancestors 'none';
  upgrade-insecure-requests;
```

### HTTPS Everywhere

**Always use HTTPS in production:**
- Encrypts data in transit
- Prevents MITM attacks
- Required for modern browser features (geolocation, camera, etc.)
- SEO ranking boost from Google

**HTTP Strict Transport Security (HSTS):**
```http
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

---

## 3. Bot Protection Strategies

### Types of Bad Bots

| Bot Type | Purpose | Danger Level |
|----------|---------|--------------|
| **Scraper Bots** | Steal content, pricing data | Medium |
| **Credential Stuffing** | Automated login attempts | High |
| **DDoS Bots** | Overwhelm servers | Critical |
| **Click Fraud** | Fake ad interactions | Medium |
| **SEO Spam** | Comment spam, fake backlinks | Low |
| **Inventory Hoarding** | Automated purchasing (sneaker bots) | High |

### Protection Layers

#### 1. Detection Methods
- **TLS fingerprinting** — Identify client type from handshake
- **JavaScript challenges** — Test for browser capabilities
- **Behavioral analysis** — Mouse movements, typing patterns
- **Request patterns** — Rate, timing, sequence analysis
- **Device fingerprinting** — Canvas, WebGL, fonts

#### 2. Challenge Mechanisms
| Type | User Experience | Bot Deterrence |
|------|-----------------|----------------|
| CAPTCHA | Poor | High |
| reCAPTCHA v3 | Invisible | Medium |
| Cloudflare Turnstile | Minimal | High |
| JS Challenge | Transparent | Medium |
| Proof-of-Work | Delayed | High |

#### 3. Rate Limiting
```javascript
// Express rate limiting example
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP'
});

app.use('/api/', limiter);
```

#### 4. Honeypots
```html
<!-- Hidden field bots will fill -->
<input type="text" name="website" style="display:none" tabindex="-1">
```

#### 5. Device Fingerprinting
JavaScript-based detection of headless browsers:
- Check for webdriver property
- Verify plugins exist
- Test for inconsistent window properties
- Canvas/WebGL hashing

### Modern Protection Stack

**Recommended Approach:**

1. **Edge Protection** (Cloudflare/AWS WAF)
   - DDoS mitigation
   - Bot detection
   - IP reputation filtering

2. **Application Layer**
   - Rate limiting per user/IP
   - CSRF tokens for state-changing actions
   - Input validation and sanitization

3. **Authentication Layer**
   - Multi-factor authentication (MFA)
   - Account lockout after failed attempts
   - Device verification

4. **Monitoring**
   - Failed request logging
   - Traffic pattern analysis
   - Alert on anomaly detection

---

## 4. Implementation Checklist

### Pre-Launch Security
- [ ] HTTPS enforced with HSTS
- [ ] CSP header configured
- [ ] X-Frame-Options set
- [ ] Secure cookie attributes (HttpOnly, Secure, SameSite)
- [ ] Input validation on all endpoints
- [ ] Output encoding to prevent XSS
- [ ] Database parameterized queries
- [ ] Security headers scan (securityheaders.com)

### Design System
- [ ] Color palette defined with contrast ratios
- [ ] Dark mode support implemented
- [ ] Typography scale established (1.125-1.250 ratio)
- [ ] Spacing system (8px base grid)
- [ ] Component library documented
- [ ] Responsive breakpoints defined

### Bot Protection
- [ ] WAF configured
- [ ] Rate limiting implemented
- [ ] Login form honeypot added
- [ ] Anomaly monitoring set up
- [ ] Bot challenge for suspicious traffic

---

## 5. Resources & Tools

### Design
- **Coolors.co** — Color palette generator
- **Figma** — Design system creation
- **WebAIM Contrast Checker** — A11y compliance

### Security Testing
- **OWASP ZAP** — Web application security scanner
- **Burp Suite** — Penetration testing
- **Mozilla Observatory** — Security header checker
- **VirusTotal** — URL/file reputation checking

### Bot Protection
- **Cloudflare** — Turnstile, Bot Management
- **reCAPTCHA Enterprise** — Google bot detection
- **DataDome** — Advanced bot protection
- **PerimeterX** — Behavioral detection

---

*Sources: web.dev, MDN Web Security, OWASP Top 10 2025, Cloudflare Bot Management, W3C WCAG 2.1*
*Compiled: 2026-03-10*
