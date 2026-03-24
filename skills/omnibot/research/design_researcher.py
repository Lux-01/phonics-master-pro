"""
Design Researcher Module - Omnibot Phase 2
Researches design trends and generates HTML/CSS mockups.
ACA Methodology: Analyze-Construct-Audit
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path
import os
import zipfile
from io import BytesIO

from .research_orchestrator import ResearchOrchestrator, ResearchFinding


@dataclass
class ColorPalette:
    """Color palette definition."""
    name: str
    primary: str
    secondary: str
    accent: str
    background: str
    text: str
    surface: str
    description: str = ""


@dataclass
class LayoutPattern:
    """Layout pattern with use case."""
    name: str
    description: str
    best_for: List[str]
    complexity: str  # "low", "medium", "high"
    css_template: Optional[str] = None


@dataclass
class TypographySet:
    """Typography recommendation."""
    heading_font: str
    body_font: str
    accent_font: Optional[str]
    notes: str = ""


@dataclass
class DesignTrends:
    """Complete design trends research results."""
    trends_2026: List[str] = field(default_factory=list)
    color_palettes: List[ColorPalette] = field(default_factory=list)
    layout_patterns: List[LayoutPattern] = field(default_factory=list)
    typography: List[TypographySet] = field(default_factory=list)
    recommendation: str = ""
    source_research: Optional[Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'trends_2026': self.trends_2026,
            'color_palettes': [asdict(p) for p in self.color_palettes],
            'layout_patterns': [asdict(p) for p in self.layout_patterns],
            'typography': [asdict(t) for t in self.typography],
            'recommendation': self.recommendation,
        }


class DesignResearcher:
    """
    Research current design trends + generate HTML/CSS mockups.
    
    Capabilities:
    - Research 2026 design trends across multiple sources
    - Generate color palettes based on domain/use case
    - Recommend layout patterns and typography
    - Generate complete HTML/CSS mockups
    - Mobile-first responsive design
    - WCAG accessibility compliance
    """
    
    # Trending design trends for 2026
    TRENDS_2026 = [
        {
            'name': 'Glassmorphism',
            'description': 'Frosted glass effect with blur and transparency',
            'tags': ['modern', 'premium', 'crypto', 'tech'],
            'css_support': True,
        },
        {
            'name': 'Bento Grids',
            'description': 'Card-based layouts inspired by Apple design',
            'tags': ['dashboard', 'SaaS', 'mobile', 'clean'],
            'css_support': True,
        },
        {
            'name': 'Neon Gradients',
            'description': 'Bold gradient combinations with neon accents',
            'tags': ['gaming', 'creative', 'youth', 'energy'],
            'css_support': True,
        },
        {
            'name': '3D Elements',
            'description': 'Subtle 3D illustrations and icons',
            'tags': ['premium', 'tech', 'creative', 'engaging'],
            'css_support': 'partial',
        },
        {
            'name': 'Dark Mode First',
            'description': 'Design for dark mode, light as alternative',
            'tags': ['modern', 'professional', 'developer-focused'],
            'css_support': True,
        },
        {
            'name': 'Ambient Backgrounds',
            'description': 'Soft flowing gradients and aurora effects',
            'tags': ['premium', 'minimal', 'calm'],
            'css_support': True,
        },
        {
            'name': 'Micro-Interactions',
            'description': 'Subtle hover states and button animations',
            'tags': ['engagement', 'retention', 'modern'],
            'css_support': True,
        },
        {
            'name': 'Variable Fonts',
            'description': 'Dynamic typography weight and width adjustments',
            'tags': ['modern', 'performance', 'responsive'],
            'css_support': True,
        },
    ]
    
    # Domain-specific color palettes
    COLOR_PALETTES = {
        'fitness': [
            ColorPalette(
                name="Energy Pulse",
                primary="#FF6B35",
                secondary="#004E89",
                accent="#1A936F",
                background="#0F172A",
                text="#F8FAFC",
                surface="#1E293B",
                description="High-energy palette with vibrant orange and deep navy"
            ),
            ColorPalette(
                name="Iron Will",
                primary="#DC2626",
                secondary="#1F2937",
                accent="#F59E0B",
                background="#111827",
                text="#F9FAFB",
                surface="#374151",
                description="Aggressive red and black for strength-focused brands"
            ),
        ],
        'wellness': [
            ColorPalette(
                name="Zen Garden",
                primary="#059669",
                secondary="#0891B2",
                accent="#84CC16",
                background="#FEFCF3",
                text="#1F2937",
                surface="#FFFFFF",
                description="Calming greens and blues for mental wellness"
            ),
            ColorPalette(
                name="Soft Lavender",
                primary="#8B5CF6",
                secondary="#10B981",
                accent="#F472B6",
                background="#FAFAF9",
                text="#1C1917",
                surface="#FFFFFF",
                description="Gentle pastels for yoga and meditation"
            ),
        ],
        'tech': [
            ColorPalette(
                name="Cyber Terminal",
                primary="#3B82F6",
                secondary="#10B981",
                accent="#F59E0B",
                background="#0A0A0F",
                text="#E5E7EB",
                surface="#18181B",
                description="Dark mode with electric blue and green accents"
            ),
            ColorPalette(
                name="Neon Nights",
                primary="#22D3EE",
                secondary="#A855F7",
                accent="#F472B6",
                background="#000000",
                text="#FFFFFF",
                surface="#111827",
                description="Synthwave-inspired neon on pure black"
            ),
        ],
        'food': [
            ColorPalette(
                name="Fresh Harvest",
                primary="#EA580C",
                secondary="#65A30D",
                accent="#FACC15",
                background="#FFFBEB",
                text="#292524",
                surface="#FFFFFF",
                description="Warm oranges and greens for restaurants"
            ),
            ColorPalette(
                name="Artisan Dark",
                primary="#92400E",
                secondary="#A16207",
                accent="#DC2626",
                background="#1C1917",
                text="#FAFAF9",
                surface="#292524",
                description="Rich browns for coffee shops and bakeries"
            ),
        ],
        'finance': [
            ColorPalette(
                name="Corporate Trust",
                primary="#1E40AF",
                secondary="#059669",
                accent="#DC2626",
                background="#FFFFFF",
                text="#1F2937",
                surface="#F9FAFB",
                description="Professional blue with profit/loss indicators"
            ),
            ColorPalette(
                name="Crypto Dark",
                primary="#8B5CF6",
                secondary="#06B6D4",
                accent="#10B981",
                background="#0F172A",
                text="#F1F5F9",
                surface="#1E293B",
                description="Web3 aesthetic with purple and cyan"
            ),
        ],
        'ecommerce': [
            ColorPalette(
                name="Shopify Classic",
                primary="#059669",
                secondary="#374151",
                accent="#F59E0B",
                background="#FFFFFF",
                text="#111827",
                surface="#F9FAFB",
                description="Conversion-optimized with green CTAs"
            ),
        ],
    }
    
    # Layout patterns
    LAYOUT_PATTERNS = [
        LayoutPattern(
            name="Hero Split",
            description="50/50 split with image/text or feature/content",
            best_for=["landing_pages", "product_intro"],
            complexity="low",
        ),
        LayoutPattern(
            name="Bento Grid",
            description="Card-based grid layout with varying sizes",
            best_for=["features", "pricing", "dashboard"],
            complexity="medium",
        ),
        LayoutPattern(
            name="Asymmetric Hero",
            description="Dynamic hero with overlap and layer effects",
            best_for=["creative", "startups", "agencies"],
            complexity="high",
        ),
        LayoutPattern(
            name="Sticky Sidebar",
            description="Main content scrolls while sidebar stays fixed",
            best_for=["documentation", "blog", "product_detail"],
            complexity="medium",
        ),
        LayoutPattern(
            name="Masonry Gallery",
            description="Pinterest-style masonry grid",
            best_for=["portfolio", "products", "gallery"],
            complexity="medium",
        ),
        LayoutPattern(
            name="Tabbed Content",
            description="Content organized in horizontal tabs",
            best_for=["features", "pricing_comparison", "specs"],
            complexity="low",
        ),
    ]
    
    # Typography combinations
    TYPOGRAPHY_SETS = [
        TypographySet(
            heading_font="Inter",
            body_font="Inter",
            accent_font=None,
            notes="Modern sans-serif, works for almost any use case"
        ),
        TypographySet(
            heading_font="Poppins",
            body_font="Open Sans",
            accent_font="Playfair Display",
            notes="Friendly with serif accents for elegance"
        ),
        TypographySet(
            heading_font="Space Grotesk",
            body_font="Inter",
            accent_font="JetBrains Mono",
            notes="Tech-forward with monospace code styling"
        ),
        TypographySet(
            heading_font="Plus Jakarta Sans",
            body_font="Source Sans 3",
            accent_font="DM Serif Display",
            notes="Contemporary with editorial serif contrast"
        ),
        TypographySet(
            heading_font="Clash Display",
            body_font="Manrope",
            accent_font=None,
            notes="Bold display font for creative/agency sites"
        ),
    ]
    
    def __init__(self):
        """Initialize Design Researcher."""
        self.orchestrator = ResearchOrchestrator()
    
    def research_trends(self, domain: str) -> DesignTrends:
        """
        Research design trends for a specific domain.
        
        Args:
            domain: Business domain (e.g., "fitness app", "crypto platform")
            
        Returns:
            DesignTrends object with recommendations
        """
        # Use orchestrator to get external trend data
        research_result = self.orchestrator.research(
            f"2026 web design trends for {domain}",
            sources=['dribbble', 'behance', 'material_design', 'awwwards']
        )
        
        # Match domain to known patterns
        domain_lower = domain.lower()
        matched_domain = None
        for key in self.COLOR_PALETTES:
            if key in domain_lower:
                matched_domain = key
                break
        
        # Get relevant trends
        relevant_trends = []
        for trend in self.TRENDS_2026:
            # Score trend relevance to domain
            score = 0
            for tag in trend['tags']:
                if tag in domain_lower:
                    score += 2
                elif any(tag in d for d in [domain_lower]):
                    score += 1
            if score > 0 or matched_domain in ['tech', 'saas']:
                relevant_trends.append(trend['name'])
        
        # Ensure some defaults if no matches
        if not relevant_trends:
            relevant_trends = ['Bento Grids', 'Micro-Interactions', 'Glassmorphism']
        
        # Get color palettes
        palettes = self.COLOR_PALETTES.get(matched_domain, self.COLOR_PALETTES['ecommerce'])
        
        # Get layout patterns
        patterns = []
        if 'landing' in domain_lower or 'homepage' in domain_lower:
            patterns = [p for p in self.LAYOUT_PATTERNS if 'landing' in p.best_for]
        elif 'app' in domain_lower or 'dashboard' in domain_lower:
            patterns = [p for p in self.LAYOUT_PATTERNS if 'dashboard' in p.best_for]
        elif 'portfolio' in domain_lower or 'gallery' in domain_lower:
            patterns = [p for p in self.LAYOUT_PATTERNS if 'portfolio' in p.best_for]
        else:
            patterns = self.LAYOUT_PATTERNS[:3]
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            domain, relevant_trends[:3], palettes[0] if palettes else None
        )
        
        return DesignTrends(
            trends_2026=relevant_trends[:5],
            color_palettes=palettes[:2],
            layout_patterns=patterns[:3],
            typography=self.TYPOGRAPHY_SETS[:3],
            recommendation=recommendation,
            source_research=research_result.to_dict(),
        )
    
    def _generate_recommendation(self, domain: str, trends: List[str],
                                  palette: Optional[ColorPalette]) -> str:
        """Generate a natural language recommendation."""
        parts = [f"For a {domain}, consider:"]
        
        if trends:
            parts.append(f"\n**Trends:** Incorporate {', '.join(trends)} for a contemporary feel.")
        
        if palette:
            parts.append(
                f"\n**Colors:** Use the '{palette.name}' palette with {palette.primary} as "
                f"your primary color to evoke {palette.description.lower()}."
            )
        
        parts.append(
            "\n**Implementation:** Focus on mobile-first responsive design with "
            "WCAG AA accessibility compliance. Test contrast ratios and ensure "
            "keyboard navigation works throughout."
        )
        
        return '\n'.join(parts)
    
    def generate_mockup(self, requirements: Dict[str, Any],
                       research: Optional[DesignTrends] = None) -> Dict[str, str]:
        """
        Generate HTML/CSS mockup based on requirements.
        
        Args:
            requirements: Dict with 'type', 'colors', 'features'
            research: Optional DesignTrends (will research if not provided)
            
        Returns:
            Dict with 'html' and 'css' keys
        """
        if research is None:
            research = self.research_trends(requirements.get('domain', 'generic'))
        
        page_type = requirements.get('type', 'landing_page')
        colors = requirements.get('colors', [])
        features = requirements.get('features', [])
        
        # Select palette based on requirements
        palette = research.color_palettes[0] if research.color_palettes else self.COLOR_PALETTES['ecommerce'][0]
        
        # Select typography
        typography = research.typography[0] if research.typography else self.TYPOGRAPHY_SETS[0]
        
        # Generate CSS
        css = self._generate_css(palette, typography, requirements)
        
        # Generate HTML based on page type
        if page_type == 'landing_page':
            html = self._generate_landing_page(palette, typography, features, requirements)
        elif page_type == 'dashboard':
            html = self._generate_dashboard(palette, typography, features)
        elif page_type == 'pricing':
            html = self._generate_pricing_page(palette, typography, features)
        else:
            html = self._generate_landing_page(palette, typography, features, requirements)
        
        # Combine into single file with inline styles
        full_html = html.replace('{{STYLES}}', f'<style>\n{css}\n</style>')
        
        return {
            'html': full_html,
            'css': css,
            'standalone': full_html,
        }
    
    def _generate_css(self, palette: ColorPalette, typography: TypographySet,
                      requirements: Dict[str, Any]) -> str:
        """Generate complete CSS with design tokens."""
        
        return f"""/* Design System Variables */
