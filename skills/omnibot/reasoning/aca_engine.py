"""
ACA (Analyze, Create, Adjust) Engine.
7-step workflow for every code task.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import re

class ACAEngine:
    """
    Implements the 7-step ACA workflow:
    1. Requirements analysis
    2. Architecture design
    3. Data flow mapping
    4. Edge case identification
    5. Constraint definition
    6. Error handling
    7. Testing strategy
    """
    
    def __init__(self, omnibot):
        self.omnibot = omnibot
    
    def run_workflow(self, requirements: str,
                     data_flow: Optional[str] = None,
                     constraints: Optional[List[str]] = None,
                     auto_run: bool = True) -> Dict:
        """
        Run the complete 7-step ACA workflow.
        
        Args:
            requirements: Task requirements
            data_flow: Optional data flow description
            constraints: Optional constraints
            auto_run: Automatically execute the workflow
            
        Returns:
            Complete ACA analysis
        """
        workflow = {
            "started_at": datetime.now().isoformat(),
            "requirements": requirements,
            "steps": {}
        }
        
        # Step 1: Requirements Analysis
        workflow["steps"]["requirements_analysis"] = self._analyze_requirements(requirements)
        
        # Step 2: Architecture Design
        workflow["steps"]["architecture"] = self._design_architecture(
            workflow["steps"]["requirements_analysis"]
        )
        
        # Step 3: Data Flow
        workflow["steps"]["data_flow"] = self._map_data_flow(
            data_flow or self._infer_data_flow(requirements)
        )
        
        # Step 4: Edge Cases
        workflow["steps"]["edge_cases"] = self._identify_edge_cases(
            workflow["steps"]["requirements_analysis"],
            workflow["steps"]["data_flow"]
        )
        
        # Step 5: Constraints
        workflow["steps"]["constraints"] = self._define_constraints(
            constraints or [],
            workflow["steps"]["requirements_analysis"]
        )
        
        # Step 6: Error Handling
        workflow["steps"]["error_handling"] = self._plan_error_handling(
            workflow["steps"]["edge_cases"],
            workflow["steps"]["data_flow"]
        )
        
        # Step 7: Testing
        workflow["steps"]["testing"] = self._design_testing(
            workflow["steps"],
            requirements
        )
        
        workflow["completed_at"] = datetime.now().isoformat()
        
        # Generate code if requested
        if auto_run:
            workflow["generated_code"] = self._generate_implementation(workflow)
        
        return workflow
    
    def _analyze_requirements(self, requirements: str) -> Dict:
        """Step 1: Analyze and decompose requirements."""
        analysis = {
            "raw": requirements,
            "type": self._classify_requirement_type(requirements),
            "components": [],
            "inputs": [],
            "outputs": [],
            "functions": []
        }
        
        # Extract components
        component_patterns = [
            r"(?:create|build|make|implement)\s+(?:a|an)?\s*(\w+)",
            r"(\w+)\s+(?:system|app|script|module|function|class)",
            r"(?:for|to)\s+(\w+)"
        ]
        
        for pattern in component_patterns:
            matches = re.findall(pattern, requirements.lower())
            analysis["components"].extend(matches)
        
        # Extract functions/actions
        action_patterns = [
            r"(?:need|should|must)\s+(\w+)",
            r"(?:that|which)\s+(\w+)s"
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, requirements.lower())
            analysis["functions"].extend(matches)
        
        # Identify inputs/outputs
        input_keywords = ["input", "receive", "get", "take", "accept"]
        output_keywords = ["output", "return", "produce", "generate", "create"]
        
        for kw in input_keywords:
            if kw in requirements.lower():
                analysis["inputs"].append(f"Detected: {kw}")
        
        for kw in output_keywords:
            if kw in requirements.lower():
                analysis["outputs"].append(f"Detected: {kw}")
        
        # Deduplicate
        analysis["components"] = list(set(analysis["components"]))
        analysis["functions"] = list(set(analysis["functions"]))
        
        return analysis
    
    def _design_architecture(self, requirements_analysis: Dict) -> Dict:
        """Step 2: Design architecture based on requirements."""
        components = requirements_analysis.get("components", [])
        req_type = requirements_analysis.get("type", "generic")
        
        architecture = {
            "pattern": "unknown",
            "layers": [],
            "modules": [],
            "interfaces": []
        }
        
        # Determine pattern
        if any(c in ["api", "endpoint", "service"] for c in components):
            architecture["pattern"] = "api_service"
            architecture["layers"] = ["routes", "handlers", "services", "data"]
        elif any(c in ["ui", "interface", "widget", "component"] for c in components):
            architecture["pattern"] = "ui_component"
            architecture["layers"] = ["presentation", "state", "logic", "data"]
        elif any(c in ["script", "tool", "utility"] for c in components):
            architecture["pattern"] = "cli_tool"
            architecture["layers"] = ["cli", "logic", "output"]
        elif any(c in ["agent", "bot", "automation"] for c in components):
            architecture["pattern"] = "agent_system"
            architecture["layers"] = ["input", "orchestration", "execution", "output"]
        else:
            architecture["pattern"] = "modular"
            architecture["layers"] = ["interface", "core", "data"]
        
        # Create modules
        for component in components[:3]:  # Limit to top 3
            architecture["modules"].append({
                "name": component,
                "responsibility": f"Handle {component} related logic",
                "dependencies": []
            })
        
        # Define interfaces
        architecture["interfaces"] = [
            {
                "name": "primary_input",
                "type": "function_call",
                "parameters": requirements_analysis.get("inputs", [])
            },
            {
                "name": "primary_output",
                "type": "return_value",
                "format": requirements_analysis.get("outputs", [])
            }
        ]
        
        return architecture
    
    def _map_data_flow(self, data_flow_desc: str) -> Dict:
        """Step 3: Map data flow through the system."""
        if not data_flow_desc:
            data_flow_desc = "Input → Process → Output"
        
        # Parse flow steps
        steps = []
        flow_parts = re.split(r'[→\-\>]+', data_flow_desc)
        
        for i, part in enumerate(flow_parts):
            step_name = part.strip()
            steps.append({
                "step": i + 1,
                "name": step_name,
                "operation": f"Process {step_name.lower()}",
                "data_transform": "unknown"
            })
        
        return {
            "description": data_flow_desc,
            "steps": steps,
            "entry_point": steps[0]["name"] if steps else "unknown",
            "exit_points": [steps[-1]["name"]] if steps else ["unknown"],
            "validation_points": [s["name"] for s in steps[1:-1]] if len(steps) > 2 else []
        }
    
    def _identify_edge_cases(self, requirements: Dict, data_flow: Dict) -> List[Dict]:
        """Step 4: Identify edge cases and boundary conditions."""
        edge_cases = []
        
        # Standard edge cases for any system
        standard_cases = [
            {
                "category": "input",
                "case": "empty_input",
                "description": "No input provided",
                "risk": "medium",
                "mitigation": "Validate input before processing"
            },
            {
                "category": "input",
                "case": "invalid_format",
                "description": "Input in unexpected format",
                "risk": "medium",
                "mitigation": "Add input validation and type checking"
            },
            {
                "category": "volume",
                "case": "large_input",
                "description": "Input exceeds expected size",
                "risk": "high",
                "mitigation": "Implement size limits and pagination"
            },
            {
                "category": "dependency",
                "case": "external_failure",
                "description": "External service unavailable",
                "risk": "high",
                "mitigation": "Add retry logic and graceful degradation"
            },
            {
                "category": "concurrency",
                "case": "race_condition",
                "description": "Multiple simultaneous requests",
                "risk": "medium",
                "mitigation": "Implement proper locking/queuing"
            },
            {
                "category": "state",
                "case": "partial_failure",
                "description": "Operation partially completes",
                "risk": "high",
                "mitigation": "Implement transactions or rollback capability"
            }
        ]
        
        edge_cases.extend(standard_cases)
        
        # Add specific cases based on requirements
        components = requirements.get("components", [])
        for comp in components:
            edge_cases.append({
                "category": "component_specific",
                "case": f"{comp}_not_found",
                "description": f"Required {comp} does not exist",
                "risk": "medium",
                "mitigation": f"Check for {comp} existence before use"
            })
        
        return edge_cases
    
    def _define_constraints(self, constraints: List[str], 
                           requirements: Dict) -> Dict:
        """Step 5: Define constraints and limitations."""
        all_constraints = {
            "explicit": constraints,
            "inferred": [],
            "technical": [],
            "business": [],
            "performance": []
        }
        
        # Infer constraints from requirements
        req_lower = requirements.get("raw", "").lower()
        
        if "fast" in req_lower or "performance" in req_lower:
            all_constraints["inferred"].append("Must meet performance requirements")
            all_constraints["performance"].append("Response time < 100ms")
        
        if "secure" in req_lower or "private" in req_lower:
            all_constraints["technical"].append("Must handle sensitive data securely")
            all_constraints["technical"].append("Input validation required")
        
        if "web" in req_lower or "online" in req_lower:
            all_constraints["technical"].append("Must handle network failures")
        
        if "many" in req_lower or "scale" in req_lower:
            all_constraints["performance"].append("Must handle load gracefully")
            all_constraints["performance"].append("Memory usage should be bounded")
        
        # Standard constraints
        all_constraints["technical"].extend([
            "Code must be maintainable",
            "Follow existing project conventions",
            "Include error handling"
        ])
        
        return all_constraints
    
    def _plan_error_handling(self, edge_cases: List[Dict],
                            data_flow: Dict) -> Dict:
        """Step 6: Plan error handling strategy."""
        error_handling = {
            "strategy": "exception_based",
            "error_types": {},
            "recovery_actions": {},
            "logging": {}
        }
        
        # Group edge cases by risk
        for case in edge_cases:
            risk = case.get("risk", "unknown")
            if risk not in error_handling["error_types"]:
                error_handling["error_types"][risk] = []
            error_handling["error_types"][risk].append(case)
        
        # Define recovery strategies
        error_handling["recovery_actions"] = {
            "low": "Log and continue",
            "medium": "Retry with backoff, then fail gracefully",
            "high": "Immediate halt with detailed error message"
        }
        
        # Logging strategy
        error_handling["logging"] = {
            "level": "INFO",
            "include": ["timestamp", "operation", "error_message", "stack_trace"],
            "sensitive_data": "Must be redacted"
        }
        
        return error_handling
    
    def _design_testing(self, all_steps: Dict, requirements: str) -> Dict:
        """Step 7: Design testing strategy."""
        testing = {
            "levels": [],
            "coverage_targets": {},
            "test_cases": []
        }
        
        # Unit tests
        modules = all_steps.get("architecture", {}).get("modules", [])
        for mod in modules:
            testing["test_cases"].append({
                "type": "unit",
                "target": mod.get("name"),
                "description": f"Test {mod.get('name')} functionality",
                "assertions": ["Expected output for valid input",
                             "Proper error for invalid input"]
            })
        
        # Integration tests
        steps = all_steps.get("data_flow", {}).get("steps", [])
        if len(steps) > 1:
            testing["test_cases"].append({
                "type": "integration",
                "target": "full_flow",
                "description": "Test complete data flow",
                "assertions": ["End-to-end functionality",
                             "Data integrity maintained"]
            })
        
        # Edge case tests
        edge_cases = all_steps.get("edge_cases", [])
        for case in edge_cases[:3]:  # Test top 3 edge cases
            testing["test_cases"].append({
                "type": "edge_case",
                "target": case.get("case"),
                "description": f"Test {case.get('description')}",
                "assertions": [case.get("mitigation", "Handle gracefully")]
            })
        
        # Coverage targets
        testing["coverage_targets"] = {
            "line_coverage": 80,
            "branch_coverage": 70,
            "edge_case_coverage": 100
        }
        
        return testing
    
    def _infer_data_flow(self, requirements: str) -> str:
        """Infer data flow from requirements."""
        # Look for common patterns
        if "process" in requirements.lower():
            return "Input → Process → Output"
        elif "filter" in requirements.lower():
            return "Raw Input → Filter → Validated Output"
        elif "transform" in requirements.lower():
            return "Source → Transform → Target"
        else:
            return "Request → Handle → Response"
    
    def _classify_requirement_type(self, requirements: str) -> str:
        """Classify the type of requirement."""
        req_lower = requirements.lower()
        
        if any(word in req_lower for word in ["api", "endpoint", "service"]):
            return "api_service"
        elif any(word in req_lower for word in ["interface", "ui", "widget", "component"]):
            return "ui_component"
        elif any(word in req_lower for word in ["script", "tool", "automation"]):
            return "automation_tool"
        elif any(word in req_lower for word in ["agent", "bot", "ai"]):
            return "ai_agent"
        else:
            return "utility_function"
    
    def _generate_implementation(self, workflow: Dict) -> str:
        """Generate code based on ACA workflow."""
        # This is a simplified code generator
        # In practice, this would use an LLM or rule-based system
        
        architecture = workflow["steps"].get("architecture", {})
        modules = architecture.get("modules", [])
        
        code_lines = ["# Generated based on ACA workflow",
                     "# Pattern: {}".format(architecture.get("pattern", "modular")),
                     ""]
        
        # Add imports
        code_lines.extend([
            "from typing import Dict, List, Optional, Any",
            "import logging",
            ""
        ])
        
        # Add main class/function
        if modules:
            main_name = modules[0].get("name", "main").title()
            code_lines.extend([
                f"class {main_name}:",
                '    """',
                f'    {main_name} module based on ACA analysis.',
                '    """',
                "",
                "    def __init__(self):",
                f'        self.logger = logging.getLogger("{main_name}")',
                "",
                "    def process(self, data: Any) -> Any:",
                '        """Process input data."""',
                "        try:",
                "            # Validate input",
                "            if not data:",
                "                raise ValueError('Empty input')",
                "",
                "            # Process",
                "            result = data  # TODO: implement",
                "",
                "            return result",
                "        except Exception as e:",
                '            self.logger.error(f"Processing error: {e}")',
                "            raise"
            ])
        
        return '\n'.join(code_lines)