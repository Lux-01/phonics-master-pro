#!/usr/bin/env python3
"""
Autonomous Designer - End-to-end design automation from concept to assets.

Workflow:
1. Design research → Competitor analysis, trends
2. Concept generation → Mood boards, color theory
3. Layout design → Wireframes, responsive grids
4. Asset generation → Icons, illustrations (via code/SVG)
5. Design system → Typography, spacing, component library
6. Interactive prototypes → HTML/CSS mockups
7. Design review → Accessibility, usability checks
8. Export assets → Cut images, CSS, design tokens
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import colorsys
import random


class DesignPhase(Enum):
    """Phases of autonomous design workflow."""
    RESEARCH = "research"
    CONCEPT = "concept"
    LAYOUT = "layout"
    ASSETS = "assets"
    SYSTEM = "system"
    PROTOTYPE = "prototype"
    REVIEW = "review"
    EXPORT = "export"


class DesignStyle(Enum):
    """Common design styles."""
    MINIMAL = "minimal"
    MODERN = "modern"
    BRUTALIST = "brutalist"
    GLASSMORPHISM = "glassmorphism"
    NEUMORPHISM = "neumorphism"
    RETRO = "retro"
    CORPORATE = "corporate"
    PLAYFUL = "playful"


@dataclass
class ColorPalette:
    """Generated color palette."""
    primary: str
    secondary: str
    accent: str
    background: str
    surface: str
    text: str
    text_muted: str
    success: str
    warning: str
    error: str
    info: str
    
    def to_css_vars(self) -> Dict[str, str]:
        """Convert to CSS custom properties."""
        return {
            '--color-primary': self.primary,
            '--color-secondary': self.secondary,
            '--color-accent': self.accent,
            '--color-background': self.background,
            '--color-surface': self.surface,
            '--color-text': self.text,
            '--color-text-muted': self.text_muted,
            '--color-success': self.success,
            '--color-warning': self.warning,
            '--color-error': self.error,
            '--color-info': self.info,
        }


@dataclass
class Typography:
    """Typography system."""
    font_family_primary: str
    font_family_secondary: str
    font_family_mono: str
    sizes: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.sizes:
            self.sizes = {
                "xs": {"size": "0.75rem", "line_height": 1.4, "letter_spacing": "0.05em"},
                "sm": {"size": "0.875rem", "line_height": 1.5, "letter_spacing": "0.01em"},
                "base": {"size": "1rem", "line_height": 1.6, "letter_spacing": "0"},
                "lg": {"size": "1.125rem", "line_height": 1.5, "letter_spacing": "-0.01em"},
                "xl": {"size": "1.25rem", "line_height": 1.4, "letter_spacing": "-0.02em"},
                "2xl": {"size": "1.5rem", "line_height": 1.3, "letter_spacing": "-0.02em"},
                "3xl": {"size": "1.875rem", "line_height": 1.2, "letter_spacing": "-0.03em"},
                "4xl": {"size": "2.25rem", "line_height": 1.1, "letter_spacing": "-0.03em"},
            }


@dataclass
class ComponentDesign:
    """Design for a specific component."""
    name: str
    type: str
    styles: Dict[str, Any]
    variants: List[str]
    states: List[str]
    css_code: str = ""


@dataclass
class DesignProject:
    """Complete design project."""
    project_id: str
    name: str
    description: str
    style: DesignStyle
    palette: Optional[ColorPalette] = None
    typography: Optional[Typography] = None
    components: List[ComponentDesign] = field(default_factory=list)
    screens: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    exported_files: List[str] = field(default_factory=list)


class ColorTheory:
    """Color theory computations."""
    
    @staticmethod
    def hex_to_hsl(hex_color: str) -> Tuple[float, float, float]:
        """Convert hex to HSL."""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        return (h * 360, s * 100, l * 100)
    
    @staticmethod
    def hsl_to_hex(h: float, s: float, l: float) -> str:
        """Convert HSL to hex."""
        r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
    
    @staticmethod
    def generate_palette(base_color: Optional[str] = None, style: DesignStyle = DesignStyle.MODERN) -> ColorPalette:
        """Generate harmonious color palette."""
        if base_color:
            h, s, l = ColorTheory.hex_to_hsl(base_color)
        else:
            # Generate random harmonious base
            h = random.choice([210, 270, 150, 30, 340])  # Blue, Purple, Green, Orange, Pink
            s = 70
            l = 50
        
        # Adjust based on style
        if style == DesignStyle.MINIMAL:
            s = min(s, 30)
            l = 95
        elif style == DesignStyle.BRUTALIST:
            s = 100
            l = 50
        
        primary = ColorTheory.hsl_to_hex(h, s, 50)
        secondary = ColorTheory.hsl_to_hex((h + 30) % 360, s - 10, 45)
        accent = ColorTheory.hsl_to_hex((h + 180) % 360, s, 55)
        
        return ColorPalette(
            primary=primary,
            secondary=secondary,
            accent=accent,
            background="#fafafa" if style != DesignStyle.BRUTALIST else "#ffffff",
            surface="#ffffff",
            text="#1a1a1a",
            text_muted="#666666",
            success="#22c55e",
            warning="#f59e0b",
            error="#ef4444",
            info="#3b82f6"
        )
    
    @staticmethod
    def generate_tints_shades(base_color: str, steps: int = 5) -> Dict[str, List[str]]:
        """Generate tints and shades from base color."""
        h, s, l = ColorTheory.hex_to_hsl(base_color)
        
        tints = []
        shades = []
        
        for i in range(1, steps + 1):
            # Tints (lighter)
            tint_l = min(l + (i * (100 - l) / steps), 95)
            tints.append(ColorTheory.hsl_to_hex(h, max(s - i * 5, 0), tint_l))
            
            # Shades (darker)
            shade_l = max(l - (i * l / steps), 10)
            shades.append(ColorTheory.hsl_to_hex(h, min(s + i * 2, 100), shade_l))
        
        return {"tints": tints, "shades": shades}


class LayoutGenerator:
    """Generate responsive layouts."""
    
    def __init__(self):
        self.logger = logging.getLogger("Omnibot.LayoutGenerator")
    
    def generate_grid(self, columns: int = 12, gap: str = "1rem") -> Dict:
        """Generate CSS grid system."""
        return {
            "grid_template_columns": f"repeat({columns}, 1fr)",
            "gap": gap,
            "breakpoints": {
                "sm": "640px",
                "md": "768px",
                "lg": "1024px",
                "xl": "1280px",
                "2xl": "1536px"
            }
        }
    
    def generate_spacing_scale(self, base: float = 0.25) -> Dict[str, str]:
        """Generate spacing scale in rem."""
        scale = {}
        multipliers = [0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96]
        names = ["0", "1", "2", "3", "4", "5", "6", "8", "10", "12", "16", "20", "24", "32", "40", "48", "64", "80", "96"]
        
        for name, mult in zip(names, multipliers):
            scale[name] = f"{base * mult}rem"
        
        return scale
    
    def generate_shadows(self, elevation: int = 5) -> Dict[str, str]:
        """Generate shadow scale."""
        shadows = {
            "none": "none",
            "sm": "0 1px 2px 0 rgb(0 0 0 / 0.05)",
            "DEFAULT": "0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)",
            "md": "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)",
            "lg": "0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)",
            "xl": "0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)",
        }
        return shadows


class CodeGenerator:
    """Generate HTML/CSS from designs."""
    
    def generate_css_variables(self, palette: ColorPalette, typography: Typography,
                            spacing: Dict[str, str], shadows: Dict[str, str]) -> str:
        """Generate CSS custom properties."""
        css = ":root {\n"
        
        # Color variables
        for name, value in palette.to_css_vars().items():
            css += f"  {name}: {value};\n"
        
        # Typography variables
        css += "\n  /* Typography */\n"
        css += f"  --font-primary: {typography.font_family_primary};\n"
        css += f"  --font-secondary: {typography.font_family_secondary};\n"
        css += f"  --font-mono: {typography.font_family_mono};\n"
        
        for size_name, props in typography.sizes.items():
            css += f"  --text-{size_name}: {props['size']};\n"
            css += f"  --leading-{size_name}: {props['line_height']};\n"
        
        # Spacing variables
        css += "\n  /* Spacing */\n"
        for name, value in spacing.items():
            css += f"  --space-{name}: {value};\n"
        
        # Shadow variables
        css += "\n  /* Shadows */\n"
        for name, value in shadows.items():
            css += f"  --shadow-{name}: {value};\n"
        
        css += "}\n"
        return css
    
    def generate_component_css(self, component: ComponentDesign) -> str:
        """Generate CSS for a component."""
        css = f"/* {component.name} */\n"
        css += f".{component.name} {{\n"
        
        for prop, value in component.styles.items():
            css_prop = prop.replace('_', '-')
            css += f"  {css_prop}: {value};\n"
        
        css += "}\n"
        
        # Generate variants
        for variant in component.variants:
            css += f"\n.{component.name}--{variant} {{\n"
            css += f"  /* Variant: {variant} */\n"
            css += "}\n"
        
        # Generate states
        for state in component.states:
            css += f"\n.{component.name}:{state} {{\n"
            css += f"  /* State: {state} */\n"
            css += "}\n"
        
        return css
    
    def generate_html_mockup(self, screen_name: str, components: List[str],
                            palette: ColorPalette) -> str:
        """Generate HTML mockup."""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{screen_name}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>{screen_name}</h1>
        </header>
        <main class="main-content">
"""
        
        for component in components:
            html += f"            <div class='{component}'></div>\n"
        
        html += """        </main>
        <footer class="footer">
            <p>Generated by Omnibot Designer</p>
        </footer>
    </div>
</body>
</html>"""
        
        return html