:root {{
  /* Colors */
  --color-primary: {palette.primary};
  --color-secondary: {palette.secondary};
  --color-accent: {palette.accent};
  --color-background: {palette.background};
  --color-text: {palette.text};
  --color-surface: {palette.surface};
  
  /* Typography */
  --font-heading: '{typography.heading_font}', system-ui, sans-serif;
  --font-body: '{typography.body_font}', system-ui, sans-serif;
  
  /* Spacing */
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 1.5rem;
  --space-xl: 3rem;
  --space-2xl: 6rem;
  
  /* Border Radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 1rem;
  --radius-xl: 1.5rem;
  
  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-base: 250ms ease;
}}

/* Reset & Base */
*, *::before, *::after {{
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}}

html {{
  scroll-behavior: smooth;
}}

body {{
  font-family: var(--font-body);
  background-color: var(--color-background);
  color: var(--color-text);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}}

h1, h2, h3, h4, h5, h6 {{
  font-family: var(--font-heading);
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: var(--space-md);
}}

h1 {{ font-size: clamp(2rem, 5vw, 3.5rem); }}
h2 {{ font-size: clamp(1.5rem, 4vw, 2.5rem); }}
h3 {{ font-size: clamp(1.25rem, 3vw, 1.75rem); }}

p {{
  margin-bottom: var(--space-md);
  max-width: 65ch;
}}

/* Container */
.container {{
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-lg);
}}

/* Button */
.btn {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-lg);
  font-family: var(--font-heading);
  font-weight: 600;
  font-size: 1rem;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-base);
  text-decoration: none;
}}

