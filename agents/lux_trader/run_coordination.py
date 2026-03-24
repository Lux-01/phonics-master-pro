#!/usr/bin/env python3
"""
🔥 MULTI-AGENT COORDINATOR: LUXTRADER v3.0 + HOLY TRINITY
Skill: multi-agent-coordinator
Method: Parallel agent execution with monitoring

Agents:
- Agent A: LuxTrader v3.0 (Research + Trading)
- Agent B: Holy Trinity (Risk + Analysis + Trading)

Coordination:
1. Spawn both agents
2. Run in parallel
3. Monitor status
4. Merge results
5. Status reporting
"""

import subprocess
import json
import time
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import asyncio

WORKSPACE = Path("/home/skux/.openclaw/workspace/agents/lux_trader")
LOGS_DIR = WORKSPACE / "parallel_logs"
LOGS_DIR.mkdir(exist_ok=True)

class TradingAgent:
    """
    Agent wrapper for trading systems
    Follows Multi-Agent Coordinator pattern
    """
    def __init__(self, name: str, script: str, state_file: str):
        self.name = name
        self.script = script
        self.state_file = state_file
        self.pid = None
        self.process = None
        self.log_file = None
        
    def spawn(self) -> Tuple[bool, str]:
        """Spawn agent process"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = LOGS_DIR / f"{self.name}_{timestamp}.log"
        
        try:
            with open(self.log_file, 'w') as log:
                self.process = subprocess.Popen(
                    ['python3', str(WORKSPACE / self.script)],
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    cwd=WORKSPACE
                )
                self.pid = self.process.pid
                return True, f"Spawned (PID: {self.pid})"
        except Exception as e:
            return False, f"Failed to spawn: {e}"
    
    def check_status(self) -> Dict:
        """Check agent health and state"""
        # Check if process running
        is_running = self.process is not None and self.process.poll() is None
        
        # Load state
        state = {}
        if (WORKSPACE / self.state_file).exists():
            try:
                with open(WORKSPACE / self.state_file) as f:
                    state = json.load(f)
            except:
                pass
        
        return {
            "name": self.name,
            "pid": self.pid,
            "running": is_running,
            "capital": state.get('total_capital', 'N/A'),
            "trades": state.get('total_trades', 0),
            "wins": state.get('wins', 0),
            "losses": state.get('losses', 0),
            "daily_pnl": state.get('daily_pnl', 0),
            "daily_trades": state.get('daily_trades', 0),
            "log_file": str(self.log_file) if self.log_file else None
        }
    
    def terminate(self) -> bool:
        """Terminate agent"""
        if self.pid:
            try:
                import subprocess
                subprocess.run(['kill', str(self.pid)], check=False)
                return True
            except:
                pass
        return False


class ParallelTradingCoordinator:
    """
    Multi-Agent Coordinator for parallel trading
    
    Philosophy: One AI becomes many - specialists working together
    """
    
    def __init__(self):
        self.agents = {
            "luxtrader": TradingAgent(
                name="LuxTrader_v3.0",
                script="luxtrader_live.py",
                state_file="live_state.json"
            ),
            "holy_trinity": TradingAgent(
                name="Holy_Trinity",
                script="holy_trinity_live.py",
                state_file="holy_trinity_state.json"
            )
        }
        self.start_time = None
        
    def print_header(self):
        """Print MAC header"""
        print("="*80)
        print("🔥 MULTI-AGENT COORDINATOR")
        print("="*80)
        print("Skill: multi-agent-coordinator v2.0")
        print("Method: Parallel execution with monitoring")
        print("Agents: LuxTrader v3.0 + Holy Trinity")
        print("="*80)
        
    def check_existing(self) -> Dict[str, bool]:
        """Check for existing running agents"""
        import subprocess
        running = {}
        
        for name, agent in self.agents.items():
            # Check if script already running using pgrep
            try:
                result = subprocess.run(['pgrep', '-f', agent.script], 
                                    capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    agent.pid = int(result.stdout.strip().split('\n')[0])
                    running[name] = True
                else:
                    running[name] = False
            except:
                running[name] = False
                
        return running
    
    def spawn_agents(self) -> List[Tuple[str, bool, str]]:
        """
        Step 1: SPAWN - Create agent processes
        MAC Pattern: Spawn specialists
        """
        print("\n🚀 STEP 1: SPAWN AGENTS")
        print("-"*80)
        
        results = []
        existing = self.check_existing()
        
        for name, agent in self.agents.items():
            if existing[name]:
                print(f"✅ {agent.name}: Already running (PID: {agent.pid})")
                results.append((name, True, f"Existing (PID: {agent.pid})"))
            else:
                print(f"🆕 {agent.name}: Spawning...")
                success, msg = agent.spawn()
                status = "✅" if success else "❌"
                print(f"   {status} {msg}")
                results.append((name, success, msg))
                
        return results
    
    def execute_parallel(self) -> Dict:
        """
        Step 2: EXECUTE - Run agents in parallel
        MAC Pattern: Parallel execution
        """
        print("\n⚡ STEP 2: EXECUTE PARALLEL")
        print("-"*80)
        print("Agents running independently...")
        print("Each agent:")
        print("  • Monitors market independently")
        print("  • Makes own trading decisions")
        print("  • Logs to separate files")
        print("  • Updates own state")
        print()
        print("Waiting for initial status...")
        time.sleep(2)  # Give agents time to initialize
        
        return {"status": "running", "agents": len(self.agents)}
    
    def monitor_status(self) -> Dict:
        """
        Step 3: MONITOR - Check agent health
        MAC Pattern: Status aggregation
        """
        print("\n📊 STEP 3: MONITOR STATUS")
        print("-"*80)
        
        statuses = {}
        total_capital = 0
        total_trades = 0
        
        for name, agent in self.agents.items():
            status = agent.check_status()
            statuses[name] = status
            
            # Display
            print(f"\n🔷 {status['name']}")
            print(f"   Status: {'🟢 RUNNING' if status['running'] else '🔴 STOPPED'}")
            print(f"   PID: {status['pid']}")
            print(f"   Capital: {status['capital']:.4f} SOL" if isinstance(status['capital'], float) else f"   Capital: {status['capital']}")
            print(f"   Trades: {status['trades']} (W:{status['wins']}/L:{status['losses']})")
            print(f"   Daily PnL: {status['daily_pnl']:.4f} SOL")
            print(f"   Daily Trades: {status['daily_trades']}")
            
            if isinstance(status['capital'], (int, float)):
                total_capital += status['capital']
            total_trades += status['trades']
        
        return {
            "agents": statuses,
            "summary": {
                "total_capital": total_capital,
                "total_trades": total_trades,
                "running_agents": sum(1 for s in statuses.values() if s['running'])
            }
        }
    
    def merge_results(self, statuses: Dict) -> Dict:
        """
        Step 4: MERGE - Combine results
        MAC Pattern: Synthesis
        """
        print("\n🔄 STEP 4: MERGE & SYNTHESIZE")
        print("-"*80)
        
        # Aggregate stats
        lux = statuses.get('luxtrader', {})
        tri = statuses.get('holy_trinity', {})
        
        combined = {
            "total_capital": (lux.get('capital', 0) or 0) + (tri.get('capital', 0) or 0),
            "total_trades": lux.get('trades', 0) + tri.get('trades', 0),
            "total_wins": lux.get('wins', 0) + tri.get('wins', 0),
            "total_losses": lux.get('losses', 0) + tri.get('losses', 0),
            "daily_pnl": lux.get('daily_pnl', 0) + tri.get('daily_pnl', 0),
            "running": sum(1 for s in statuses.values() if s.get('running'))
        }
        
        print("Combined Portfolio:")
        print(f"   💰 Total Capital: {combined['total_capital']:.4f} SOL")
        print(f"   📊 Total Trades: {combined['total_trades']}")
        print(f"   ✅ Total Wins: {combined['total_wins']}")
        print(f"   ❌ Total Losses: {combined['total_losses']}")
        print(f"   📈 Daily PnL: {combined['daily_pnl']:.4f} SOL")
        print(f"   🟢 Agents Running: {combined['running']}/2")
        
        return combined
    
    def report_outcome(self, combined: Dict):
        """
        Step 5: REPORT - Final output
        MAC Pattern: Delivery
        """
        print("\n" + "="*80)
        print("✅ COORDINATION COMPLETE")
        print("="*80)
        print()
        print("📊 FINAL STATUS:")
        print(f"   Total Capital: {combined['total_capital']:.4f} SOL")
        print(f"   Total Trades: {combined['total_trades']}")
        print(f"   Win Rate: {combined['total_wins']/max(1,combined['total_trades'])*100:.1f}%")
        print(f"   Daily PnL: {combined['daily_pnl']:+.4f} SOL")
        print()
        print("📝 LOG FILES:")
        for name, agent in self.agents.items():
            if agent.log_file:
                print(f"   {name}: {agent.log_file}")
        print()
        print("🔧 STATE FILES:")
        print(f"   LuxTrader: {WORKSPACE}/live_state.json")
        print(f"   Holy Trinity: {WORKSPACE}/holy_trinity_state.json")
        print()
        print("📋 NEXT COMMANDS:")
        print("   Check status: python3 run_coordination.py --status")
        print("   Stop all:     python3 run_coordination.py --stop")
        print("   Logs:         ls -la parallel_logs/")
        print("="*80)
    
    def stop_all(self):
        """Stop all agents"""
        print("\n🛑 STOPPING ALL AGENTS")
        print("-"*80)
        
        for name, agent in self.agents.items():
            if agent.terminate():
                print(f"✅ {agent.name}: Stopped")
            else:
                print(f"⚠️  {agent.name}: Not running or already stopped")
                
        # Cleanup PID files
        for pid_file in ['.luxtrader.pid', '.holy_trinity.pid']:
            f = WORKSPACE / pid_file
            if f.exists():
                f.unlink()
                
        print("✅ All agents stopped")
    
    def run(self):
        """Execute full coordination workflow"""
        self.print_header()
        
        # Step 1: Spawn
        spawn_results = self.spawn_agents()
        
        # Check if any failed
        if not any(success for _, success, _ in spawn_results):
            print("❌ All agents failed to spawn")
            return
        
        # Step 2: Execute
        self.execute_parallel()
        
        # Step 3: Monitor
        monitor_data = self.monitor_status()
        
        # Step 4: Merge
        combined = self.merge_results(monitor_data['agents'])
        
        # Step 5: Report
        self.report_outcome(combined)
        
        # Save coordination state
        state = {
            "timestamp": datetime.now().isoformat(),
            "skill": "multi-agent-coordinator",
            "agents": list(self.agents.keys()),
            "summary": combined,
            "status": "active"
        }
        
        with open(WORKSPACE / "coordination_state.json", 'w') as f:
            json.dump(state, f, indent=2)


def main():
    import sys
    
    coordinator = ParallelTradingCoordinator()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--status":
            coordinator.print_header()
            monitor_data = coordinator.monitor_status()
            combined = coordinator.merge_results(monitor_data['agents'])
            coordinator.report_outcome(combined)
            return
        elif sys.argv[1] == "--stop":
            coordinator.stop_all()
            return
    
    # Full coordination run
    coordinator.run()


if __name__ == "__main__":
    main()
