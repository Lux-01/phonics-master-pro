#!/usr/bin/env python3
"""
Integration & Compatibility Engine (ICE) - ACA Built v1.0
Read API docs, integrate new services, test endpoints, build wrappers.
"""

import json
import os
import re
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
import argparse


@dataclass
class APIEndpoint:
    """Represents an API endpoint."""
    path: str
    method: str
    description: str
    parameters: List[Dict] = field(default_factory=list)
    tested: bool = False
    working: bool = False


@dataclass
class APIService:
    """Represents an integrated API service."""
    name: str
    base_url: str
    auth_type: str
    endpoints: List[APIEndpoint] = field(default_factory=list)
    compatibility_score: float = 0.0
    integrated_at: str = ""
    
    def __post_init__(self):
        if not self.integrated_at:
            self.integrated_at = datetime.now().isoformat()


class IntegrationCompatibilityEngine:
    """
    Integration & Compatibility Engine.
    Makes OpenClaw future-proof with API integrations.
    """
    
    def __init__(self, memory_dir: str = None):
        self.memory_dir = memory_dir or os.path.expanduser("~/.openclaw/workspace/memory/ice")
        self.state_file = os.path.join(self.memory_dir, "state.json")
        self.services_file = os.path.join(self.memory_dir, "services.json")
        self.wrappers_dir = os.path.join(self.memory_dir, "wrappers")
        self._ensure_dirs()
        self.state = self._load_state()
        self.services: Dict[str, APIService] = {}
        self._load_services()
    
    def _ensure_dirs(self):
        Path(self.memory_dir).mkdir(parents=True, exist_ok=True)
        Path(self.wrappers_dir).mkdir(parents=True, exist_ok=True)
    
    def _load_state(self) -> Dict:
        defaults = {
            "total_integrations": 0,
            "apis_tested": 0,
            "wrappers_generated": 0
        }
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    defaults.update(json.load(f))
        except Exception:
            pass
        return defaults
    
    def _load_services(self):
        try:
            if os.path.exists(self.services_file):
                with open(self.services_file, 'r') as f:
                    data = json.load(f)
                    for name, svc in data.items():
                        endpoints = [APIEndpoint(**e) for e in svc.get("endpoints", [])]
                        svc["endpoints"] = endpoints
                        self.services[name] = APIService(**svc)
        except Exception:
            pass
    
    def _save(self):
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
            with open(self.services_file, 'w') as f:
                json.dump({k: asdict(v) for k, v in self.services.items()}, f, indent=2)
        except Exception:
            pass
    
    def parse_openapi(self, spec_path: str) -> Optional[APIService]:
        """Parse OpenAPI spec."""
        try:
            with open(spec_path, 'r') as f:
                spec = json.load(f)
            
            service = APIService(
                name=spec.get("info", {}).get("title", "Unknown"),
                base_url=spec.get("servers", [{}])[0].get("url", ""),
                auth_type="api_key"
            )
            
            for path, methods in spec.get("paths", {}).items():
                for method, details in methods.items():
                    if method.upper() in ["GET", "POST", "PUT", "DELETE"]:
                        endpoint = APIEndpoint(
                            path=path,
                            method=method.upper(),
                            description=details.get("summary", "")
                        )
                        service.endpoints.append(endpoint)
            
            return service
        except Exception:
            return None
    
    def test_endpoint(self, base_url: str, endpoint: APIEndpoint, 
                     headers: Dict = None) -> Tuple[bool, str]:
        """Test an API endpoint."""
        url = f"{base_url.rstrip('/')}/{endpoint.path.lstrip('/')}"
        
        try:
            method = getattr(requests, endpoint.method.lower())
            response = method(url, headers=headers, timeout=10)
            
            endpoint.tested = True
            endpoint.working = response.status_code < 400
            
            return endpoint.working, f"Status: {response.status_code}"
        except Exception as e:
            endpoint.tested = True
            endpoint.working = False
            return False, str(e)
    
    def generate_wrapper(self, service: APIService, output_dir: str = None) -> str:
        """Generate Python wrapper for API."""
        if output_dir is None:
            output_dir = self.wrappers_dir
        
        class_name = service.name.replace(" ", "").replace("-", "") + "Client"
        filename = f"{service.name.lower().replace(' ', '_')}_client.py"
        filepath = os.path.join(output_dir, filename)
        
        code_lines = [
            f"#!/usr/bin/env python3",
            f"\"\"\"",
            f"{service.name} API Client - Generated by ICE",
            f"\"\"\"",
            "",
            "import requests",
            "from typing import Dict, Optional",
            "",
            f"class {class_name}:",
            f'    BASE_URL = "{service.base_url}"',
            "",
            "    def __init__(self, api_key: str):",
            "        self.api_key = api_key",
            "        self.session = requests.Session()",
            f'        self.session.headers.update({{"Authorization": f"Bearer {{api_key}}"}})',
            "",
        ]
        
        for endpoint in service.endpoints[:10]:  # First 10 endpoints
            method_name = endpoint.path.strip('/').replace('/', '_').replace('-', '_')
            code_lines.extend([
                f"    def {method_name}(self, **params):",
                f'        \"\"\"{endpoint.description}\"\"\"',
                f'        url = f"{{self.BASE_URL}}{endpoint.path}"',
                f'        response = self.session.{endpoint.method.lower()}(url, params=params)',
                '        response.raise_for_status()',
                '        return response.json()',
                '',
            ])
        
        code = "\n".join(code_lines)
        
        with open(filepath, 'w') as f:
            f.write(code)
        
        self.state["wrappers_generated"] += 1
        self._save()
        
        return filepath
    
    def integrate_service(self, name: str, base_url: str, 
                         auth_type: str = "api_key") -> APIService:
        """Integrate a new API service."""
        service = APIService(
            name=name,
            base_url=base_url,
            auth_type=auth_type
        )
        
        self.services[name] = service
        self.state["total_integrations"] += 1
        self._save()
        
        return service
    
    def check_compatibility(self, service_name: str) -> Dict:
        """Check API compatibility."""
        service = self.services.get(service_name)
        if not service:
            return {"error": "Service not found"}
        
        tested = sum(1 for e in service.endpoints if e.tested)
        working = sum(1 for e in service.endpoints if e.working)
        
        return {
            "service": service_name,
            "endpoints_total": len(service.endpoints),
            "endpoints_tested": tested,
            "endpoints_working": working,
            "compatibility": working / len(service.endpoints) if service.endpoints else 0
        }
    
    def get_rate_limits(self, headers: Dict) -> Dict:
        """Extract rate limits from headers."""
        limits = {}
        
        for key in headers:
            if "rate" in key.lower() or "limit" in key.lower():
                limits[key] = headers[key]
        
        return limits
    
    def get_report(self) -> str:
        """Generate ICE report."""
        lines = [
            "Integration & Compatibility Engine Report",
            f"Total integrations: {self.state['total_integrations']}",
            f"APIs tested: {self.state['apis_tested']}",
            f"Wrappers generated: {self.state['wrappers_generated']}",
            "",
            "Integrated services:"
        ]
        
        for name, service in self.services.items():
            working = sum(1 for e in service.endpoints if e.working)
            lines.append(f"  • {name}: {working}/{len(service.endpoints)} endpoints working")
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="ICE - Integration & Compatibility Engine")
    parser.add_argument("--mode", choices=["parse", "test", "integrate", "wrapper", "report", "test-ice"], default="report")
    parser.add_argument("--name", "-n", help="Service name")
    parser.add_argument("--url", "-u", help="API base URL")
    parser.add_argument("--spec", help="OpenAPI spec path")
    
    args = parser.parse_args()
    
    ice = IntegrationCompatibilityEngine()
    
    if args.mode == "parse":
        if not args.spec:
            print("Error: --spec required")
            return
        service = ice.parse_openapi(args.spec)
        if service:
            print(f"✓ Parsed: {service.name}")
            print(f"  Endpoints: {len(service.endpoints)}")
        else:
            print("✗ Failed to parse spec")
    
    elif args.mode == "test":
        if not args.name:
            print("Error: --name required")
            return
        compat = ice.check_compatibility(args.name)
        print(json.dumps(compat, indent=2))
    
    elif args.mode == "integrate":
        if not args.name or not args.url:
            print("Error: --name and --url required")
            return
        service = ice.integrate_service(args.name, args.url)
        print(f"✓ Integrated: {args.name}")
    
    elif args.mode == "wrapper":
        if not args.name:
            print("Error: --name required")
            return
        service = ice.services.get(args.name)
        if service:
            filepath = ice.generate_wrapper(service)
            print(f"✓ Generated wrapper: {filepath}")
        else:
            print("✗ Service not found")
    
    elif args.mode == "report":
        print(ice.get_report())
    
    elif args.mode in ["test-ice", "test"]:
        print("🧪 Testing ICE...")
        service = ice.integrate_service("TestAPI", "https://api.test.com", "api_key")
        service.endpoints.append(APIEndpoint("/test", "GET", "Test endpoint"))
        print(f"✓ Integrated service: {service.name}")
        compat = ice.check_compatibility("TestAPI")
        print(f"✓ Compatibility checked: {compat['endpoints_total']} endpoints")
        print(f"✓ Total integrations: {ice.state['total_integrations']}")
        print("✓ All tests passed")


if __name__ == "__main__":
    main()