.btn-primary {{
  background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
  color: white;
}}

.btn-primary:hover {{
  transform: translateY(-2px);
  box-shadow: 0 10px 30px -10px var(--color-primary);
}}

.btn-secondary {{
  background: transparent;
  color: var(--color-text);
  border: 2px solid var(--color-surface);
}}

.btn-secondary:hover {{
  border-color: var(--color-primary);
  color: var(--color-primary);
}}

/* Card */
.card {{
  background: linear-gradient(145deg, var(--color-surface), transparent);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: var(--radius-lg);
  padding: var(--space-xl);
  transition: transform var(--transition-base);
}}

.card:hover {{
  transform: translateY(-4px);
}}

/* Header */
.header {{
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  backdrop-filter: blur(12px);
  background: rgba({self._hex_to_rgb(palette.background)}, 0.8);
  border-bottom: 1px solid rgba(255,255,255,0.1);
}}

.header-content {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 72px;
}}

.logo {{
  font-family: var(--font-heading);
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--color-text);
  text-decoration: none;
}}

.logo span {{
  color: var(--color-primary);
}}

.nav {{
  display: flex;
  align-items: center;
  gap: var(--space-xl);
}}

.nav a {{
  color: var(--color-text);
  text-decoration: none;
  font-weight: 500;
  opacity: 0.8;
  transition: opacity var(--transition-fast);
}}

