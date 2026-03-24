#!/usr/bin/env python3
"""
Memory CLI - Command Line Interface for Universal Memory System
Easy commands to remember, recall, and manage memories.
"""

import sys
import argparse
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from aca_memory_system import UniversalMemorySystem, get_ums
from memory_bridge import MemoryBridge

def main():
    parser = argparse.ArgumentParser(
        description="🧠 Universal Memory System CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s remember "Important decision made" --category decision
  %(prog)s recall "trading strategy"
  %(prog)s research "crypto mining" --findings "Mining is not profitable..."
  %(prog)s context "what were we building"
  %(prog)s today
  %(prog)s status
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Remember command
    remember_parser = subparsers.add_parser("remember", help="Remember something")
    remember_parser.add_argument("content", help="Content to remember")
    remember_parser.add_argument("--category", "-c", help="Category (code, research, decision)")
    remember_parser.add_argument("--tags", "-t", nargs="+", help="Tags (space-separated)")
    
    # Recall command
    recall_parser = subparsers.add_parser("recall", help="Recall memories")
    recall_parser.add_argument("query", help="Search query")
    recall_parser.add_argument("--limit", "-l", type=int, default=5, help="Max results")
    
    # Research command
    research_parser = subparsers.add_parser("research", help="Store research")
    research_parser.add_argument("topic", help="Research topic")
    research_parser.add_argument("--findings", "-f", required=True, help="Research findings")
    research_parser.add_argument("--sources", "-s", nargs="+", help="Source URLs/references")
    
    # Decision command
    decision_parser = subparsers.add_parser("decision", help="Store decision")
    decision_parser.add_argument("text", help="Decision text")
    decision_parser.add_argument("--reasoning", "-r", required=True, help="Reasoning")
    decision_parser.add_argument("--context", "-c", help="Additional context")
    
    # Context command
    context_parser = subparsers.add_parser("context", help="Get context for query")
    context_parser.add_argument("query", help="Query to get context for")
    context_parser.add_argument("--limit", "-l", type=int, default=5, help="Max entries")
    
    # Today command
    today_parser = subparsers.add_parser("today", help="Show today's memories")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show memory system status")
    
    # Interactive command
    interactive_parser = subparsers.add_parser("interactive", help="Interactive memory mode")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize
    ums = get_ums()
    bridge = MemoryBridge()
    
    # Execute command
    if args.command == "remember":
        entry_id = ums.capture(
            content=args.content,
            category=args.category,
            tags=args.tags or []
        )
        print(f"✅ Remembered! ID: {entry_id[:16]}...")
    
    elif args.command == "recall":
        results = ums.search(args.query, limit=args.limit)
        if results:
            print(f"\n🔍 Found {len(results)} memories:\n")
            for i, entry in enumerate(results, 1):
                date = entry.timestamp[:10]
                print(f"{i}. [{entry.category.upper()}] ({date})")
                print(f"   {entry.content[:100]}...")
                if entry.tags:
                    print(f"   Tags: {', '.join(entry.tags)}")
                print()
        else:
            print("No memories found.")
    
    elif args.command == "research":
        entry_id = ums.remember_research(
            topic=args.topic,
            findings=args.findings,
            sources=args.sources or []
        )
        print(f"✅ Research saved! ID: {entry_id[:16]}...")
    
    elif args.command == "decision":
        entry_id = ums.remember_decision(
            decision=args.text,
            reasoning=args.reasoning,
            context=args.context or ""
        )
        print(f"✅ Decision saved! ID: {entry_id[:16]}...")
    
    elif args.command == "context":
        context = ums.get_context(args.query, max_entries=args.limit)
        if context:
            print(context)
        else:
            print("No relevant context found.")
    
    elif args.command == "today":
        summary = ums.get_daily_summary()
        print(summary)
    
    elif args.command == "status":
        print("\n" + "="*60)
        print("🧠 Universal Memory System Status")
        print("="*60)
        print(f"\nMemory Directory: {ums.memory_dir}")
        print(f"Index Entries: {len(ums.index.get('entries', {}))}")
        print(f"Tags: {len(ums.index.get('tags', {}))}")
        print(f"Keywords: {len(ums.index.get('keywords', {}))}")
        print(f"\nSession Cache: {len(ums.session_cache)} entries")
        print("\n✅ System operational")
    
    elif args.command == "interactive":
        print("\n" + "="*60)
        print("🧠 Interactive Memory Mode")
        print("="*60)
        print("\nCommands: remember, recall, research, decision, context, quit")
        print()
        
        while True:
            try:
                cmd = input("memory> ").strip()
                if cmd.lower() == "quit":
                    break
                
                parts = cmd.split(maxsplit=1)
                if not parts:
                    continue
                
                if parts[0] == "remember":
                    entry_id = ums.capture(parts[1])
                    print(f"✅ Remembered: {entry_id[:16]}...")
                
                elif parts[0] == "recall":
                    results = ums.search(parts[1], limit=3)
                    for entry in results:
                        print(f"  [{entry.category}] {entry.content[:80]}...")
                
                else:
                    print("Unknown command. Try: remember, recall, context, quit")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
        
        print("\nGoodbye!")

if __name__ == "__main__":
    main()