class AutonomousDesigner:
    """
    Autonomous design system - from concept to code.
    """
    
    def __init__(self, omnibot=None, output_dir: Optional[str] = None):
        self.logger = logging.getLogger("Omnibot.AutonomousDesigner")
        self.omnibot = omnibot
        
        # Sub-components
        self.color_theory = ColorTheory()
        self.layout_generator = LayoutGenerator()
        self.code_generator = CodeGenerator()
        
        # Storage
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).parent / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Active projects
        self.projects: Dict[str, DesignProject] = {}
        
        self.logger.info("AutonomousDesigner initialized")
    
    def create_project(self, name: str, description: str,
                     style: DesignStyle = DesignStyle.MODERN,
                     base_color: Optional[str] = None) -> DesignProject:
        """
        Create a new design project.
        
        Args:
            name: Project name
            description: Project description
            style: Design style to use
            base_color: Optional brand color
            
        Returns:
            DesignProject
        """
        self.logger.info(f"Creating design project: {name}")
        
        project_id = f"design_{datetime.now().timestamp()}"
        
        # Generate color palette
        palette = self.color_theory.generate_palette(base_color, style)
        
        # Generate typography
        typography = Typography(
            font_family_primary="Inter, system-ui, sans-serif",
            font_family_secondary="Georgia, serif",
            font_family_mono="Fira Code, monospace"
        )
        
        project = DesignProject(
            project_id=project_id,
            name=name,
            description=description,
            style=style,
            palette=palette,
            typography=typography
        )
        
        self.projects[project_id] = project
        
        return project
    
    def generate_design_system(self, project_id: str) -> Dict[str, Any]:
        """
        Generate complete design system.
        
        Args:
            project_id: Project identifier
            
        Returns:
            Design system specifications
        """
        project = self.projects.get(project_id)
        if not project:
            return {"error": "Project not found"}
        
        self.logger.info(f"Generating design system for {project.name}")
        
        # Generate spacing
        spacing = self.layout_generator.generate_spacing_scale()
        
        # Generate shadows
        shadows = self.layout_generator.generate_shadows()
        
        # Generate common components
        components = self._generate_common_components(project.palette)
        project.components = components
        
        design_system = {
            "project": project.name,
            "style": project.style.value,
            "colors": project.palette,
            "typography": project.typography,
            "spacing": spacing,
            "shadows": shadows,
            "components": len(components),
            "css_variables": self.code_generator.generate_css_variables(
                project.palette, project.typography, spacing, shadows
            )
        }
        
        return design_system
    
    def _generate_common_components(self, palette: ColorPalette) -> List[ComponentDesign]:
        """Generate common UI components."""
        components = []
        
        # Button component
        components.append(ComponentDesign(
            name="btn",
            type="button",
            styles={
                "display": "inline-flex",
                "align_items": "center",
                "justify_content": "center",
                "padding": "0.75rem 1.5rem",
                "background_color": palette.primary,
                "color": "#ffffff",
                "border_radius": "0.5rem",
                "font_weight": "500",
                "border": "none",
                "cursor": "pointer",
                "transition": "all 150ms ease"
            },
            variants=["primary", "secondary", "ghost"],
            states=["hover", "focus", "active", "disabled"]
        ))
        
        # Card component
        components.append(ComponentDesign(
            name="card",
            type="card",
            styles={
                "background_color": palette.surface,
                "border_radius": "0.75rem",
                "padding": "1.5rem",
                "box_shadow": "0 1px 3px rgba(0,0,0,0.1)"
            },
            variants=["default", "outlined", "elevated"],
            states=["hover"]
        ))
        
        # Input component
        components.append(ComponentDesign(
            name="input",
            type="input",
            styles={
                "display": "block",
                "width": "100%",
                "padding": "0.75rem 1rem",
                "border": f"1px solid {palette.text_muted}",
                "border_radius": "0.5rem",
                "background_color": palette.background,
                "color": palette.text
            },
            variants=["default", "error", "success"],
            states=["focus", "disabled", "placeholder"]
        ))
        
        return components
    
    def generate_screen(self, project_id: str, screen_name: str,
                       components: List[str]) -> str:
        """
        Generate HTML for a screen.
        
        Args:
            project_id: Project identifier
            screen_name: Screen name (e.g., 'homepage', 'dashboard')
            components: List of component names to include
            
        Returns:
            Path to generated HTML file
        """
        project = self.projects.get(project_id)
        if not project:
            return ""
        
        # Generate HTML
        html_content = self.code_generator.generate_html_mockup(
            screen_name, components, project.palette
        )
        
        # Save file
        output_path = self.output_dir / project_id / f"{screen_name}.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html_content)
        
        # Generate CSS
        css_content = self.code_generator.generate_css_variables(
            project.palette, project.typography,
            self.layout_generator.generate_spacing_scale(),
            self.layout_generator.generate_shadows()
        )
        
        for component in project.components:
            css_content += "\n\n" + self.code_generator.generate_component_css(component)
        
        css_path = output_path.parent / "styles.css"
        css_path.write_text(css_content)
        
        project.screens[screen_name] = str(output_path)
        
        return str(output_path)
    
    def export_project(self, project_id: str, format: str = "css") -> Dict:
        """
        Export design project to various formats.
        
        Args:
            project_id: Project identifier
            format: Export format (css, scss, json)
            
        Returns:
            Export information
        """
        project = self.projects.get(project_id)
        if not project:
            return {"error": "Project not found"}
        
        export_dir = self.output_dir / project_id / "export"
        export_dir.mkdir(parents=True, exist_ok=True)
        
        exported_files = []
        
        if format in ("css", "scss"):
            # Export CSS
            css_path = export_dir / f"{format}_variables.{format}"
            spacing = self.layout_generator.generate_spacing_scale()
            shadows = self.layout_generator.generate_shadows()
            css = self.code_generator.generate_css_variables(
                project.palette, project.typography, spacing, shadows
            )
            css_path.write_text(css)
            exported_files.append(str(css_path))
            
            # Export component CSS
            components_css = ""
            for component in project.components:
                components_css += self.code_generator.generate_component_css(component) + "\n\n"
            
            components_path = export_dir / f"components.{format}"
            components_path.write_text(components_css)
            exported_files.append(str(components_path))
        
        elif format == "json":
            # Export as JSON tokens
            tokens = {
                "colors": project.palette.__dict__,
                "typography": project.typography.__dict__,
                "spacing": self.layout_generator.generate_spacing_scale(),
                "shadows": self.layout_generator.generate_shadows()
            }
            
            json_path = export_dir / "design_tokens.json"
            json_path.write_text(json.dumps(tokens, indent=2))
            exported_files.append(str(json_path))
        
        project.exported_files = exported_files
        
        return {
            "project": project.name,
            "format": format,
            "files": exported_files,
            "export_dir": str(export_dir)
        }
    
    def check_accessibility(self, project_id: str) -> Dict:
        """
        Check design for accessibility issues.
        
        Args:
            project_id: Project identifier
            
        Returns:
            Accessibility report
        """
        project = self.projects.get(project_id)
        if not project:
            return {"error": "Project not found"}
        
        issues = []
        
        # Check contrast
        def luminance(hex_color: str) -> float:
            hex_color = hex_color.lstrip('#')
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            
            # Apply gamma correction
            r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
            g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
            b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
            
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        def contrast_ratio(color1: str, color2: str) -> float:
            l1 = luminance(color1) + 0.05
            l2 = luminance(color2) + 0.05
            return max(l1, l2) / min(l1, l2)
        
        # Check primary text on background
        text_bg_ratio = contrast_ratio(project.palette.text, project.palette.background)
        if text_bg_ratio < 7:
            issues.append(f"Text/Background contrast: {text_bg_ratio:.2f}:1 (should be >= 7:1 for AAA)")
        
        # Check primary button
        btn_bg_ratio = contrast_ratio("#ffffff", project.palette.primary)
        if btn_bg_ratio < 4.5:
            issues.append(f"Button text contrast: {btn_bg_ratio:.2f}:1 (should be >= 4.5:1)")
        
        return {
            "project": project.name,
            "contrast_checks": 2,
            "issues_found": issues,
            "passed": len(issues) == 0
        }
    
    def get_project_summary(self, project_id: str) -> str:
        """Get human-readable project summary."""
        project = self.projects.get(project_id)
        if not project:
            return "Project not found"
        
        return f"""
🎨 DESIGN PROJECT: {project.name}
{'='*50}

Style: {project.style.value}
Components: {len(project.components)}
Screens: {len(project.screens)}

🎨 COLOR PALETTE
- Primary: {project.palette.primary}
- Secondary: {project.palette.secondary}
- Accent: {project.palette.accent}
- Background: {project.palette.background}

🔤 TYPOGRAPHY
- Primary: {project.typography.font_family_primary}
- Secondary: {project.typography.font_family_secondary}
- Sizes: {', '.join(project.typography.sizes.keys())}

📱 SCREENS
{chr(10).join(f"- {name}" for name in project.screens.keys())}

📁 EXPORTED FILES
{chr(10).join(f"- {f}" for f in project.exported_files) if project.exported_files else "No exports yet"}
"""


# Convenience function for quick design generation
def quick_design(name: str, style: str = "modern", screens: List[str] = None) -> Dict:
    """Quickly generate a design system."""
    designer = AutonomousDesigner()
    
    style_enum = DesignStyle(style.lower()) if style.lower() in [s.value for s in DesignStyle] else DesignStyle.MODERN
    
    project = designer.create_project(name, f"Quick design for {name}", style_enum)
    designer.generate_design_system(project.project_id)
    
    if screens:
        for screen in screens:
            designer.generate_screen(project.project_id, screen, ["btn", "card", "input"])
    
    export_info = designer.export_project(project.project_id, "css")
    
    return {
        "project_id": project.project_id,
        "name": project.name,
        "style": project.style.value,
        "palette": project.palette,
        "screens": list(project.screens.keys()),
        "exports": export_info
    }