.nav a:hover {{
  opacity: 1;
  color: var(--color-primary);
}}

/* Hero */
.hero {{
  min-height: 100vh;
  display: flex;
  align-items: center;
  padding-top: 72px;
  position: relative;
  overflow: hidden;
}}

.hero::before {{
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 800px;
  height: 800px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
  border-radius: 50%;
  opacity: 0.15;
  filter: blur(100px);
  animation: float 20s ease-in-out infinite;
}}

@keyframes float {{
  0%, 100% {{ transform: translate(0, 0) scale(1); }}
  50% {{ transform: translate(-50px, 50px) scale(1.1); }}
}}

.hero-content {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-2xl);
  align-items: center;
}}

.hero-text {{
  position: relative;
  z-index: 1;
}}

.hero h1 {{
  margin-bottom: var(--space-lg);
}}

.hero h1 em {{
  color: var(--color-primary);
  font-style: normal;
}}

.hero-description {{
  font-size: 1.125rem;
  color: rgba({self._hex_to_rgb(palette.text)}, 0.8);
  margin-bottom: var(--space-xl);
}}

.hero-buttons {{
  display: flex;
  gap: var(--space-md);
  flex-wrap: wrap;
}}

.hero-visual {{
  position: relative;
}}

.hero-image {{
  width: 100%;
  aspect-ratio: 4/3;
  background: linear-gradient(135deg, var(--color-surface), transparent);
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba({self._hex_to_rgb(palette.text)}, 0.4);
  font-size: 1.125rem;
}}

