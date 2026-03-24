#!/usr/bin/env python3
"""
Website Designer - Core Engine
Creates websites, manages live editing, security scanning
"""
import os
import json
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

def print_header(text):
    print(f"\n{'='*50}")
    print(f"  {text}")
    print(f"{'='*50}\n")


class PortfolioBuilder:
    """Build professional portfolio websites - Merged from portfolio-website-builder"""
    
    TEMPLATES = {
        "modern": "modern",
        "minimalist": "minimalist", 
        "creative": "creative",
        "professional": "professional"
    }
    
    def create_portfolio(self, name, title, services, projects=None, template="modern", output_dir=None):
        """Create portfolio website with specified template"""
        
        if projects is None:
            projects = [
                {"name": "AI Agent Project", "desc": "Automated customer service solution"},
                {"name": "Automation Workflow", "desc": "Saved 20 hours/week through automation"}
            ]
        
        if output_dir is None:
            output_dir = f"{name.lower().replace(' ', '-')}-portfolio"
        
        # Create directory structure
        base_dir = Path(f"./{output_dir}")
        base_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate HTML based on template
        if template == "modern":
            html = self._modern_template(name, title, services, projects)
        elif template == "minimalist":
            html = self._minimalist_template(name, title, services, projects)
        elif template == "creative":
            html = self._creative_template(name, title, services, projects)
        else:
            html = self._professional_template(name, title, services, projects)
        
        # Save files
        filepath = base_dir / "index.html"
        with open(filepath, "w") as f:
            f.write(html)
        
        # Create README
        readme = self._generate_readme(name, output_dir)
        with open(base_dir / "README.md", "w") as f:
            f.write(readme)
        
        return {
            "filepath": str(filepath),
            "output_dir": str(base_dir),
            "template": template,
            "services": services,
            "next_steps": [
                "Customize content in index.html",
                "Add your projects and images",
                "Update contact email and social links",
                "Deploy to Vercel/Netlify/GitHub Pages",
                "Connect custom domain"
            ]
        }
    
    def _modern_template(self, name, title, services, projects):
        """Modern gradient template"""
        services_html = "\n".join([
            f'<div class="service-card"><h3>{service}</h3><p>Professional {service.lower()} services tailored to your needs.</p></div>' 
            for service in services
        ])
        projects_html = "\n".join([
            f'<div class="project-card"><div class="project-content"><h3>{p["name"]}</h3><p>{p["desc"]}</p></div></div>' 
            for p in projects
        ])
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} - {title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
        .hero {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 100px 0; text-align: center; }}
        .hero h1 {{ font-size: 3rem; margin-bottom: 1rem; }}
        .hero p {{ font-size: 1.5rem; opacity: 0.9; }}
        .services {{ padding: 80px 0; background: #f8f9fa; }}
        .services h2 {{ text-align: center; font-size: 2.5rem; margin-bottom: 3rem; }}
        .service-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; }}
        .service-card {{ background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .service-card h3 {{ color: #667eea; margin-bottom: 1rem; }}
        .projects {{ padding: 80px 0; }}
        .projects h2 {{ text-align: center; font-size: 2.5rem; margin-bottom: 3rem; }}
        .project-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 2rem; }}
        .project-card {{ border: 1px solid #e0e0e0; border-radius: 10px; overflow: hidden; }}
        .project-content {{ padding: 1.5rem; }}
        .contact {{ padding: 80px 0; background: #333; color: white; text-align: center; }}
        .contact h2 {{ font-size: 2.5rem; margin-bottom: 2rem; }}
        .contact a {{ color: #667eea; text-decoration: none; }}
        footer {{ padding: 20px; text-align: center; background: #222; color: #666; }}
    </style>
</head>
<body>
    <section class="hero">
        <div class="container">
            <h1>{name}</h1>
            <p>{title}</p>
        </div>
    </section>
    <section class="services">
        <div class="container">
            <h2>Services</h2>
            <div class="service-grid">{services_html}</div>
        </div>
    </section>
    <section class="projects">
        <div class="container">
            <h2>Recent Work</h2>
            <div class="project-grid">{projects_html}</div>
        </div>
    </section>
    <section class="contact">
        <div class="container">
            <h2>Let's Work Together</h2>
            <p>Ready to start your project? <a href="mailto:contact@example.com">Get in touch</a></p>
        </div>
    </section>
    <footer><p>&copy; 2026 {name}. All rights reserved.</p></footer>
</body>
</html>'''
    
    def _minimalist_template(self, name, title, services, projects):
        """Clean minimalist template"""
        services_html = "\n".join([f'<li>{service}</li>' for service in services])
        projects_html = "\n".join([f'<li><strong>{p["name"]}</strong> - {p["desc"]}</li>' for p in projects])
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} - {title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Helvetica Neue', Arial, sans-serif; line-height: 1.8; color: #222; max-width: 800px; margin: 0 auto; padding: 60px 20px; }}
        h1 {{ font-size: 2.5rem; font-weight: 300; margin-bottom: 0.5rem; }}
        .title {{ color: #666; font-size: 1.2rem; margin-bottom: 3rem; }}
        h2 {{ font-size: 1.2rem; text-transform: uppercase; letter-spacing: 2px; margin: 3rem 0 1rem; color: #999; }}
        ul {{ list-style: none; }}
        li {{ padding: 0.5rem 0; border-bottom: 1px solid #eee; }}
        a {{ color: #222; text-decoration: none; border-bottom: 1px solid #222; }}
        footer {{ margin-top: 4rem; padding-top: 2rem; border-top: 1px solid #eee; color: #999; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <h1>{name}</h1>
    <p class="title">{title}</p>
    <h2>Services</h2>
    <ul>{services_html}</ul>
    <h2>Projects</h2>
    <ul>{projects_html}</ul>
    <h2>Contact</h2>
    <p><a href="mailto:contact@example.com">contact@example.com</a></p>
    <footer>&copy; 2026 {name}</footer>
</body>
</html>'''
    
    def _creative_template(self, name, title, services, projects):
        """Bold creative template"""
        services_html = "\n".join([f'<span class="tag">{service}</span>' for service in services])
        projects_html = "\n".join([f'<div class="project"><h3>{p["name"]}</h3><p>{p["desc"]}</p></div>' for p in projects])
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} - {title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Georgia', serif; line-height: 1.6; color: #1a1a1a; background: #fafafa; }}
        .container {{ max-width: 1000px; margin: 0 auto; padding: 0 20px; }}
        .hero {{ background: #1a1a1a; color: #fff; padding: 120px 0; text-align: center; }}
        .hero h1 {{ font-size: 4rem; font-weight: 400; letter-spacing: -2px; margin-bottom: 1rem; }}
        .hero p {{ font-size: 1.3rem; color: #888; }}
        .section {{ padding: 80px 0; }}
        .tags {{ display: flex; flex-wrap: wrap; gap: 1rem; justify-content: center; margin-top: 2rem; }}
        .tag {{ background: #fff; padding: 0.5rem 1.5rem; border-radius: 50px; font-family: sans-serif; font-size: 0.9rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .projects-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin-top: 3rem; }}
        .project {{ background: #fff; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 20px rgba(0,0,0,0.05); }}
        .project h3 {{ font-size: 1.5rem; margin-bottom: 0.5rem; }}
        .contact {{ background: #1a1a1a; color: #fff; padding: 80px 0; text-align: center; }}
        .contact a {{ color: #fff; text-decoration: underline; text-underline-offset: 4px; }}
        footer {{ padding: 40px; text-align: center; color: #666; }}
    </style>
</head>
<body>
    <section class="hero">
        <div class="container">
            <h1>{name}</h1>
            <p>{title}</p>
            <div class="tags">{services_html}</div>
        </div>
    </section>
    <section class="section">
        <div class="container">
            <h2 style="text-align: center; font-size: 2rem;">Selected Work</h2>
            <div class="projects-grid">{projects_html}</div>
        </div>
    </section>
    <section class="contact">
        <div class="container">
            <h2 style="font-size: 2rem; margin-bottom: 1rem;">Let's collaborate</h2>
            <p><a href="mailto:contact@example.com">Get in touch</a></p>
        </div>
    </section>
    <footer>&copy; 2026 {name}. All rights reserved.</footer>
</body>
</html>'''
    
    def _professional_template(self, name, title, services, projects):
        """Corporate professional template"""
        services_html = "\n".join([
            f'<div class="service"><h3>{service}</h3><p>Expert {service.lower()} solutions for businesses of all sizes.</p></div>' 
            for service in services
        ])
        projects_html = "\n".join([
            f'<div class="project-item"><h4>{p["name"]}</h4><p>{p["desc"]}</p></div>' for p in projects
        ])
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} | {title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 1100px; margin: 0 auto; padding: 0 20px; }}
        header {{ background: #fff; border-bottom: 1px solid #e0e0e0; padding: 20px 0; }}
        header .container {{ display: flex; justify-content: space-between; align-items: center; }}
        .logo {{ font-size: 1.5rem; font-weight: 700; color: #1a365d; }}
        .hero {{ background: #1a365d; color: white; padding: 100px 0; }}
        .hero h1 {{ font-size: 2.8rem; margin-bottom: 1rem; }}
        .hero p {{ font-size: 1.3rem; opacity: 0.9; max-width: 600px; }}
        .services {{ padding: 80px 0; background: #f7fafc; }}
        .services h2 {{ text-align: center; font-size: 2rem; margin-bottom: 3rem; color: #1a365d; }}
        .services-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem; }}
        .service {{ background: white; padding: 2rem; border-radius: 8px; border: 1px solid #e2e8f0; }}
        .service h3 {{ color: #1a365d; margin-bottom: 0.5rem; }}
        .projects {{ padding: 80px 0; }}
        .projects h2 {{ text-align: center; font-size: 2rem; margin-bottom: 3rem; color: #1a365d; }}
        .project-item {{ padding: 1.5rem; border-left: 4px solid #1a365d; margin-bottom: 1rem; background: #f7fafc; }}
        .project-item h4 {{ color: #1a365d; margin-bottom: 0.5rem; }}
        .contact {{ background: #1a365d; color: white; padding: 60px 0; text-align: center; }}
        .contact h2 {{ margin-bottom: 1rem; }}
        .btn {{ display: inline-block; background: white; color: #1a365d; padding: 12px 30px; text-decoration: none; border-radius: 4px; margin-top: 1rem; font-weight: 600; }}
        footer {{ background: #0d1b2a; color: #718096; padding: 30px 0; text-align: center; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="logo">{name}</div>
        </div>
    </header>
    <section class="hero">
        <div class="container">
            <h1>{title}</h1>
            <p>Delivering exceptional results through expertise and innovation.</p>
        </div>
    </section>
    <section class="services">
        <div class="container">
            <h2>Our Services</h2>
            <div class="services-grid">{services_html}</div>
        </div>
    </section>
    <section class="projects">
        <div class="container">
            <h2>Case Studies</h2>
            {projects_html}
        </div>
    </section>
    <section class="contact">
        <div class="container">
            <h2>Ready to get started?</h2>
            <p>Contact us to discuss your project requirements.</p>
            <a href="mailto:contact@example.com" class="btn">Contact Us</a>
        </div>
    </section>
    <footer>
        <div class="container">
            <p>&copy; 2026 {name}. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>'''
    
    def _generate_readme(self, name, output_dir):
        """Generate README for portfolio"""
        return f'''# {name} Portfolio

Professional portfolio website generated with Website Designer.

## Structure

```
{output_dir}/
├── index.html    # Main portfolio page
└── README.md     # This file
```

## Customization

1. **Edit Content**: Open `index.html` and modify:
   - Name and title
   - Services list
   - Project descriptions
   - Contact email

2. **Add Images**: Create an `images/` folder and reference them in HTML

3. **Styling**: Modify the CSS in the `<style>` section

## Deployment

### Vercel
```bash
npm i -g vercel
vercel
```

### Netlify
```bash
npm i -g netlify-cli
netlify deploy
```

### GitHub Pages
1. Push to GitHub repository
2. Enable GitHub Pages in settings
3. Select main branch as source

## Next Steps

- [ ] Add professional photo
- [ ] Include portfolio images
- [ ] Add testimonials section
- [ ] Connect contact form
- [ ] Add social media links
- [ ] Set up custom domain

---
Generated by OpenClaw Website Designer
'''


def create_portfolio_quick(name, title, services, template="modern", projects=None):
    """Quick portfolio creation function"""
    builder = PortfolioBuilder()
    result = builder.create_portfolio(name, title, services, projects, template)
    return result

def create_website(name, site_type="business"):
    """Create a new website project"""
    print_header(f"Creating {site_type} website: {name}")
    
    base_dir = Path(f"./{name}")
    if base_dir.exists():
        print(f"❌ Directory '{name}' already exists")
        return False
    
    # Create directory structure
    dirs = [
        base_dir / "src",
        base_dir / "src" / "css",
        base_dir / "src" / "js",
        base_dir / "src" / "assets" / "images",
        base_dir / "src" / "assets" / "fonts",
        base_dir / "dist"
    ]
    for d in dirs:
        d.mkdir(parents=True)
        print(f"  ✓ Created {d}/")
    
    # Generate site configuration
    config = {
        "name": name,
        "description": f"A {site_type} website built with Lux",
        "url": "https://example.com",
        "type": site_type,
        "created": datetime.now().isoformat(),
        "theme": {
            "primary": "#6366f1",
            "secondary": "#ec4899",
            "background": "#ffffff",
            "surface": "#f9fafb",
            "text": "#111827",
            "textMuted": "#6b7280",
            "border": "#e5e7eb",
            "success": "#10b981",
            "warning": "#f59e0b",
            "error": "#ef4444",
            "darkMode": True
        },
        "typography": {
            "fontHeading": "Inter, sans-serif",
            "fontBody": "Inter, sans-serif",
            "scale": 1.125
        },
        "security": {
            "csp": True,
            "hsts": True,
            "xss": True,
            "scanOnBuild": True
        },
        "seo": {
            "title": f"{name} | Welcome",
            "description": f"Welcome to {name}",
            "keywords": []
        }
    }
    
    with open(base_dir / "site.json", "w") as f:
        json.dump(config, f, indent=2)
    print(f"  ✓ Created site.json")
    
    # Generate CSS variables file
    css_vars = generate_css_variables(config)
    with open(base_dir / "src" / "css" / "variables.css", "w") as f:
        f.write(css_vars)
    print(f"  ✓ Created CSS variables")
    
    # Generate main CSS
    main_css = generate_main_css()
    with open(base_dir / "src" / "css" / "main.css", "w") as f:
        f.write(main_css)
    print(f"  ✓ Created main.css")
    
    # Generate HTML based on type
    html = generate_html(site_type, config)
    with open(base_dir / "src" / "index.html", "w") as f:
        f.write(html)
    print(f"  ✓ Created index.html")
    
    # Generate theme toggle JS
    theme_js = generate_theme_js()
    with open(base_dir / "src" / "js" / "theme.js", "w") as f:
        f.write(theme_js)
    print(f"  ✓ Created theme.js")
    
    # Generate main JS
    main_js = generate_main_js()
    with open(base_dir / "src" / "js" / "main.js", "w") as f:
        f.write(main_js)
    print(f"  ✓ Created main.js")
    
    # Generate security headers config
    security_conf = generate_security_headers(config)
    with open(base_dir / "security.conf", "w") as f:
        f.write(security_conf)
    print(f"  ✓ Created security.conf")
    
    # Generate README
    readme = generate_readme(name, site_type)
    with open(base_dir / "README.md", "w") as f:
        f.write(readme)
    print(f"  ✓ Created README.md")
    
    print(f"\n✅ Website '{name}' created successfully!")
    print(f"\nNext steps:")
    print(f"  1. cd {name}")
    print(f"  2. Edit site.json to customize")
    print(f"  3. Run: python3 website_designer.py serve {name}")
    return True

def generate_css_variables(config):
    theme = config["theme"]
    return f""":root {{
  /* Colors */
  --color-primary: {theme['primary']};
  --color-secondary: {theme['secondary']};
  --color-bg: {theme['background']};
  --color-surface: {theme['surface']};
  --color-text: {theme['text']};
  --color-text-muted: {theme['textMuted']};
  --color-border: {theme['border']};
  --color-success: {theme['success']};
  --color-warning: {theme['warning']};
  --color-error: {theme['error']};
  
  /* Typography */
  --font-heading: {config['typography']['fontHeading']};
  --font-body: {config['typography']['fontBody']};
  
  /* Spacing (8px base) */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-12: 3rem;
  --space-16: 4rem;
  
  /* Layout */
  --max-width: 1200px;
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 1rem;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1);
  
  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-base: 300ms ease;
}}

/* Dark mode */
@media (prefers-color-scheme: dark) {{
  :root {{
    --color-bg: #0f172a;
    --color-surface: #1e293b;
    --color-text: #f8fafc;
    --color-text-muted: #94a3b8;
    --color-border: #334155;
  }}
}}

[data-theme="dark"] {{
  --color-bg: #0f172a;
  --color-surface: #1e293b;
  --color-text: #f8fafc;
  --color-text-muted: #94a3b8;
  --color-border: #334155;
}}
"""

def generate_main_css():
    return '''/* Reset */
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  scroll-behavior: smooth;
}

body {
  font-family: var(--font-body);
  background-color: var(--color-bg);
  color: var(--color-text);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-heading);
  font-weight: 700;
  line-height: 1.2;
  color: var(--color-text);
}

h1 { font-size: 3rem; margin-bottom: var(--space-6); }
h2 { font-size: 2.25rem; margin-bottom: var(--space-4); }
h3 { font-size: 1.5rem; margin-bottom: var(--space-3); }

p {
  margin-bottom: var(--space-4);
  color: var(--color-text-muted);
}

/* Layout */
.container {
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 0 var(--space-4);
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-3) var(--space-6);
  font-family: inherit;
  font-size: 1rem;
  font-weight: 600;
  text-decoration: none;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-base);
}

.btn-primary {
  background-color: var(--color-primary);
  color: white;
}

.btn-primary:hover {
  opacity: 0.9;
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-secondary {
  background-color: transparent;
  color: var(--color-primary);
  border: 2px solid var(--color-primary);
}

.btn-secondary:hover {
  background-color: var(--color-primary);
  color: white;
}

/* Cards */
.card {
  background-color: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  box-shadow: var(--shadow-sm);
  transition: transform var(--transition-base), box-shadow var(--transition-base);
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

/* Navigation */
.nav {
  position: sticky;
  top: 0;
  background-color: var(--color-bg);
  border-bottom: 1px solid var(--color-border);
  backdrop-filter: blur(10px);
  z-index: 100;
}

.nav-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
}

.nav-links {
  display: flex;
  gap: var(--space-6);
  list-style: none;
}

.nav-links a {
  color: var(--color-text-muted);
  text-decoration: none;
  font-weight: 500;
  transition: color var(--transition-fast);
}

.nav-links a:hover {
  color: var(--color-text);
}

/* Hero */
.hero {
  padding: var(--space-16) 0;
  text-align: center;
}

.hero h1 {
  background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero p {
  font-size: 1.25rem;
  max-width: 600px;
  margin: 0 auto var(--space-8);
}

/* Grid */
.grid {
  display: grid;
  gap: var(--space-6);
}

.grid-3 {
  grid-template-columns: repeat(3, 1fr);
}

@media (max-width: 768px) {
  .grid-3 {
    grid-template-columns: 1fr;
  }
  
  h1 { font-size: 2rem; }
  h2 { font-size: 1.5rem; }
}

/* Footer */
.footer {
  background-color: var(--color-surface);
  border-top: 1px solid var(--color-border);
  padding: var(--space-8) 0;
  margin-top: var(--space-16);
  text-align: center;
  color: var(--color-text-muted);
}

/* Utility */
.text-center { text-align: center; }
.mt-8 { margin-top: var(--space-8); }
.mb-4 { margin-bottom: var(--space-4); }
'''

def generate_html(site_type, config):
    theme = config["theme"]
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{config['seo']['description']}">
  <meta name="theme-color" content="{theme['primary']}">
  
  <!-- Security -->
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  
  <title>{config['seo']['title']}</title>
  
  <!-- Preconnect for performance -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  
  <!-- Fonts -->
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  
  <!-- Styles -->
  <link rel="stylesheet" href="css/variables.css">
  <link rel="stylesheet" href="css/main.css">
</head>
<body>
  <!-- Navigation -->
  <nav class="nav">
    <div class="container nav-content">
      <a href="#" class="logo" style="font-weight: 700; font-size: 1.5rem; color: var(--color-text); text-decoration: none;">
        {config['name']}
      </a>
      <ul class="nav-links">
        <li><a href="#home">Home</a></li>
        <li><a href="#about">About</a></li>
        <li><a href="#services">Services</a></li>
        <li><a href="#contact">Contact</a></li>
      </ul>
      <button class="btn btn-primary" onclick="toggleTheme()">🌓 Theme</button>
    </div>
  </nav>

  <!-- Hero Section -->
  <section id="home" class="hero">
    <div class="container">
      <h1>Welcome to {config['name']}</h1>
      <p>{config['description']}</p>
      <div style="display: flex; gap: var(--space-4); justify-content: center;">
        <a href="#services" class="btn btn-primary">Get Started</a>
        <a href="#about" class="btn btn-secondary">Learn More</a>
      </div>
      </div>
  </section>

  <!-- Features/Services -->
  <section id="services" class="container mt-8">
    <h2 class="text-center mb-4">Our Services</h2>
    <div class="grid grid-3">
      <div class="card">
        <h3>🚀 Fast</h3>
        <p>Lightning-fast performance optimized for modern web standards.</p>
      </div>
      <div class="card">
        <h3>🔒 Secure</h3>
        <p>Built with security-first approach to protect your data.</p>
      </div>
      <div class="card">
        <h3>📱 Responsive</h3>
        <p>Looks great on any device, from mobile to desktop.</p>
      </div>
    </div>
  </section>

  <!-- About Section -->
  <section id="about" class="container mt-8">
    <div class="card" style="max-width: 800px; margin: 0 auto;">
      <h2 class="text-center">About Us</h2>
      <p style="text-align: center;">
        We are dedicated to delivering exceptional quality and service. 
        Our team combines creativity with technical expertise to create 
        outstanding digital experiences.
      </p>
    </div>
  </section>

  <!-- Contact Section -->
  <section id="contact" class="container mt-8">
    <div class="card" style="max-width: 600px; margin: 0 auto;">
      <h2 class="text-center">Get In Touch</h2>
      <form style="display: flex; flex-direction: column; gap: var(--space-4);">
        <input type="text" placeholder="Your Name" class="btn" style="text-align: left; background: var(--color-surface); cursor: text;">
        <input type="email" placeholder="Your Email" class="btn" style="text-align: left; background: var(--color-surface); cursor: text;">
        <textarea placeholder="Your Message" rows="4" class="btn" style="text-align: left; background: var(--color-surface); cursor: text; resize: vertical;"></textarea>
        <button type="submit" class="btn btn-primary">Send Message</button>
      </form>
    </div>
  </section>

  <!-- Footer -->
  <footer class="footer">
    <div class="container">
      <p>&copy; {datetime.now().year} {config['name']}. All rights reserved.</p>
      <p style="margin-top: var(--space-2); font-size: 0.875rem;">
        Built with ❤️ using Lux Website Designer
      </p>
    </div>
  </footer>

  <!-- Scripts -->
  <script src="js/theme.js"></script>
  <script src="js/main.js"></script>
</body>
</html>
'''

def generate_theme_js():
    return '''// Theme Toggle
document.addEventListener('DOMContentLoaded', () => {
  // Check for saved theme preference or default to system
  const savedTheme = localStorage.getItem('theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  
  if (savedTheme) {
    document.documentElement.setAttribute('data-theme', savedTheme);
  } else if (prefersDark) {
    document.documentElement.setAttribute('data-theme', 'dark');
  }
});

function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute('data-theme');
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
  
  document.documentElement.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
}

// Export for use in other scripts
if (typeof module !== 'undefined') {
  module.exports = { toggleTheme };
}
'''

def generate_main_js():
    return '''// Main JavaScript - Add your custom functionality here

document.addEventListener('DOMContentLoaded', () => {
  // Smooth scrolling for navigation links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });
  
  // Form submission handling
  const form = document.querySelector('form');
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      // Add your form handling logic here
      alert('Form submitted! (Demo mode)');
    });
  }
  
  // Intersection Observer for animations
  const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1
  };
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, observerOptions);
  
  // Observe cards for scroll animations
  document.querySelectorAll('.card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(card);
  });
});

// Console greeting
console.log('%c🔥 Built with Lux Website Designer', 'color: #6366f1; font-size: 14px; font-weight: bold;');
'''

def generate_security_headers(config):
    seo = config.get('seo', {})
    return f'''# Security Headers Configuration
# Add these to your web server (Apache, Nginx, .htaccess, etc.)

# Content Security Policy
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self';

# XSS Protection
X-XSS-Protection: 1; mode=block

# Content Type Options
X-Content-Type-Options: nosniff

# Frame Options (clickjacking)
X-Frame-Options: DENY

# HTTPS Strict Transport (uncomment when HTTPS enabled)
# Strict-Transport-Security: max-age=31536000; includeSubDomains; preload

# Referrer Policy
Referrer-Policy: strict-origin-when-cross-origin

# Permissions Policy
Permission-Policy: camera=(), microphone=(), geolocation=(self), payment=()

# SEO/Meta
X-Description: {seo.get('description', '')}
'''

def generate_readme(name, site_type):
    return f'''# {name}

A {site_type} website built with Lux Website Designer.

## Development

1. Edit `site.json` to customize theme and content
2. Run local server:
   ```bash
   python3 website_designer.py serve {name}
   ```
3. Edit files in `src/` with live reload

## Structure

- `src/index.html` - Main page
- `src/css/` - Stylesheets
- `src/js/` - JavaScript
- `src/assets/` - Images, fonts
- `site.json` - Configuration
- `security.conf` - Security headers

## Deployment

1. Build production version:
   ```bash
   python3 website_designer.py build {name}
   ```
2. Deploy contents of `dist/` folder

## Security

This site includes:
- ✅ Content Security Policy headers
- ✅ XSS protection
- ✅ Clickjacking protection
- ✅ Secure defaults

See `security.conf` for server configuration.

---

Built with ❤️ by Lux
'''

# Command line interface
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 website_designer.py <command> [options]")
        print("")
        print("Commands:")
        print("  create <name> [--type business|portfolio|landing|blog]")
        print("  create-portfolio <name> <title> [--template modern|minimalist|creative|professional]")
        print("  serve <name> [--port 3000]")
        print("  build <name>")
        print("  scan <name> [--fix]")
        print("")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "create":
        if len(sys.argv) < 3:
            print("Usage: create <name> [--type business]")
            sys.exit(1)
        name = sys.argv[2]
        site_type = "business"
        if "--type" in sys.argv:
            type_idx = sys.argv.index("--type") + 1
            if type_idx < len(sys.argv):
                site_type = sys.argv[type_idx]
        create_website(name, site_type)
    
    elif command == "serve":
        if len(sys.argv) < 3:
            print("Usage: serve <name> [--port 3000]")
            sys.exit(1)
        name = sys.argv[2]
        
        site_dir = Path(f"./{name}/src")
        if not site_dir.exists():
            print(f"❌ Site '{name}' not found")
            sys.exit(1)
        
        # Use the live reload server
        print("Starting live reload server...")
        subprocess.run([
            "python3",
            "/home/skux/.openclaw/workspace/skills/website-designer/website_server.py",
            name
        ])
    
    elif command == "create-portfolio":
        if len(sys.argv) < 4:
            print("Usage: create-portfolio <name> <title> [--template modern|minimalist|creative|professional]")
            print("Example: create-portfolio 'John Doe' 'Web Developer' --template modern")
            sys.exit(1)
        name = sys.argv[2]
        title = sys.argv[3]
        template = "modern"
        services = ["Web Development", "UI/UX Design", "Consulting"]
        
        if "--template" in sys.argv:
            t_idx = sys.argv.index("--template") + 1
            if t_idx < len(sys.argv):
                template = sys.argv[t_idx]
        
        print_header(f"Creating Portfolio: {name}")
        print(f"  Template: {template}")
        print(f"  Title: {title}")
        
        result = create_portfolio_quick(name, title, services, template)
        
        print(f"\n✅ Portfolio created successfully!")
        print(f"  Location: {result['output_dir']}/")
        print(f"  File: {result['filepath']}")
        print(f"\nNext steps:")
        for step in result['next_steps']:
            print(f"  • {step}")
    
    elif command == "build":
        if len(sys.argv) < 3:
            print("Usage: build <name>")
            sys.exit(1)
        name = sys.argv[2]
        print_header(f"Building {name} for production")
        
        src_dir = Path(f"./{name}/src")
        dist_dir = Path(f"./{name}/dist")
        
        if not src_dir.exists():
            print(f"❌ Site '{name}' not found")
            sys.exit(1)
        
        # Clean dist
        if dist_dir.exists():
            shutil.rmtree(dist_dir)
        
        # Copy src to dist
        shutil.copytree(src_dir, dist_dir)
        print(f"  ✓ Copied source to dist/")
        
        # Minify CSS (simple version - could be enhanced)
        import re
        for css_file in dist_dir.glob("**/*.css"):
            with open(css_file, 'r') as f:
                content = f.read()
            # Simple minification
            content = re.sub(r'/\*[\s\S]*?\*/', '', content)  # Remove comments
            content = re.sub(r'\s+', ' ', content)  # Collapse whitespace
            content = re.sub(r';\s*}', '}', content)  # Remove last semicolon
            content = re.sub(r'\s*{\s*', '{', content)  # Clean braces
            content = re.sub(r'\s*}\s*', '}', content)
            with open(css_file, 'w') as f:
                f.write(content.strip())
        print(f"  ✓ Minified CSS")
        
        # Minify JS
        for js_file in dist_dir.glob("**/*.js"):
            with open(js_file, 'r') as f:
                content = f.read()
            # Simple minification
            content = re.sub(r'/\*[\s\S]*?\*/', '', content)
            content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
            content = re.sub(r'\s+', ' ', content)
            with open(js_file, 'w') as f:
                f.write(content.strip())
        print(f"  ✓ Minified JavaScript")
        
        # Minify HTML
        for html_file in dist_dir.glob("**/*.html"):
            with open(html_file, 'r') as f:
                content = f.read()
            content = re.sub(r'>\s+<', '><', content)  # Remove whitespace between tags
            content = re.sub(r'\s+', ' ', content)
            with open(html_file, 'w') as f:
                f.write(content.strip())
        print(f"  ✓ Minified HTML")
        
        # Copy security config
        sec_src = Path(f"./{name}/security.conf")
        if sec_src.exists():
            sec_dst = dist_dir / "security.conf"
            shutil.copy2(sec_src, sec_dst)
            print(f"  ✓ Copied security headers")
        
        print(f"\n✅ Build complete!")
        print(f"  Output: ./{name}/dist/")
        print(f"  Ready to deploy!")
    
    elif command == "scan":
        if len(sys.argv) < 3:
            print("Usage: scan <name> [--fix]")
            sys.exit(1)
        name = sys.argv[2]
        auto_fix = "--fix" in sys.argv
        
        print_header(f"Security Scan: {name}")
        
        src_dir = Path(f"./{name}")
        if not src_dir.exists():
            print(f"❌ Site '{name}' not found")
            sys.exit(1)
        
        issues = []
        
        # Check for CSP
        html_files = list(src_dir.glob("src/**/*.html"))
        for html_file in html_files:
            with open(html_file, 'r') as f:
                content = f.read()
            if 'http-equiv="Content-Security-Policy"' not in content:
                issues.append(f"Missing CSP meta tag in {html_file.relative_to(src_dir)}")
        
        # Check for inline scripts without nonce
        if html_files:
            with open(html_files[0], 'r') as f:
                content = f.read()
            if 'onclick=' in content and 'nonce' not in content:
                issues.append("Inline event handlers detected (consider moving to JS file)")
        
        # Check for HTTPS links
        with open(list(html_files)[0], 'r') as f:
            content = f.read()
        if 'http://' in content or 'href="//' in content:
            issues.append("HTTP URLs found - use HTTPS only")
        
        # Check for XSS vulnerable patterns
        if 'eval(' in content or 'innerHTML = ' in content:
            issues.append("Potential XSS vulnerability (eval or innerHTML)")
        
        # Report
        if issues:
            print(f"⚠️  Found {len(issues)} potential issue(s):\n")
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue}")
            
            if auto_fix:
                print("\n🔧 Auto-fix not implemented in this version")
                print("   Manual review recommended")
        else:
            print("✅ No security issues found!")
        
        print(f"\n{'='*50}")
        print(f"Scan complete")
        print(f"{'='*50}")
    
    else:
        print(f"Unknown command: {command}")
        print("Use: create, serve, build, or scan")
        sys.exit(1)
