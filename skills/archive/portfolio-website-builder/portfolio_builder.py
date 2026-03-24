#!/usr/bin/env python3
"""
Portfolio Website Builder
"""

import os

class PortfolioBuilder:
    """Build professional portfolio websites"""
    
    def create_modern_portfolio(self, name, title, services, projects=None):
        """Create modern portfolio website"""
        
        if projects is None:
            projects = [
                {"name": "AI Agent Project", "desc": "Automated customer service"},
                {"name": "Automation Workflow", "desc": "Saved 20 hours/week"}
            ]
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} - {title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
        
        /* Hero */
        .hero {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 100px 0; text-align: center; }}
        .hero h1 {{ font-size: 3rem; margin-bottom: 1rem; }}
        .hero p {{ font-size: 1.5rem; opacity: 0.9; }}
        
        /* Services */
        .services {{ padding: 80px 0; background: #f8f9fa; }}
        .services h2 {{ text-align: center; font-size: 2.5rem; margin-bottom: 3rem; }}
        .service-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; }}
        .service-card {{ background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .service-card h3 {{ color: #667eea; margin-bottom: 1rem; }}
        
        /* Projects */
        .projects {{ padding: 80px 0; }}
        .projects h2 {{ text-align: center; font-size: 2.5rem; margin-bottom: 3rem; }}
        .project-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 2rem; }}
        .project-card {{ border: 1px solid #e0e0e0; border-radius: 10px; overflow: hidden; }}
        .project-content {{ padding: 1.5rem; }}
        
        /* Contact */
        .contact {{ padding: 80px 0; background: #333; color: white; text-align: center; }}
        .contact h2 {{ font-size: 2.5rem; margin-bottom: 2rem; }}
        .contact a {{ color: #667eea; text-decoration: none; }}
        
        /* Footer */
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
            <div class="service-grid">
                {chr(10).join([f'<div class="service-card"><h3>{service}</h3><p>Professional {service.lower()} services tailored to your needs.</p></div>' for service in services])}
            </div>
        </div>
    </section>
    
    <section class="projects">
        <div class="container">
            <h2>Recent Work</h2>
            <div class="project-grid">
                {chr(10).join([f'<div class="project-card"><div class="project-content"><h3>{p["name"]}</h3><p>{p["desc"]}</p></div></div>' for p in projects])}
            </div>
        </div>
    </section>
    
    <section class="contact">
        <div class="container">
            <h2>Let's Work Together</h2>
            <p>Ready to start your project? <a href="mailto:contact@example.com">Get in touch</a></p>
        </div>
    </section>
    
    <footer>
        <p>&copy; 2026 {name}. All rights reserved.</p>
    </footer>
</body>
</html>"""
        
        return html
    
    def save_portfolio(self, html, output_dir="portfolio"):
        """Save portfolio to file"""
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, "index.html")
        
        with open(filepath, "w") as f:
            f.write(html)
        
        return filepath

def create_portfolio(name, title, services, projects=None, output_dir="portfolio"):
    """Main portfolio creation function"""
    
    builder = PortfolioBuilder()
    html = builder.create_modern_portfolio(name, title, services, projects)
    filepath = builder.save_portfolio(html, output_dir)
    
    return {
        "filepath": filepath,
        "services": services,
        "next_steps": [
            "Customize content in index.html",
            "Add your projects",
            "Update contact email",
            "Deploy to Vercel/Netlify",
            "Connect custom domain"
        ]
    }

if __name__ == "__main__":
    result = create_portfolio(
        name="Your Name",
        title="AI Automation Specialist",
        services=["AI Agent Development", "Workflow Automation", "Technical Consulting"]
    )
    print(f"Portfolio created: {result['filepath']}")