/* Features Grid */
.features {{
  padding: var(--space-2xl) 0;
}}

.section-header {{
  text-align: center;
  margin-bottom: var(--space-2xl);
}}

.section-header h2 {{
  margin-bottom: var(--space-md);
}}

.section-header p {{
  color: rgba({self._hex_to_rgb(palette.text)}, 0.7);
  margin: 0 auto;
}}

.features-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--space-lg);
}}

.feature-card {{
  text-align: center;
}}

.feature-icon {{
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  margin: 0 auto var(--space-lg);
}}

.feature-card h3 {{
  margin-bottom: var(--space-sm);
}}

.feature-card p {{
  color: rgba({self._hex_to_rgb(palette.text)}, 0.7);
  font-size: 0.95rem;
}}

/* CTA Section */
.cta {{
  padding: var(--space-2xl) 0;
  text-align: center;
}}

.cta-content {{
  max-width: 600px;
  margin: 0 auto;
}}

/* Form */
.form-group {{
  margin-bottom: var(--space-lg);
}}

.form-group label {{
  display: block;
  margin-bottom: var(--space-sm);
  font-weight: 500;
}}

.form-group input,
.form-group textarea {{
  width: 100%;
  padding: var(--space-md);
  background: var(--color-surface);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: var(--radius-md);
  color: var(--color-text);
  font-family: inherit;
  transition: border-color var(--transition-fast);
}}

.form-group input:focus,
.form-group textarea:focus {{
  outline: none;
  border-color: var(--color-primary);
}}

/* Footer */
.footer {{
  padding: var(--space-xl) 0;
  border-top: 1px solid rgba(255,255,255,0.1);
  text-align: center;
  color: rgba({self._hex_to_rgb(palette.text)}, 0.5);
}}

