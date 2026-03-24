#!/usr/bin/env python3
"""
CEL-Core: Cognitive Enhancement Layer - Orchestrator
Coordinates all cognitive modules for enhanced AI capabilities.

ACA Implementation - Phase 1: Foundation
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import sys

# Add workspace to path
sys.path.insert(0, '/home/skux/.openclaw/workspace')


class CELCore:
    """
    Central orchestrator for Cognitive Enhancement Layer.
    
    Routes queries to appropriate modules,
    coordinates multi-module responses,
    manages execution order,
    aggregates outputs.
    """
    
    def __init__(self):
        self.modules = {}
        self.module_order = [
            'understanding',
            'creativity', 
            'self',
            'transfer',
            'commonsense'
        ]
        self.execution_log = []
        self.performance_metrics = {
            'total_queries': 0,
            'avg_latency_ms': 0,
            'module_usage': {}
        }
        
        # Load modules dynamically
        self._load_modules()
    
    def _load_modules(self):
        """Dynamically load cognitive modules."""
        module_map = {
            'understanding': 'cel_understanding.CELUnderstanding',
            'creativity': 'cel_creativity.CELCreativity',
            'self': 'cel_self.CELSelf',
            'transfer': 'cel_transfer.CELTransfer',
            'commonsense': 'cel_commonsense.CELCommonsense'
        }
        
        for name, module_path in module_map.items():
            try:
                module_parts = module_path.split('.')
                module = __import__(f"skills.cognitive-enhancement-layer.{module_parts[0]}")
                class_ = getattr(module, module_parts[1])
                self.modules[name] = class_()
                print(f"✅ Loaded module: {name}")
            except Exception as e:
                print(f"⚠️ Failed to load {name}: {e}")
                self.modules[name] = None
    
    def analyze_input(self, user_input: str, context: Dict = None) -> Dict[str, Any]:
        """
        Analyze input to determine which modules should process it.
        
        Returns routing decision with confidence scores.
        """
        analysis = {
            'input_type': self._classify_input(user_input),
            'complexity': self._assess_complexity(user_input),
            'domain': self._identify_domain(user_input),
            'recommended_modules': [],
            'confidence': 0.0
        }
        
        # Determine which modules to invoke
        if analysis['complexity'] == 'high':
            analysis['recommended_modules'] = ['understanding', 'self']
        
        if 'create' in user_input.lower() or 'design' in user_input.lower():
            analysis['recommended_modules'].append('creativity')
        
        if analysis['domain'] == 'cross_domain':
            analysis['recommended_modules'].append('transfer')
        
        if self._needs_commonsense(user_input):
            analysis['recommended_modules'].append('commonsense')
        
        # Remove duplicates while preserving order
        seen = set()
        analysis['recommended_modules'] = [
            m for m in analysis['recommended_modules'] 
            if not (m in seen or seen.add(m))
        ]
        
        analysis['confidence'] = min(0.95, 0.5 + 0.1 * len(analysis['recommended_modules']))
        
        return analysis
    
    def _classify_input(self, user_input: str) -> str:
        """Classify the type of input."""
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ['why', 'explain', 'how does']):
            return 'explanatory'
        elif any(word in input_lower for word in ['create', 'design', 'invent']):
            return 'creative'
        elif any(word in input_lower for word in ['what is', 'define', 'describe']):
            return 'descriptive'
        elif any(word in input_lower for word in ['compare', 'analyze', 'evaluate']):
            return 'analytical'
        else:
            return 'general'
    
    def _assess_complexity(self, user_input: str) -> str:
        """Assess complexity of the input."""
        word_count = len(user_input.split())
        question_marks = user_input.count('?')
        
        if word_count > 50 or question_marks > 2:
            return 'high'
        elif word_count > 20 or question_marks > 0:
            return 'medium'
        else:
            return 'low'
    
    def _identify_domain(self, user_input: str) -> str:
        """Identify the domain of the input."""
        domains = {
            'trading': ['trade', 'token', 'price', 'market', 'solana'],
            'coding': ['code', 'program', 'script', 'function', 'api'],
            'research': ['research', 'analyze', 'study', 'investigate'],
            'design': ['design', 'create', 'build', 'architect']
        }
        
        input_lower = user_input.lower()
        detected = []
        
        for domain, keywords in domains.items():
            if any(kw in input_lower for kw in keywords):
                detected.append(domain)
        
        if len(detected) > 1:
            return 'cross_domain'
        elif detected:
            return detected[0]
        else:
            return 'general'
    
    def _needs_commonsense(self, user_input: str) -> bool:
        """Determine if input requires commonsense reasoning."""
        commonsense_indicators = [
            'should i', 'is it', 'would', 'could', 'might',
            'probably', 'likely', 'usually', 'normally'
        ]
        
        input_lower = user_input.lower()
        return any(indicator in input_lower for indicator in commonsense_indicators)
    
    def process(self, user_input: str, context: Dict = None, 
                modules: List[str] = None) -> Dict[str, Any]:
        """
        Main entry point for CEL processing.
        
        Args:
            user_input: The user's query or command
            context: Optional context (conversation history, etc.)
            modules: Specific modules to use (auto-detect if None)
        
        Returns:
            Enhanced response with cognitive processing
        """
        start_time = time.time()
        self.performance_metrics['total_queries'] += 1
        
        # Step 1: Analyze input
        analysis = self.analyze_input(user_input, context)
        
        # Step 2: Determine modules to use
        if modules is None:
            modules = analysis['recommended_modules']
        
        # Step 3: Execute modules
        module_outputs = {}
        for module_name in modules:
            if module_name in self.modules and self.modules[module_name]:
                try:
                    module_start = time.time()
                    output = self.modules[module_name].process(
                        user_input, context, analysis
                    )
                    module_outputs[module_name] = {
                        'output': output,
                        'latency_ms': (time.time() - module_start) * 1000
                    }
                    
                    # Track usage
                    if module_name not in self.performance_metrics['module_usage']:
                        self.performance_metrics['module_usage'][module_name] = 0
                    self.performance_metrics['module_usage'][module_name] += 1
                    
                except Exception as e:
                    module_outputs[module_name] = {
                        'output': None,
                        'error': str(e),
                        'latency_ms': (time.time() - module_start) * 1000
                    }
        
        # Step 4: Aggregate outputs
        aggregated = self._aggregate_outputs(module_outputs, user_input)
        
        # Step 5: Update metrics
        total_latency = (time.time() - start_time) * 1000
        self._update_latency_metrics(total_latency)
        
        # Step 6: Log execution
        self._log_execution(user_input, modules, module_outputs, total_latency)
        
        return {
            'original_input': user_input,
            'analysis': analysis,
            'module_outputs': module_outputs,
            'aggregated_response': aggregated,
            'latency_ms': total_latency,
            'modules_used': modules
        }
    
    def _aggregate_outputs(self, module_outputs: Dict, original_input: str) -> str:
        """Aggregate outputs from multiple modules into coherent response."""
        parts = []
        
        # Understanding module provides explanation
        if 'understanding' in module_outputs and module_outputs['understanding'].get('output'):
            parts.append(module_outputs['understanding']['output'])
        
        # Creativity module provides novel ideas
        if 'creativity' in module_outputs and module_outputs['creativity'].get('output'):
            parts.append(f"\n💡 Creative insight: {module_outputs['creativity']['output']}")
        
        # Self module provides reasoning trace
        if 'self' in module_outputs and module_outputs['self'].get('output'):
            parts.append(f"\n🧠 Reasoning: {module_outputs['self']['output']}")
        
        # Transfer module provides cross-domain application
        if 'transfer' in module_outputs and module_outputs['transfer'].get('output'):
            parts.append(f"\n🔄 Cross-domain insight: {module_outputs['transfer']['output']}")
        
        # Commonsense module provides contextual grounding
        if 'commonsense' in module_outputs and module_outputs['commonsense'].get('output'):
            parts.append(f"\n🌍 Context: {module_outputs['commonsense']['output']}")
        
        return '\n'.join(parts) if parts else original_input
    
    def _update_latency_metrics(self, latency_ms: float):
        """Update running average latency."""
        n = self.performance_metrics['total_queries']
        current_avg = self.performance_metrics['avg_latency_ms']
        new_avg = (current_avg * (n - 1) + latency_ms) / n
        self.performance_metrics['avg_latency_ms'] = new_avg
    
    def _log_execution(self, user_input: str, modules: List[str], 
                       outputs: Dict, latency_ms: float):
        """Log execution for learning."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'input': user_input[:100],  # Truncate for privacy
            'modules': modules,
            'success': all(not o.get('error') for o in outputs.values()),
            'latency_ms': latency_ms
        }
        self.execution_log.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.execution_log) > 1000:
            self.execution_log = self.execution_log[-1000:]
    
    def get_metrics(self) -> Dict:
        """Get performance metrics."""
        return {
            **self.performance_metrics,
            'module_status': {
                name: 'loaded' if module else 'not_loaded'
                for name, module in self.modules.items()
            }
        }
    
    def get_reasoning_trace(self, query_id: str = None) -> Optional[str]:
        """Get reasoning trace for a query (if self module is active)."""
        if self.modules.get('self'):
            return self.modules['self'].get_trace(query_id)
        return None


# Global instance
cel_core = None

def get_cel() -> CELCore:
    """Get or create singleton CEL instance."""
    global cel_core
    if cel_core is None:
        cel_core = CELCore()
    return cel_core


def enhance(user_input: str, context: Dict = None, 
            modules: List[str] = None) -> str:
    """
    Convenience function to enhance input with CEL.
    
    Args:
        user_input: Input to enhance
        context: Optional context
        modules: Specific modules to use
    
    Returns:
        Enhanced response
    """
    cel = get_cel()
    result = cel.process(user_input, context, modules)
    return result['aggregated_response']


if __name__ == "__main__":
    # Test CEL-Core
    print("🧠 Testing CEL-Core...")
    
    cel = CELCore()
    
    test_inputs = [
        "Why does the scanner miss some tokens?",
        "Create a new trading strategy",
        "Compare this to previous versions",
        "Should I trade this token?"
    ]
    
    for test_input in test_inputs:
        print(f"\n{'='*60}")
        print(f"Input: {test_input}")
        analysis = cel.analyze_input(test_input)
        print(f"Analysis: {analysis}")
    
    print(f"\n{'='*60}")
    print("CEL-Core initialized successfully!")
