---
name: website-designer
description: Professional website builder with live editing, security hardening, and malware protection. Creates modern, responsive websites with automatic security scanning and deployment-ready code.
---

# Website Designer Skill

**"Professional web development in a skill."**

Build modern, secure websites with ease. Generate responsive designs, edit live, harden security, and protect against malware.

---

## Capabilities

### 🎨 Design & Create
- Generate complete HTML/CSS/JS websites
- Responsive layouts (mobile-first)
- Modern color schemes with accessibility
- Dark/light theme support
- Typography and spacing systems
- Component-based architecture

### ✏️ Live Edit
- Hot-reload development server
- Real-time preview
- Easy configuration editing
- Template customization
- Asset management (images, fonts, icons)

### 🛡️ Security & Protection
- Automatic security scanning
- CSP headers generation
- HTTPS enforcement config
- XSS protection
- Content sanitization
- Malware detection
- Vulnerability alerts

### 🚀 Deployment Ready
- Static site generation
- CDN optimization
- Minification
- Image optimization
- SEO meta tags
- Sitemap generation

---

## Quick Start

### Create a Website
```bash
# Create a new website project
lux website create --name my-site --type business

# Types available: business, portfolio, landing, blog, ecommerce
```

### Live Preview
```bash
# Start development server with hot reload
lux website serve my-site

# Opens browser at http://localhost:3000
```

### Security Scan
```bash
# Scan for vulnerabilities
lux website scan my-site

# Auto-fix issues
lux website scan --fix my-site
```

### Deploy
```bash
# Build for production
lux website build my-site

# Output in dist/ folder ready to deploy
```

---

## Website Types

### Business Site
- Hero section
- Services/Products
- About section
- Contact form
- Footer with social links

### Portfolio
- Gallery showcase
- Project details
- Skills/experience
- Testimonials
- Contact
- **Quick Portfolio Generator** - One-command portfolio creation
- **Pre-built Templates** - Modern, minimalist, creative styles
- **Portfolio Sections** - Hero, About, Services, Projects, Contact
- **Auto-deployment Ready** - Vercel/Netlify/GitHub Pages config

### Landing Page
- Single focus CTA
- Feature highlights
- Social proof
- Lead capture
- Minimal navigation

### Blog
- Article list
- Category/tags
- Author pages
- RSS feed
- Search

### E-commerce (Simple)
- Product grid
- Cart functionality
- Checkout flow
- Payment integration ready

---

## Security Features

### Automatic Hardening
| Feature | Description |
|---------|-------------|
| CSP Headers | Content Security Policy config |
| Frame Options | Clickjacking protection |
| XSS Protection | Reflected XSS mitigation |
| MIME Sniffing | Content type enforcement |
| HSTS | HTTPS enforcement |
| Referrer Policy | Privacy protection |

### Malware Protection
- File upload validation
- Image sanitization
- Script injection detection
- Suspicious pattern scanning
- Dependency vulnerability check

---

## Configuration

### Site Config (site.json)
```json
{
  "name": "My Business",
  "description": "Professional services company",
  "url": "https://mybusiness.com",
  "theme": {
    "primary": "#0066CC",
    "secondary": "#FF6B6B",
    "background": "#FFFFFF",
    "text": "#333333",
    "darkMode": true
  },
  "fonts": {
    "heading": "Inter",
    "body": "Open Sans"
  },
  "security": {
    "csp": true,
    "hsts": true,
    "xss": true,
    "scanOnBuild": true
  },
  "seo": {
    "title": "My Business | Professional Services",
    "description": "We provide top-quality professional services",
    "keywords": ["business", "services", "professional"]
  }
}
```

### Color Scheme Generator
```bash
# Generate accessible color palette
lux website colors --base "#0066CC" --mode auto

# Outputs CSS variables with contrast ratios
```

---

## Commands Reference

| Command | Description |
|---------|-------------|
| `create` | Initialize new website |
| `create-portfolio` | Quick portfolio generation with templates |
| `serve` | Start dev server with hot reload |
| `build` | Production build with optimization |
| `scan` | Security vulnerability scan |
| `scan --fix` | Auto-fix security issues |
| `colors` | Generate color palette |
| `add-page` | Add new page to site |
| `add-component` | Add reusable component |
| `optimize` | Optimize images/assets |
| `validate` | Check HTML/CSS/JS |
| `deploy` | Deploy to hosting (configurable) |

---

## Output Structure

```
my-site/
├── src/
│   ├── index.html
│   ├── about.html
│   ├── css/
│   │   ├── main.css
│   │   └── variables.css
│   ├── js/
│   │   ├── main.js
│   │   └── theme.js
│   └── assets/
│       ├── images/
│       └── fonts/
├── dist/               # Production build
├── site.json           # Configuration
├── security.conf       # Security headers
└── README.md
```