/* Responsive */
@media (max-width: 768px) {{
  .hero-content {{
    grid-template-columns: 1fr;
    text-align: center;
  }}
  
  .hero-buttons {{
    justify-content: center;
  }}
  
  .nav {{
    display: none; /* Consider mobile menu */
  }}
  
  .features-grid {{
    grid-template-columns: 1fr;
  }}
}}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }}
}}

/* Focus visible */
:focus-visible {{
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}}

/* Screen reader only */
.sr-only {{
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}}"""
    
    def _hex_to_rgb(self, hex_color: str) -> str:
        """Convert hex color to RGB values for rgba()."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"{r}, {g}, {b}"
    
    def _generate_landing_page(self, palette: ColorPalette, typography: TypographySet,
                               features: List[str], requirements: Dict[str, Any]) -> str:
        """Generate HTML for landing page."""
        
        # Build features section
        features_html = ""
        if 'features' in requirements.get('sections', ['features']):
            feature_cards = ""
            for i, feature in enumerate([
                {"title": "Lightning Fast", "desc": "Optimized for speed and performance across all devices", "icon": "⚡"},
                {"title": "Secure by Default", "desc": "Enterprise-grade security built into every component", "icon": "🔒"},
                {"title": "Easy Integration", "desc": "Works seamlessly with your existing tools and workflows", "icon": "🔄"},
            ]):
                feature_cards += f"""
                    <div class="card feature-card">
                        <div class="feature-icon">{feature['icon']}</div>
                        <h3>{feature['title']}</h3>
                        <p>{feature['desc']}</p>
                    </div>
                """
            
            features_section = f"""
        <section class="features">
            <div class="container">
                <div class="section-header">
                    <h2>Why Choose Us</h2>
                    <p>Everything you need to succeed, all in one platform.</p>
                </div>
                <div class="features-grid">
                    {feature_cards}
                </div>
            </div>
        </section>
            """
        else:
            features_section = ""
        
        # Build CTA section
        cta_html = ""
        if 'cta_form' in features or 'newsletter' in features:
            cta_html = f"""
        <section class="cta">
            <div class="container">
                <div class="cta-content">
                    <h2>Ready to get started?</h2>
                    <p style="color: rgba({self._hex_to_rgb(palette.text)}, 0.7); margin-bottom: 2rem;">Join thousands of satisfied customers today.</p>
                    <form style="display: flex; gap: 1rem; flex-wrap: wrap; justify-content: center;">
                        <input type="email" placeholder="Enter your email" style="padding: 0.75rem 1rem; border-radius: 0.5rem; border: 1px solid rgba(255,255,255,0.2); background: var(--color-surface); color: inherit; min-width: 280px;">
                        <button type="submit" class="btn btn-primary">Get Started</button>
                    </form>
                </div>
            </div>
        </section>
            """
        
        # Build pricing section
        pricing_html = ""
        if 'pricing' in features:
            pricing_html = f"""
        <section class="features" id="pricing">
            <div class="container">
                <div class="section-header">
                    <h2>Simple Pricing</h2>
                    <p>Choose the plan that works for you.</p>
                </div>
                <div class="features-grid" style="max-width: 900px; margin: 0 auto;">
                    <div class="card" style="text-align: center;">
                        <h3>Starter</h3>
                        <div style="font-size: 3rem; font-weight: 800; margin: 1rem 0;">$9<span style="font-size: 1rem; font-weight: 400;">/mo</span></div>
                        <ul style="list-style: none; padding: 0; color: rgba({self._hex_to_rgb(palette.text)}, 0.7); line-height: 2;">
                            <li>✓ Up to 5 projects</li>
                            <li>✓ Basic analytics</li>
                            <li>✓ Email support</li>
                        </ul>
                        <button class="btn btn-secondary" style="width: 100%; margin-top: 1.5rem;">Get Started</button>
                    </div>
                    <div class="card" style="text-align: center; border-color: var(--color-primary);">
                        <h3>Pro</h3>
                        <div style="font-size: 3rem; font-weight: 800; margin: 1rem 0; color: var(--color-primary);">$29<span style="font-size: 1rem; font-weight: 400; color: inherit;">/mo</span></div>
                        <ul style="list-style: none; padding: 0; color: rgba({self._hex_to_rgb(palette.text)}, 0.7); line-height: 2;">
                            <li>✓ Unlimited projects</li>
                            <li>✓ Advanced analytics</li>
                            <li>✓ Priority support</li>
                        </ul>
                        <button class="btn btn-primary" style="width: 100%; margin-top: 1.5rem;">Get Started</button>
                    </div>
                    <div class="card" style="text-align: center;">
                        <h3>Enterprise</h3>
                        <div style="font-size: 3rem; font-weight: 800; margin: 1rem 0;">Custom</div>
                        <ul style="list-style: none; padding: 0; color: rgba({self._hex_to_rgb(palette.text)}, 0.7); line-height: 2;">
                            <li>✓ Everything in Pro</li>
                            <li>✓ Dedicated support</li>
                            <li>✓ Custom integrations</li>
                        </ul>
                        <button class="btn btn-secondary" style="width: 100%; margin-top: 1.5rem;">Contact Sales</button>
                    </div>
                </div>
            </div>
        </section>
            """
        
        # Build testimonials section
        testimonials_html = ""
        if 'testimonials' in features:
            testimonials_html = f"""
        <section class="features" style="background: var(--color-surface);">
            <div class="container">
                <div class="section-header">
                    <h2>What Our Customers Say</h2>
                </div>
                <div class="features-grid" style="grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));">
                    <div class="card">
                        <p style="font-style: italic; margin-bottom: 1rem;">"This platform transformed our workflow. Highly recommended!"</p>
                        <div style="display: flex; align-items: center; gap: 1rem;">
                            <div style="width: 48px; height: 48px; background: linear-gradient(135deg, var(--color-primary), var(--color-secondary)); border-radius: 50%;"></div>
                            <div>
                                <div style="font-weight: 600;">Sarah Johnson</div>
                                <div style="font-size: 0.875rem; opacity: 0.7;">CEO, TechStart</div>
                            </div>
                        </div>
                    </div>
                    <div class="card">
                        <p style="font-style: italic; margin-bottom: 1rem;">"Best investment we've made. The ROI was immediate."</p>
                        <div style="display: flex; align-items: center; gap: 1rem;">
                            <div style="width: 48px; height: 48px; background: linear-gradient(135deg, var(--color-secondary), var(--color-accent)); border-radius: 50%;"></div>
                            <div>
                                <div style="font-weight: 600;">Michael Chen</div>
                                <div style="font-size: 0.875rem; opacity: 0.7;">CTO, InnovateCo</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
            """
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Landing Page - {requirements.get('domain', 'Business')}</title>
    {{STYLES}}
