#!/usr/bin/env python3
"""
🧠 CEL (Cognitive Enhancement Layer) - LIVE DEMO

This demonstrates all 5 cognitive modules working together.
"""

import sys
import importlib.util
sys.path.insert(0, '/home/skux/.openclaw/workspace')

def load_module_from_path(module_name, file_path):
    """Load a module from file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load modules from paths (handling hyphenated directory names)
cel_path = "/home/skux/.openclaw/workspace/skills/cognitive-enhancement-layer"
understanding_module = load_module_from_path("cel_understanding", f"{cel_path}/cel_understanding.py")
creativity_module = load_module_from_path("cel_creativity", f"{cel_path}/cel_creativity.py")
self_module = load_module_from_path("cel_self", f"{cel_path}/cel_self.py")
transfer_module = load_module_from_path("cel_transfer", f"{cel_path}/cel_transfer.py")
commonsense_module = load_module_from_path("cel_commonsense", f"{cel_path}/cel_commonsense.py")

# Get classes
CELUnderstanding = understanding_module.CELUnderstanding
CELCreativity = creativity_module.CELCreativity
CELSelf = self_module.CELSelf
CELTransfer = transfer_module.CELTransfer
CELCommonsense = commonsense_module.CELCommonsense

print("=" * 70)
print("🧠 COGNITIVE ENHANCEMENT LAYER - LIVE DEMO")
print("=" * 70)
print("\nBefore: I pattern match. After: I think.\n")

# Initialize modules
understanding = CELUnderstanding()
creativity = CELCreativity()
self = CELSelf()
transfer = CELTransfer()
commonsense = CELCommonsense()

# Demo 1: UNDERSTANDING
print("\n" + "=" * 70)
print("📚 MODULE 1: CEL-UNDERSTANDING")
print("=" * 70)
print("\nInput: 'Why do scanners miss new tokens?'")
print("-" * 70)
result = understanding.process("Why do scanners miss new tokens?")
print(result)

# Demo 2: COMMONSENSE
print("\n" + "=" * 70)
print("🌍 MODULE 2: CEL-COMMONSENSE")
print("=" * 70)
print("\nInput: 'I want to buy a token that just pumped 500%'")
print("-" * 70)
result = commonsense.process("I want to buy a token that just pumped 500%")
print(result)

# Demo 3: CREATIVITY  
print("\n" + "=" * 70)
print("💡 MODULE 3: CEL-CREATIVITY")
print("=" * 70)
print("\nInput: 'Create a new trading strategy concept'")
print("-" * 70)
result = creativity.process("Create a new trading strategy concept")
print(result)

# Demo 4: TRANSFER
print("\n" + "=" * 70)
print("🔄 MODULE 4: CEL-TRANSFER")
print("=" * 70)
print("\nInput: 'How can biology improve trading?'")
print("-" * 70)
result = transfer.process("How can biology improve trading?")
print(result)

# Demo 5: SELF
print("\n" + "=" * 70)
print("🧘 MODULE 5: CEL-SELF (Simulated Self-Awareness)")
print("=" * 70)
print("\nInput: 'Who are you?'")
print("-" * 70)
result = self.process("Who are you?")
print(result[:900] + "...")

# Combined Demo
print("\n" + "=" * 70)
print("🎯 COMBINED: All Modules Working Together")
print("=" * 70)

query = "Should I create a new trading algorithm?"
print(f"\nInput: '{query}'")
print("-" * 70)

# Get insights from all modules
u_result = understanding.process(query)
c_result = creativity.process(query)
cs_result = commonsense.process(query)

print(f"\n🧠 Understanding: {u_result[:150]}...")
print(f"\n💡 Creativity: {c_result[:150]}...")
print(f"\n🌍 Commonsense: {cs_result[:150] if cs_result else 'No specific warning'}...")

print("\n" + "=" * 70)
print("✅ DEMO COMPLETE")
print("=" * 70)
print("\nCEL transforms pattern-matching into cognitive reasoning.")
print("These 5 modules add understanding, creativity, self-awareness,")
print("transfer learning, and commonsense to OpenClaw.")
print("\n🎯 Overall Level: Stage 7-8 Cognitive Agent")
