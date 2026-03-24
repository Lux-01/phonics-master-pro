#!/usr/bin/env python3
"""
Output Generator Module
Generates polished, formatted CV output.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class OutputGenerator:
    """Generates formatted CV output in multiple formats."""
    
    def __init__(self, template_dir: Optional[Path] = None):
        self.template_dir = template_dir or Path(__file__).parent / 'templates'
        self.template_dir.mkdir(exist_ok=True)
    
    def generate_markdown(self, cv_data: Dict, company_data: Optional[Dict] = None) -> str:
        """
        Generate Markdown format CV.
        
        Args:
            cv_data: Structured CV data
            company_data: Optional company research data
            
        Returns:
            Markdown formatted CV
        """
        lines = []
        
        # Header
        lines.append('# ' + cv_data.get('name', 'Candidate'))
        lines.append('')
        
        # Contact info
        contact = []
        if cv_data.get('email'):
            contact.append(f"📧 {cv_data['email']}")
        if cv_data.get('phone'):
            contact.append(f"📞 {cv_data['phone']}")
        if cv_data.get('linkedin'):
            contact.append(f"🔗 {cv_data['linkedin']}")
        if contact:
            lines.append(' | '.join(contact))
            lines.append('')
        
        # Summary
        if cv_data.get('summary'):
            lines.append('## Professional Summary')
            lines.append('')
            lines.append(cv_data['summary'])
            lines.append('')
        
        # Skills
        if cv_data.get('skills'):
            lines.append('## Skills')
            lines.append('')
            skills = cv_data['skills']
            for i in range(0, len(skills), 5):
                chunk = skills[i:i+5]
                lines.append(', '.join(chunk))
            lines.append('')
        
        # Experience
        if cv_data.get('experience'):
            lines.append('## Professional Experience')
            lines.append('')
            for exp in cv_data['experience']:
                title = exp.get('title', '')
                company = exp.get('company', '')
                duration = exp.get('duration', '')
                
                lines.append(f"### {title}")
                if company:
                    loc = f" at {company}" if company else ""
                    lines.append(f"**{company}{loc}** | {duration}")
                lines.append('')
                
                for desc in exp.get('description', [])[:5]:
                    lines.append(f"- {desc}")
                lines.append('')
        
        # Education
        if cv_data.get('education'):
            lines.append('## Education')
            lines.append('')
            for edu in cv_data['education']:
                if isinstance(edu, dict):
                    degree = edu.get('degree', '')
                    institution = edu.get('institution', '')
                    year = edu.get('year', '')
                    if degree:
                        lines.append(f"- **{degree}**")
                        if institution:
                            lines.append(f"  {institution}")
                        if year:
                            lines.append(f"  {year}")
                else:
                    lines.append(f"- {edu}")
            lines.append('')
        
        # Certifications
        if cv_data.get('certifications'):
            lines.append('## Certifications')
            lines.append('')
            for cert in cv_data['certifications'][:5]:
                lines.append(f"- {cert}")
            lines.append('')
        
        return '\n'.join(lines)
    
    def generate_text(self, cv_data: Dict, optimized_for: Optional[str] = None) -> str:
        """Generate plain text CV optimized for ATS."""
        lines = []
        
        # Name (centered as best as possible in text)
        lines.append(cv_data.get('name', 'CANDIDATE').upper())
        lines.append('=' * 50)
        lines.append('')
        
        # Contact
        if cv_data.get('email'):
            lines.append(f"Email: {cv_data['email']}")
        if cv_data.get('phone'):
            lines.append(f"Phone: {cv_data['phone']}")
        if cv_data.get('linkedin'):
            lines.append(f"LinkedIn: {cv_data['linkedin']}")
        lines.append('')
        
        # Summary
        if cv_data.get('summary'):
            lines.append('PROFESSIONAL SUMMARY')
            lines.append('-' * 30)
            lines.append(cv_data['summary'])
            lines.append('')
        
        # Skills
        if cv_data.get('skills'):
            lines.append('SKILLS')
            lines.append('-' * 30)
            lines.append(', '.join(cv_data['skills'][:15]))
            lines.append('')
        
        # Experience
        if cv_data.get('experience'):
            lines.append('EXPERIENCE')
            lines.append('-' * 30)
            for exp in cv_data['experience']:
                lines.append('')
                title = exp.get('title', '').upper()
                company = exp.get('company', '')
                duration = exp.get('duration', '')
                
                if title:
                    lines.append(title)
                if company:
                    lines.append(f"{company} | {duration}")
                
                for desc in exp.get('description', [])[:3]:
                    lines.append(f"  * {desc}")
            lines.append('')
        
        # Education
        if cv_data.get('education'):
            lines.append('EDUCATION')
            lines.append('-' * 30)
            for edu in cv_data['education']:
                if isinstance(edu, dict):
                    if edu.get('degree'):
                        lines.append(edu['degree'])
                    if edu.get('institution'):
                        lines.append(f"  {edu['institution']}")
                else:
                    lines.append(edu)
            lines.append('')
        
        return '\n'.join(lines)
    
    def generate_html(self, cv_data: Dict) -> str:
        """Generate HTML formatted CV."""
        html = ['<!DOCTYPE html>', '<html>', '<head>',
               '<title>CV - {}</title>'.format(cv_data.get('name', 'Candidate')),
               '<style>',
               'body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }',
               'h1 { border-bottom: 2px solid #333; }',
               'h2 { color: #333; margin-top: 20px; }',
               '.contact { margin: 10px 0; }',
               '.experience-item { margin: 15px 0; }',
               'ul { margin: 5px 0; }',
               '</style>',
               '</head>', '<body>']
        
        # Header
        html.append(f"<h1>{cv_data.get('name', 'Candidate')}</h1>")
        
        # Contact
        contact_parts = []
        if cv_data.get('email'):
            contact_parts.append(f"<a href='mailto:{cv_data['email']}'>{cv_data['email']}</a>")
        if cv_data.get('phone'):
            contact_parts.append(cv_data['phone'])
        if cv_data.get('linkedin'):
            contact_parts.append(f"<a href='{cv_data['linkedin']}'>LinkedIn</a>")
        
        if contact_parts:
            html.append(f"<div class='contact'>{' | '.join(contact_parts)}</div>")
        
        # Summary
        if cv_data.get('summary'):
            html.append('<h2>Professional Summary</h2>')
            html.append(f"<p>{cv_data['summary']}</p>")
        
        # Skills
        if cv_data.get('skills'):
            html.append('<h2>Skills</h2>')
            html.append('<p>' + ', '.join(cv_data['skills']) + '</p>')
        
        # Experience
        if cv_data.get('experience'):
            html.append('<h2>Professional Experience</h2>')
            for exp in cv_data['experience']:
                html.append('<div class="experience-item">')
                title = exp.get('title', '')
                if title:
                    html.append(f"<h3>{title}</h3>")
                company = exp.get('company', '')
                duration = exp.get('duration', '')
                if company or duration:
                    html.append(f"<p><strong>{company}</strong> | {duration}</p>")
                descs = exp.get('description', [])
                if descs:
                    html.append('<ul>')
                    for desc in descs[:3]:
                        html.append(f"<li>{desc}</li>")
                    html.append('</ul>')
                html.append('</div>')
        
        # Education
        if cv_data.get('education'):
            html.append('<h2>Education</h2>')
            html.append('<ul>')
            for edu in cv_data['education']:
                if isinstance(edu, dict):
                    item = edu.get('degree', '')
                    if edu.get('institution'):
                        item += f" - {edu['institution']}"
                    html.append(f"<li>{item}</li>")
                else:
                    html.append(f"<li>{edu}</li>")
            html.append('</ul>')
        
        html.extend(['</body>', '</html>'])
        
        return '\n'.join(html)
    
    def save_all_formats(self, cv_data: Dict, output_dir: Path, name: str = "cv") -> Dict[str, Path]:
        """Save CV in all formats."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        files = {}
        
        # Markdown
        md_path = output_dir / f"{name}.md"
        md_path.write_text(self.generate_markdown(cv_data))
        files['markdown'] = md_path
        
        # Text
        txt_path = output_dir / f"{name}.txt"
        txt_path.write_text(self.generate_text(cv_data))
        files['text'] = txt_path
        
        # HTML
        html_path = output_dir / f"{name}.html"
        html_path.write_text(self.generate_html(cv_data))
        files['html'] = html_path
        
        return files


def main():
    """CLI interface for output generation."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate CV outputs')
    parser.add_argument('--input', '-i', required=True, help='Path to CV analysis JSON')
    parser.add_argument('--output-dir', '-o', default='cv_output', help='Output directory')
    parser.add_argument('--name', '-n', default='cv', help='Output filename prefix')
    args = parser.parse_args()
    
    # Load data
    cv_data = json.loads(Path(args.input).read_text())
    
    # Generate
    generator = OutputGenerator()
    files = generator.save_all_formats(cv_data, args.output_dir, args.name)
    
    print(f"✓ CV generated in all formats:")
    for format_name, path in files.items():
        print(f"  {format_name}: {path}")
    
    return 0


if __name__ == '__main__':
    exit(main())