</head>
<body>
    <header class="header">
        <div class="container header-content">
            <a href="#" class="logo">Brand<span>.</span></a>
            <nav class="nav">
                <a href="#features">Features</a>
                <a href="#pricing">Pricing</a>
                <a href="#about">About</a>
                <a href="#contact" class="btn btn-primary">Get Started</a>
            </nav>
        </div>
    </header>

    <section class="hero">
        <div class="container">
            <div class="hero-content">
                <div class="hero-text">
                    <h1>Build something <em>amazing</em> today</h1>
                    <p class="hero-description">Powerful tools to help you grow your business faster than ever before. Join thousands of companies already using our platform.</p>
                    <div class="hero-buttons">
                        <a href="#" class="btn btn-primary">Start Free Trial</a>
                        <a href="#" class="btn btn-secondary">Learn More</a>
                    </div>
                </div>
                <div class="hero-visual">
                    <div class="hero-image">[Hero Image Placeholder]</div>
                </div>
            </div>
        </div>
    </section>

    {features_section}
    {pricing_html}
    {testimonials_html}
    {cta_html}

    <footer class="footer">
        <div class="container">
            <p>&copy; 2026 Brand Inc. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>"""
    
    def _generate_dashboard(self, palette: ColorPalette, typography: TypographySet,
                           features: List[str]) -> str:
        """Generate HTML for dashboard."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard</title>
    {{STYLES}}