---

## Live Editing Flow

```
1. Create: lux website create my-site
     ↓
2. Serve: lux website serve my-site
     ↓
3. Edit: Modify files with live preview
     ↓
4. Scan: lux website scan my-site
     ↓
5. Build: lux website build my-site
     ↓
6. Deploy: dist/ folder ready
```

---

## Security Checklist

Before every deployment:
- [ ] CSP headers configured
- [ ] HTTPS enforced
- [ ] No inline scripts (or nonce)  
- [ ] Images optimized
- [ ] Dependencies scanned
- [ ] No hardcoded secrets
- [ ] Forms have CSRF protection
- [ ] Input sanitized
- [ ] Output encoded

---

## Integration with Other Skills

- **Autonomous Code Architect**: Clean, tested code generation
- **Research Synthesizer**: Latest design trends & security best practices
- **Multi-Agent Coordinator**: Can spawn specialist agents for complex sites
- **ALOE**: Learns from each project to improve future designs

---

## Advanced Design Research & Best Practices

### 🎨 Current Web Design Trends (2025-2026)

#### 1. Dark Mode & High Contrast
- **Why it works:** Reduces eye strain, looks premium, saves battery on OLED
- **Best for:** Luxury brands, tech companies, creative portfolios
- **Implementation:** CSS variables for easy theme switching

#### 2. Glassmorphism & Frosted Glass
```css
.glass {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
}
```
- **Effect:** Modern, depth, premium feel
- **Usage:** Headers, cards, overlays

#### 3. Micro-Interactions
- Hover effects: Scale, color shift, underline animations
- Button states: Loading, success, error animations
- Scroll triggers: Elements fade/slide in as you scroll
- **Why:** Increases engagement, feels responsive

#### 4. Typography-First Design
- **Variable fonts:** One font file, infinite weights/styles
- **Oversized headings:** 5rem+ for impact
- **Font pairing:** Serif + Sans-serif
- **Best pairs:**
  - Playfair Display + Montserrat (luxury)
  - Inter + Merriweather (modern editorial)
  - Oswald + Open Sans (bold)

#### 5. Asymmetric Layouts
- Broken grids: Elements that break the container
- Overlapping: Images overlapping text sections
- **Why:** Visual interest, stands out from templates

---

### 🎯 UX/UI Best Practices

#### Navigation Patterns

**Sticky Header with Hide/Show:**
```javascript
let lastScroll = 0;
window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    const header = document.querySelector('header');
    
    if (currentScroll > lastScroll && currentScroll > 100) {
        header.style.transform = 'translateY(-100%)';
    } else {
        header.style.transform = 'translateY(0)';
    }
    lastScroll = currentScroll;
});
```

**Mobile-First Breakpoints:**
```css
/* Mobile first approach */
/* Base styles for mobile */

/* Tablet */
@media (min-width: 768px) { }

/* Desktop */
@media (min-width: 1024px) { }

/* Large desktop */
@media (min-width: 1400px) { }
```

---

### 🚀 Performance Optimization

#### Critical Rendering Path

**Above-the-fold CSS (Critical CSS):**
```html
<style>
/* Inline critical CSS */
/* Header, hero section, above-fold content */
</style>

<link rel="preload" href="styles.css" as="style" 
      onload="this.onload=null;this.rel='stylesheet'">
```

**Lazy Loading:**
```html
<img loading="lazy" src="image.jpg" alt="Description">
```

**Responsive Images:**
```html
<picture>
    <source srcset="image.webp" type="image/webp">
    <source srcset="image.jpg" type="image/jpeg">
    <img src="image.jpg" alt="Description">
</picture>
```

#### Core Web Vitals (Google Ranking Factor)

| Metric | Target | What it measures |
|--------|--------|------------------|
| **LCP** | < 2.5s | Largest Contentful Paint |
| **FID** | < 100ms | First Input Delay |
| **CLS** | < 0.1 | Cumulative Layout Shift |

---

### 🎨 Color Theory for Websites

#### Psychology of Colors

| Color | Emotion | Best For |
|-------|---------|----------|
| **Black** | Luxury, sophistication | Jewelry, fashion, premium |
| **Gold** | Wealth, quality | Luxury, awards, premium services |
| **Blue** | Trust, professionalism | Finance, healthcare, corporate |
| **Green** | Growth, health, nature | Organic, eco-friendly, wellness |
| **Red** | Urgency, passion | Food, sales, CTAs |
| **Purple** | Creativity, royalty | Beauty, spirituality, luxury |
| **Orange** | Energy, friendly | Food, entertainment, youth |

