#!/usr/bin/env python3
"""
Product Development Template Generator
Quickly scaffold new products with proper structure
"""

import os
import json
from datetime import datetime
from pathlib import Path

class ProductTemplate:
    """Template for new product development"""
    
    TEMPLATES = {
        "trading_bot": {
            "description": "Automated trading bot",
            "files": [
                ("main.py", "trading_bot_main.py.template"),
                ("config.json", "config.json.template"),
                ("strategy.py", "strategy.py.template"),
                ("README.md", "trading_readme.template"),
            ],
            "dirs": ["logs", "data", "tests"]
        },
        "scanner": {
            "description": "Market/data scanner",
            "files": [
                ("scanner.py", "scanner_main.py.template"),
                ("filters.py", "filters.py.template"),
                ("alerts.py", "alerts.py.template"),
                ("README.md", "scanner_readme.template"),
            ],
            "dirs": ["data", "logs", "results"]
        },
        "automation": {
            "description": "Workflow automation",
            "files": [
                ("workflow.py", "workflow_main.py.template"),
                ("tasks.py", "tasks.py.template"),
                ("scheduler.py", "scheduler.py.template"),
                ("README.md", "automation_readme.template"),
            ],
            "dirs": ["logs", "config"]
        },
        "api_service": {
            "description": "API service/wrapper",
            "files": [
                ("api.py", "api_main.py.template"),
                ("routes.py", "routes.py.template"),
                ("models.py", "models.py.template"),
                ("README.md", "api_readme.template"),
            ],
            "dirs": ["logs", "data", "tests"]
        }
    }
    
    def __init__(self, base_path="/home/skux/.openclaw/workspace/products"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.registry_file = self.base_path / ".product_registry.json"
    
    def create_product(self, name, template_type, description=""):
        """Create a new product from template"""
        if template_type not in self.TEMPLATES:
            print(f"❌ Unknown template: {template_type}")
            print(f"Available: {', '.join(self.TEMPLATES.keys())}")
            return False
        
        product_dir = self.base_path / name
        if product_dir.exists():
            print(f"❌ Product '{name}' already exists")
            return False
        
        template = self.TEMPLATES[template_type]
        
        # Create directories
        product_dir.mkdir()
        for dir_name in template["dirs"]:
            (product_dir / dir_name).mkdir()
        
        # Create files from templates
        for filename, template_name in template["files"]:
            content = self.get_template_content(template_name, name, description)
            (product_dir / filename).write_text(content)
        
        # Create project metadata
        metadata = {
            "name": name,
            "type": template_type,
            "description": description,
            "created": datetime.now().isoformat(),
            "status": "initialized",
            "version": "0.1.0"
        }
        (product_dir / "product.json").write_text(json.dumps(metadata, indent=2))
        
        # Register product
        self.register_product(metadata)
        
        print(f"\n✅ Created product: {name}")
        print(f"   Type: {template_type}")
        print(f"   Location: {product_dir}")
        print(f"\nNext steps:")
        print(f"  cd {product_dir}")
        print(f"  # Edit config.json and start building!")
        return True
    
    def get_template_content(self, template_name, product_name, description):
        """Get template content - inline templates for portability"""
        templates = {
            "trading_bot_main.py.template": f'''#!/usr/bin/env python3
"""
{product_name} - Trading Bot
{description}
Created: {datetime.now().strftime("%Y-%m-%d")}
"""

import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('logs/{product_name}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('{product_name}')

class {product_name.replace("_", "").title()}Trader:
    def __init__(self):
        self.config = self.load_config()
        self.running = False
        
    def load_config(self):
        with open('config.json') as f:
            return json.load(f)
    
    def run(self):
        logger.info("Starting {product_name}...")
        self.running = True
        # TODO: Implement trading logic
        pass

if __name__ == "__main__":
    trader = {product_name.replace("_", "").title()}Trader()
    trader.run()
''',
            "config.json.template": f'''{{
  "name": "{product_name}",
  "version": "0.1.0",
  "environment": "paper",
  "trading": {{
    "position_size": 0.01,
    "max_positions": 3,
    "take_profit": 0.15,
    "stop_loss": 0.07
  }},
  "api": {{
    "rpc_url": "",
    "api_key": ""
  }},
  "alerts": {{
    "enabled": true,
    "webhook": ""
  }}
}}''',
            "strategy.py.template": f'''#!/usr/bin/env python3
"""
Strategy module for {product_name}
"""

class Strategy:
    def __init__(self, config):
        self.config = config
    
    def should_enter(self, token_data):
        """Return True if should enter position"""
        # TODO: Implement entry logic
        return False
    
    def should_exit(self, position_data):
        """Return True if should exit position"""
        # TODO: Implement exit logic
        return False
''',
            "trading_readme.template": f'''# {product_name}

{description}

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure `config.json` with your API keys

3. Run:
   ```bash
   python3 main.py
   ```

## Structure

- `main.py` - Entry point
- `strategy.py` - Trading strategy
- `config.json` - Configuration
- `logs/` - Log files
- `data/` - Data storage
- `tests/` - Unit tests

## TODO

- [ ] Implement entry logic
- [ ] Implement exit logic
- [ ] Add risk management
- [ ] Write tests
''',
            "scanner_main.py.template": f'''#!/usr/bin/env python3
"""
{product_name} - Scanner
{description}
"""

import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('{product_name}')

class Scanner:
    def __init__(self):
        self.results = []
    
    def scan(self):
        """Run scan and return results"""
        logger.info("Scanning...")
        # TODO: Implement scanning logic
        return []
    
    def save_results(self, filename=None):
        filename = filename or f"results/scan_{{datetime.now().strftime('%Y%m%d_%H%M')}}.json"
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)

if __name__ == "__main__":
    scanner = Scanner()
    results = scanner.scan()
    scanner.save_results()
''',
            "filters.py.template": f'''#!/usr/bin/env python3
"""
Filters for {product_name}
"""

class Filters:
    @staticmethod
    def min_liquidity(token, min_amount=10000):
        return token.get('liquidity', 0) >= min_amount
    
    @staticmethod
    def min_volume(token, min_amount=5000):
        return token.get('volume24h', 0) >= min_amount
    
    @staticmethod
    def apply_all(token):
        """Apply all filters"""
        checks = [
            Filters.min_liquidity(token),
            Filters.min_volume(token),
        ]
        return all(checks)
''',
            "alerts.py.template": f'''#!/usr/bin/env python3
"""
Alert system for {product_name}
"""

import json
from datetime import datetime

class AlertManager:
    def __init__(self, config):
        self.config = config
    
    def send_alert(self, message, level="info"):
        """Send alert via configured channels"""
        print(f"[{{level.upper()}}] {{message}}")
        # TODO: Implement webhook/email/Telegram
    
    def notify_discovery(self, token):
        """Notify when new token found"""
        self.send_alert(f"New token: {{token.get('symbol', 'Unknown')}}")
''',
            "scanner_readme.template": f'''# {product_name}

{description}

## Usage

```bash
python3 scanner.py
```

## Configuration

Edit filters in `filters.py` to adjust criteria.

## Output

Results saved to `results/` directory.
''',
            "workflow_main.py.template": f'''#!/usr/bin/env python3
"""
{product_name} - Workflow Automation
{description}
"""

from tasks import TaskManager
from scheduler import Scheduler

class Workflow:
    def __init__(self):
        self.tasks = TaskManager()
        self.scheduler = Scheduler()
    
    def run(self):
        """Execute workflow"""
        print("Starting workflow...")
        # TODO: Implement workflow
        pass

if __name__ == "__main__":
    workflow = Workflow()
    workflow.run()
''',
            "tasks.py.template": f'''#!/usr/bin/env python3
"""
Task definitions for {product_name}
"""

class TaskManager:
    def __init__(self):
        self.tasks = []
    
    def add_task(self, name, func, schedule=None):
        self.tasks.append({{
            'name': name,
            'func': func,
            'schedule': schedule
        }})
    
    def run_task(self, name):
        for task in self.tasks:
            if task['name'] == name:
                return task['func']()
        return None
''',
            "scheduler.py.template": f'''#!/usr/bin/env python3
"""
Scheduler for {product_name}
"""

import time
from datetime import datetime

class Scheduler:
    def __init__(self):
        self.jobs = []
    
    def add_job(self, func, interval_seconds):
        self.jobs.append({{
            'func': func,
            'interval': interval_seconds,
            'last_run': None
        }})
    
    def run(self):
        while True:
            now = datetime.now()
            for job in self.jobs:
                if job['last_run'] is None or \
                   (now - job['last_run']).seconds >= job['interval']:
                    job['func']()
                    job['last_run'] = now
            time.sleep(1)
''',
            "automation_readme.template": f'''# {product_name}

{description}

## Running

```bash
python3 workflow.py
```

## Adding Tasks

Edit `tasks.py` to add new tasks.

## Scheduling

Configure schedules in `scheduler.py`.
''',
            "api_main.py.template": f'''#!/usr/bin/env python3
"""
{product_name} - API Service
{description}
"""

from flask import Flask
from routes import setup_routes

app = Flask(__name__)
setup_routes(app)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
''',
            "routes.py.template": f'''#!/usr/bin/env python3
"""
API Routes for {product_name}
"""

from flask import jsonify, request

def setup_routes(app):
    @app.route('/health')
    def health():
        return jsonify({{"status": "ok"}})
    
    @app.route('/api/v1/data', methods=['GET'])
    def get_data():
        # TODO: Implement
        return jsonify([])
    
    @app.route('/api/v1/data', methods=['POST'])
    def post_data():
        data = request.get_json()
        # TODO: Implement
        return jsonify({{"status": "created"}})
''',
            "models.py.template": f'''#!/usr/bin/env python3
"""
Data models for {product_name}
"""

from dataclasses import dataclass
from datetime import datetime

@dataclass
class Item:
    id: str
    name: str
    created_at: datetime
    
    def to_dict(self):
        return {{
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat()
        }}
''',
            "api_readme.template": f'''# {product_name}

{description}

## Running

```bash
python3 api.py
```

## Endpoints

- `GET /health` - Health check
- `GET /api/v1/data` - Get data
- `POST /api/v1/data` - Create data

## Testing

```bash
curl http://localhost:5000/health
```
''',
        }
        
        return templates.get(template_name, f"# Template: {template_name}")
    
    def register_product(self, metadata):
        """Register product in registry"""
        registry = {}
        if self.registry_file.exists():
            with open(self.registry_file) as f:
                registry = json.load(f)
        
        registry[metadata["name"]] = metadata
        
        with open(self.registry_file, 'w') as f:
            json.dump(registry, f, indent=2)
    
    def list_products(self):
        """List all registered products"""
        if not self.registry_file.exists():
            print("No products registered yet")
            return
        
        with open(self.registry_file) as f:
            registry = json.load(f)
        
        print("\n📦 Registered Products:")
        print("-" * 60)
        for name, meta in registry.items():
            status = meta.get("status", "unknown")
            created = meta.get("created", "")[:10]
            print(f"  {name} ({meta['type']}) - {status}")
            print(f"     Created: {created}")
            print(f"     {meta.get('description', 'No description')}")
            print()
    
    def list_templates(self):
        """List available templates"""
        print("\n📋 Available Templates:")
        print("-" * 60)
        for name, info in self.TEMPLATES.items():
            print(f"  {name}")
            print(f"     {info['description']}")
            print(f"     Files: {len(info['files'])}, Dirs: {len(info['dirs'])}")
            print()

if __name__ == "__main__":
    import sys
    
    generator = ProductTemplate()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 product_template.py list")
        print("  python3 product_template.py templates")
        print("  python3 product_template.py create <name> <type> [description]")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "list":
        generator.list_products()
    elif cmd == "templates":
        generator.list_templates()
    elif cmd == "create" and len(sys.argv) >= 4:
        name = sys.argv[2]
        template_type = sys.argv[3]
        description = sys.argv[4] if len(sys.argv) > 4 else ""
        generator.create_product(name, template_type, description)
    else:
        print("Unknown command")