</head>
<body style="display: grid; grid-template-columns: 260px 1fr; min-height: 100vh;">
    <aside style="background: var(--color-surface); border-right: 1px solid rgba(255,255,255,0.1); padding: 1.5rem;">
        <div class="logo" style="margin-bottom: 2rem;">Dashboard<span>.</span></div>
        <nav style="display: flex; flex-direction: column; gap: 0.5rem;">
            <a href="#" class="btn" style="justify-content: flex-start; background: var(--color-primary); color: white;">Overview</a>
            <a href="#" style="padding: 0.75rem 1rem; color: var(--color-text); text-decoration: none; opacity: 0.8;">Analytics</a>
            <a href="#" style="padding: 0.75rem 1rem; color: var(--color-text); text-decoration: none; opacity: 0.8;">Projects</a>
            <a href="#" style="padding: 0.75rem 1rem; color: var(--color-text); text-decoration: none; opacity: 0.8;">Settings</a>
        </nav>
    </aside>
    <main style="padding: 2rem;">
        <h1>Dashboard Overview</h1>
        <div class="features-grid" style="margin-top: 2rem;">
            <div class="card">
                <div style="color: rgba({self._hex_to_rgb(palette.text)}, 0.7); font-size: 0.875rem;">Total Revenue</div>
                <div style="font-size: 2.5rem; font-weight: 700; margin-top: 0.5rem;">$48,234</div>
            </div>
            <div class="card">
                <div style="color: rgba({self._hex_to_rgb(palette.text)}, 0.7); font-size: 0.875rem;">Active Users</div>
                <div style="font-size: 2.5rem; font-weight: 700; margin-top: 0.5rem;">2,847</div>
            </div>
            <div class="card">
                <div style="color: rgba({self._hex_to_rgb(palette.text)}, 0.7); font-size: 0.875rem;">Conversion Rate</div>
                <div style="font-size: 2.5rem; font-weight: 700; margin-top: 0.5rem; color: var(--color-accent);">12.5%</div>
            </div>
        </div>
    </main>
</body>
</html>"""
    
    def _generate_pricing_page(self, palette: ColorPalette, typography: TypographySet,
                               features: List[str]) -> str:
        """Generate HTML for pricing page."""
        return self._generate_landing_page(palette, typography, ['pricing'], {'sections': []})
    
    def export_design(self, files: Dict[str, str], output_dir: Optional[str] = None) -> str:
        """
        Export design files as zip archive.
        
        Args:
            files: Dict of filename -> content
            output_dir: Output directory (default: workspace)
            
        Returns:
            Path to exported zip file
        """
        if output_dir is None:
            output_dir = os.getcwd()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_path = os.path.join(output_dir, f"design_export_{timestamp}.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for filename, content in files.items():
                zf.writestr(filename, content)
        
        return zip_path


# === AUDIT CHECK: Validate module structure ===
if __name__ == "__main__":
    print("Testing Design Researcher...")
    
    researcher = DesignResearcher()
    
    # Test trend research
    trends = researcher.research_trends("fitness app")
    assert len(trends.trends_2026) > 0, "Should have trends"
    assert len(trends.color_palettes) > 0, "Should have color palettes"
    print(f"✓ Trend research: {len(trends.trends_2026)} trends, {len(trends.color_palettes)} palettes")
    
    # Test mockup generation
    mockup = researcher.generate_mockup({
        "type": "landing_page",
        "domain": "fitness app",
        "colors": ["energy", "motivation"],
        "features": ["cta_form", "pricing", "testimonials"],
        "sections": ["features"],
    }, trends)
    
    assert 'html' in mockup, "Should generate HTML"
    assert 'css' in mockup, "Should generate CSS"
    assert len(mockup['html']) > 1000, "HTML should be substantial"
    print(f"✓ Mockup generation: {len(mockup['html'])} chars HTML, {len(mockup['css'])} chars CSS")
    
    # Check accessibility markers
    assert 'prefers-reduced-motion' in mockup['css'], "Should have accessibility features"
    assert ':focus-visible' in mockup['css'], "Should have focus styles"
    print("✓ Accessibility: prefers-reduced-motion and focus-visible included")
    
    print("\n✅ All audits passed - Design Researcher ready!")