#### Color Accessibility

**Contrast Ratios (WCAG Guidelines):**
- Normal text: 4.5:1 minimum
- Large text: 3:1 minimum
- Use WebAIM Contrast Checker

---

### 📱 Advanced Layout Techniques

#### CSS Grid vs Flexbox

**Use Grid when:**
- 2D layouts (rows AND columns)
- Complex page layouts
- Card grids

**Use Flexbox when:**
- 1D layouts (row OR column)
- Navigation bars
- Centering elements
- Component-level layouts

#### Modern CSS Features

**Container Queries:**
```css
.card-container {
    container-type: inline-size;
}

@container (min-width: 400px) {
    .card {
        display: grid;
        grid-template-columns: 1fr 2fr;
    }
}
```

**CSS :has() Selector:**
```css
/* Style parent based on child */
.card:has(.sale-badge) {
    border: 2px solid red;
}
```

---

### 🎬 Animation & Motion Design

#### Scroll-Triggered Animations

```javascript
// Intersection Observer API
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
        }
    });
}, { threshold: 0.1 });

document.querySelectorAll('.animate-on-scroll').forEach(el => 
    observer.observe(el));
```

#### Performance Tips
- Animate `transform` and `opacity` only
- Avoid animating `width`, `height`, `top`, `left`
- Use `will-change` sparingly

---

### 🛒 E-commerce Best Practices

#### Product Pages
- **High-Quality Images:** Multiple angles, zoom, 360° rotation
- **Clear CTAs:** "Add to Cart" above fold, sticky on mobile
- **Trust Signals:** Reviews, security badges, return policy

#### Checkout Optimization
- **Guest Checkout:** Don't force account creation
- **Progress Indicator:** Show steps (Cart → Shipping → Payment → Confirmation)
- **Form Optimization:** Auto-fill, inline validation, single-page checkout

---

### 🔍 SEO Best Practices

#### Semantic HTML
```html
<header></header>
<nav></nav>
<main>
    <article></article>
    <aside></aside>
</main>
<footer></footer>
```

#### Structured Data (Schema.org)
```html
<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "Product",
    "name": "Diamond Ring",
    "image": "image.jpg",
    "description": "Beautiful diamond ring",
    "brand": {
        "@type": "Brand",
        "name": "Aurum & Co."
    },
    "offers": {
        "@type": "Offer",
        "price": "12500.00",
        "priceCurrency": "AUD"
    }
}
</script>
```

---

### 🛠️ Tools & Resources

#### Design Tools
- **Figma** - UI/UX design, prototyping
- **Adobe XD** - Wireframing, prototyping
- **Canva** - Quick graphics, social media

#### Development Tools
- **VS Code** - Code editor
- **Chrome DevTools** - Debugging, performance
- **Lighthouse** - Performance auditing
- **Prettier** - Code formatting

#### Inspiration
- **Awwwards** - Best website designs
- **Dribbble** - Design inspiration
- **Behance** - Portfolio showcase

#### Free Resources
- **Unsplash** - Free photos
- **Google Fonts** - Free web fonts
- **Font Awesome** - Free icons
- **Undraw** - Free illustrations

---

### 📊 Design Systems

#### Components to Include
1. **Colors** - Primary, secondary, neutrals, semantic
2. **Typography** - Headings, body, captions
3. **Spacing** - 4px, 8px, 16px, 24px, 32px, 48px, 64px
4. **Buttons** - Primary, secondary, ghost, sizes
5. **Forms** - Inputs, selects, checkboxes, radios
6. **Cards** - Product cards, info cards
7. **Navigation** - Header, footer, breadcrumbs

---

### ✅ Website Launch Checklist

#### Functionality
- [ ] All links work
- [ ] Forms submit correctly
- [ ] Mobile responsive
- [ ] Cross-browser tested

#### Performance
- [ ] Images optimized (WebP where possible)
- [ ] CSS/JS minified
- [ ] Lazy loading implemented
- [ ] CDN configured

#### SEO
- [ ] Meta tags complete
- [ ] XML sitemap created
- [ ] Structured data added
- [ ] Google Analytics installed

#### Accessibility
- [ ] Alt text on images
- [ ] Keyboard navigation works
- [ ] Color contrast sufficient
- [ ] ARIA labels where needed

#### Legal
- [ ] Privacy policy
- [ ] Terms of service
- [ ] Cookie consent
- [ ] SSL certificate

---

This skill transforms OpenClaw into a professional web agency — creating, securing, and deploying websites with cutting-edge design principles and best practices.
