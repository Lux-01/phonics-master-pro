#!/usr/bin/env python3
"""
Quick Start Generator - Create new project templates quickly
"""
import argparse
import os
from pathlib import Path

TEMPLATES = {
    "python": {
        "files": {
            "main.py": "#!/usr/bin/env python3\n\ndef main():\n    print('Hello, World!')\n\nif __name__ == '__main__':\n    main()\n",
            "requirements.txt": "# Add dependencies here\n",
            "README.md": "# Project\n\n## Usage\n\n```bash\npython main.py\n```\n"
        }
    },
    "website": {
        "files": {
            "index.html": "<!DOCTYPE html>\n<html>\n<head>\n    <title>My Site</title>\n    <link rel='stylesheet' href='styles.css'>\n</head>\n<body>\n    <h1>Hello!</h1>\n    <script src='script.js'></script>\n</body>\n</html>\n",
            "styles.css": "body { font-family: sans-serif; }\n",
            "script.js": "console.log('Hello!');\n",
            "README.md": "# Website\n\nOpen index.html in browser.\n"
        }
    },
    "script": {
        "files": {
            "script.py": "#!/usr/bin/env python3\n\"\"\"\nDescription of what this script does.\n\"\"\"\n\nimport argparse\n\ndef main():\n    parser = argparse.ArgumentParser()\n    parser.add_argument('--input', '-i', required=True, help='Input file')\n    args = parser.parse_args()\n    \n    print(f'Processing: {args.input}')\n\nif __name__ == '__main__':\n    main()\n",
            "README.md": "# Script\n\n## Usage\n\n```bash\npython script.py --input file.txt\n```\n"
        }
    }
}

def create_project(name, template_type):
    """Create a new project from template"""
    project_dir = Path(name)
    
    if project_dir.exists():
        print(f"Error: {name} already exists")
        return False
    
    project_dir.mkdir()
    template = TEMPLATES.get(template_type, TEMPLATES["python"])
    
    for filename, content in template["files"].items():
        filepath = project_dir / filename
        with open(filepath, 'w') as f:
            f.write(content)
        
        # Make Python files executable
        if filename.endswith('.py'):
            os.chmod(filepath, 0o755)
    
    print(f"✅ Created {template_type} project: {name}/")
    print(f"   Location: {project_dir.absolute()}")
    print("\nFiles created:")
    for f in template["files"].keys():
        print(f"  • {f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Quick project generator")
    parser.add_argument("name", help="Project name")
    parser.add_argument("--type", "-t", choices=["python", "website", "script"],
                       default="python", help="Project template type")
    
    args = parser.parse_args()
    create_project(args.name, args.type)
