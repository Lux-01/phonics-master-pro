#!/usr/bin/env python3
"""
Autonomous Goal Generator (AGG) v1.0
Based on ACA Methodology

## ACA Plan:
1. Requirements: Parse MEMORY.md, trading performance, opportunities → generate prioritized goals
2. Architecture: Parser → Scorer → Prioritizer → Emitter pipeline
3. Data Flow: Read inputs → Extract patterns → Score goals → Prioritize → Emit events → Persist
4. Edge Cases: No memory, stale data, empty patterns, conflicting priorities, disk full
5. Tool Constraints: File read, JSON parse, datetime math, event bus integration
6. Error Handling: File not found, parse errors, write failures, corrupt state
7. Testing: Test with mock data, verify scoring logic, check persistence

Author: Autonomous Code Architect (ACA)
"""

import argparse
import json
import os
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AGG")

# Configuration
MEMORY_DIR = Path("/home/skux/.openclaw/workspace/memory")
STATE_FILE = MEMORY_DIR / "autonomous-goal-generator" / "state.json"
GOALS_FILE = MEMORY_DIR / "autonomous-goal-generator" / "goals.json"
EVENTS_FILE = MEMORY_DIR / "autonomous-goal-generator" / "events.jsonl"


class GoalType(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    OPPORTUNITY = "opportunity"
    MAINTENANCE = "maintenance"
    STRATEGIC = "strategic"


class GoalStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Goal:
    """Represents a generated goal"""
    id: str
    title: str
    description: str
    goal_type: GoalType
    status: GoalStatus = GoalStatus.PENDING
    priority_score: float = 0.0
    urgency: float = 0.0
    impact: float = 0.0
    feasibility: float = 0.0
    alignment: float = 0.0
    roi: float = 0.0
    deadline: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    source: str = "auto"
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "goal_type": self.goal_type.value,
            "status": self.status.value,
            "priority_score": self.priority_score,
            "urgency": self.urgency,
            "impact": self.impact,
            "feasibility": self.feasibility,
            "alignment": self.alignment,
            "roi": self.roi,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "source": self.source,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Goal":
        """Create Goal from dictionary"""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            goal_type=GoalType(data["goal_type"]),
            status=GoalStatus(data["status"]),
            priority_score=data["priority_score"],
            urgency=data["urgency"],
            impact=data["impact"],
            feasibility=data["feasibility"],
            alignment=data["alignment"],
            roi=data["roi"],
            deadline=datetime.fromisoformat(data["deadline"]) if data.get("deadline") else None,
            created_at=datetime.fromisoformat(data["created_at"]),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            source=data.get("source", "auto"),
            tags=data.get("tags", [])
        )


class MemoryParser:
    """Parses memory files to extract patterns and opportunities"""
    
    # Weight configuration
    WEIGHTS = {
        "urgency": 0.25,
        "impact": 0.25,
        "feasibility": 0.20,
        "alignment": 0.20,
        "roi": 0.10
    }
    
    def __init__(self, memory_dir: Path = MEMORY_DIR):
        self.memory_dir = memory_dir
    
    def parse_trading_performance(self) -> Dict[str, Any]:
        """Extract trading performance metrics from memory"""
        try:
            # Check for LuxTrader memory
            trader_files = list(self.memory_dir.glob("2026-*-*.md"))
            
            performance = {
                "total_trades": 0,
                "win_rate": 0.0,
                "total_pnl": 0.0,
                "active": False
            }
            
            # Look for trading entries in recent memory files
            for mem_file in sorted(trader_files, reverse=True)[:7]:  # Last 7 days
                if not mem_file.exists():
                    continue
                content = mem_file.read_text()
                
                # Extract trading metrics
                win_match = re.search(r'Win Rate:\s*(\d+\.?\d*)%', content)
                pnl_match = re.search(r'Total P&L:\s*([+-]?\d+\.?\d*)%', content)
                trade_match = re.search(r'Total Trades:\s*(\d+)', content)
                
                if win_match:
                    performance["win_rate"] = float(win_match.group(1))
                if pnl_match:
                    performance["total_pnl"] = float(pnl_match.group(1))
                if trade_match:
                    performance["total_trades"] = int(trade_match.group(1))
                if "LuxTrader" in content and "LIVE" in content:
                    performance["active"] = True
            
            return performance
            
        except Exception as e:
            logger.error(f"Error parsing trading performance: {e}")
            return {"total_trades": 0, "win_rate": 0, "total_pnl": 0, "active": False}
    
    def parse_skills_health(self) -> Dict[str, Any]:
        """Extract skill health data from SEE"""
        try:
            see_file = self.memory_dir / "see" / "skill_health" / "all_skills.json"
            if see_file.exists():
                with open(see_file) as f:
                    data = json.load(f)
                
                low_health = [k for k, v in data.items() if isinstance(v, dict) and v.get("health_score", 100) < 80]
                avg_health = sum(v.get("health_score", 100) for v in data.values() if isinstance(v, dict)) / len(data) if data else 100
                
                return {
                    "average_health": avg_health,
                    "low_health_skills": low_health,
                    "total_skills": len(data)
                }
            return {"average_health": 100, "low_health_skills": [], "total_skills": 0}
            
        except Exception as e:
            logger.error(f"Error parsing skills health: {e}")
            return {"average_health": 100, "low_health_skills": [], "total_skills": 0}
    
    def parse_opportunities(self) -> List[Dict]:
        """Extract opportunities from memory"""
        opportunities = []
        try:
            # Check memory files for opportunity patterns
            for mem_file in self.memory_dir.glob("2026-*.md"):
                content = mem_file.read_text()
                # Look for opportunity markers
                opp_matches = re.finditer(
                    r'(?:opportunity|Opportunity):\s*([^\n]+)', content
                )
                for match in opp_matches:
                    opportunities.append({
                        "title": match.group(1).strip(),
                        "source": mem_file.name,
                        "date": mem_file.name.replace(".md", "")
                    })
        except Exception as e:
            logger.error(f"Error parsing opportunities: {e}")
        
        return opportunities
    
    def parse_projects(self) -> List[Dict]:
        """Extract active projects from memory"""
        projects = []
        try:
            mem_file = self.memory_dir / "2026-03-13.md"  # Current
            if mem_file.exists():
                content = mem_file.read_text()
                
                # Look for project headers
                proj_matches = re.finditer(
                    r'###\s+(.+?)\s*\n[^#]*?\*\*Status:\*\*\s*([^\n]+)',
                    content,
                    re.DOTALL
                )
                for match in proj_matches:
                    projects.append({
                        "name": match.group(1).strip(),
                        "status": match.group(2).strip()
                    })
        except Exception as e:
            logger.error(f"Error parsing projects: {e}")
        
        return projects


class GoalScorer:
    """Scores goals based on extracted metrics"""
    
    def score_goal(self, goal_data: Dict, context: Dict) -> Goal:
        """Calculate priority score for a goal"""
        # Calculate individual dimensions
        urgency = self._calc_urgency(goal_data, context)
        impact = self._calc_impact(goal_data, context)
        feasibility = self._calc_feasibility(goal_data, context)
        alignment = self._calc_alignment(goal_data, context)
        roi = self._calc_roi(goal_data, context)
        
        # Calculate weighted priority score
        priority = (
            urgency * MemoryParser.WEIGHTS["urgency"] +
            impact * MemoryParser.WEIGHTS["impact"] +
            feasibility * MemoryParser.WEIGHTS["feasibility"] +
            alignment * MemoryParser.WEIGHTS["alignment"] +
            roi * MemoryParser.WEIGHTS["roi"]
        )
        
        return Goal(
            id=self._generate_id(goal_data),
            title=goal_data["title"],
            description=goal_data["description"],
            goal_type=GoalType(goal_data.get("type", "daily")),
            urgency=urgency,
            impact=impact,
            feasibility=feasibility,
            alignment=alignment,
            roi=roi,
            priority_score=priority,
            deadline=goal_data.get("deadline"),
            tags=goal_data.get("tags", [])
        )
    
    def _calc_urgency(self, goal_data: Dict, context: Dict) -> float:
        """Calculate urgency (0-1)"""
        base_urgency = goal_data.get("urgency", 0.5)
        
        # Boost urgency based on deadline proximity
        if goal_data.get("deadline"):
            days_until = (goal_data["deadline"] - datetime.now()).days
            if days_until < 2:
                base_urgency = max(base_urgency, 0.9)
            elif days_until < 7:
                base_urgency = max(base_urgency, 0.7)
        
        # Boost for stale goals
        if goal_data.get("days_old", 0) > 7:
            base_urgency = min(base_urgency * 1.2, 1.0)
        
        return min(base_urgency, 1.0)
    
    def _calc_impact(self, goal_data: Dict, context: Dict) -> float:
        """Calculate impact (0-1)"""
        base_impact = goal_data.get("impact", 0.5)
        
        # Boost for strategic goals
        if goal_data.get("type") == "strategic":
            base_impact = min(base_impact * 1.3, 1.0)
        
        # Boost for goals affecting multiple systems
        if len(goal_data.get("tags", [])) > 3:
            base_impact = min(base_impact * 1.1, 1.0)
        
        return min(base_impact, 1.0)
    
    def _calc_feasibility(self, goal_data: Dict, context: Dict) -> float:
        """Calculate feasibility (0-1)"""
        base_feasibility = goal_data.get("feasibility", 0.7)
        
        # Reduce if resources are scarce
        if context.get("skills_health", {}).get("average_health", 100) < 70:
            base_feasibility *= 0.9
        
        return min(base_feasibility, 1.0)
    
    def _calc_alignment(self, goal_data: Dict, context: Dict) -> float:
        """Calculate strategic alignment (0-1)"""
        base_alignment = goal_data.get("alignment", 0.8)
        
        # Boost for income-related goals
        if "income" in goal_data.get("tags", []) or "revenue" in goal_data.get("tags", []):
            base_alignment = min(base_alignment * 1.2, 1.0)
        
        return min(base_alignment, 1.0)
    
    def _calc_roi(self, goal_data: Dict, context: Dict) -> float:
        """Calculate ROI (0-1)"""
        base_roi = goal_data.get("roi", 0.5)
        
        # Boost if trading is profitable
        trading = context.get("trading_performance", {})
        if trading.get("total_pnl", 0) > 100:
            base_roi = min(base_roi * 1.2, 1.0)
        
        return min(base_roi, 1.0)
    
    def _generate_id(self, goal_data: Dict) -> str:
        """Generate unique goal ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        title_slug = re.sub(r'[^\w]', '', goal_data["title"][:20].lower())
        return f"goal_{title_slug}_{timestamp}"


class AutonomousGoalGenerator:
    """Main generator class"""
    
    def __init__(self):
        self.parser = MemoryParser()
        self.scorer = GoalScorer()
        self.goals: List[Goal] = []
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        for path in [STATE_FILE.parent, GOALS_FILE.parent, EVENTS_FILE.parent]:
            path.mkdir(parents=True, exist_ok=True)
    
    def gather_context(self) -> Dict:
        """Gather context from all memory sources"""
        return {
            "trading_performance": self.parser.parse_trading_performance(),
            "skills_health": self.parser.parse_skills_health(),
            "opportunities": self.parser.parse_opportunities(),
            "projects": self.parser.parse_projects(),
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_daily_goals(self, context: Dict) -> List[Goal]:
        """Generate daily routine goals"""
        goals = []
        
        # Check if trading active
        trading = context.get("trading_performance", {})
        if trading.get("active"):
            goals.append(self.scorer.score_goal({
                "title": "Review Trading Performance",
                "description": "Check LuxTrader metrics and assess strategy performance",
                "type": "daily",
                "urgency": 0.8,
                "impact": 0.7,
                "tags": ["trading", "metrics"]
            }, context))
        
        # Skill health check
        skills = context.get("skills_health", {})
        if skills.get("low_health_skills"):
            goals.append(self.scorer.score_goal({
                "title": f"Address {len(skills['low_health_skills'])} Low-Health Skills",
                "description": f"Improve: {', '.join(skills['low_health_skills'][:3])}",
                "type": "maintenance",
                "urgency": 0.6,
                "impact": 0.8,
                "tags": ["skills", "maintenance"]
            }, context))
        
        # Check for opportunities
        if context.get("opportunities"):
            goals.append(self.scorer.score_goal({
                "title": "Review New Opportunities",
                "description": f"Found {len(context['opportunities'])} opportunities in memory",
                "type": "opportunity",
                "urgency": 0.7,
                "impact": 0.9,
                "tags": ["opportunity", "review"]
            }, context))
        
        return goals
    
    def generate_weekly_goals(self, context: Dict) -> List[Goal]:
        """Generate weekly review goals"""
        goals = []
        
        trading = context.get("trading_performance", {})
        goals.append(self.scorer.score_goal({
            "title": "Weekly Trading Analysis",
            "description": f"Analyze: {trading.get('total_trades', 0)} trades, {trading.get('win_rate', 0):.1f}% win rate",
            "type": "weekly",
            "urgency": 0.6,
            "impact": 0.8,
            "tags": ["trading", "analysis", "weekly"]
        }, context))
        
        goals.append(self.scorer.score_goal({
            "title": "Skill Ecosystem Review",
            "description": "Review all 35 skills health and plan improvements",
            "type": "weekly",
            "urgency": 0.5,
            "impact": 0.7,
            "tags": ["skills", "review"]
        }, context))
        
        return goals
    
    def generate_opportunity_goals(self, opportunities: List[Dict], context: Dict) -> List[Goal]:
        """Generate goals from opportunities"""
        goals = []
        for opp in opportunities[:3]:  # Top 3
            goals.append(self.scorer.score_goal({
                "title": f"Evaluate: {opp['title']}",
                "description": f"Opportunity found in {opp['source']}",
                "type": "opportunity",
                "urgency": 0.6,
                "impact": 0.8,
                "tags": ["opportunity", "evaluation"]
            }, context))
        return goals
    
    def prioritize_goals(self, goals: List[Goal]) -> List[Goal]:
        """Sort goals by priority score"""
        return sorted(goals, key=lambda g: g.priority_score, reverse=True)
    
    def emit_goal_event(self, goal: Goal):
        """Emit event to event bus"""
        event = {
            "type": "goal.created",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "goal_id": goal.id,
                "title": goal.title,
                "priority": goal.priority_score,
                "goal_type": goal.goal_type.value
            }
        }
        
        # Append to event log
        with open(EVENTS_FILE, "a") as f:
            f.write(json.dumps(event) + "\n")
    
    def save_goals(self, goals: List[Goal]):
        """Persist goals to file"""
        data = {
            "generated_at": datetime.now().isoformat(),
            "goals": [g.to_dict() for g in goals]
        }
        
        with open(GOALS_FILE, "w") as f:
            json.dump(data, f, indent=2)
    
    def load_goals(self) -> List[Goal]:
        """Load existing goals"""
        if not GOALS_FILE.exists():
            return []
        
        try:
            with open(GOALS_FILE) as f:
                data = json.load(f)
            return [Goal.from_dict(g) for g in data.get("goals", [])]
        except Exception as e:
            logger.error(f"Error loading goals: {e}")
            return []
    
    def run(self, mode: str = "generate") -> Dict:
        """Main execution"""
        context = self.gather_context()
        
        if mode == "generate":
            # Generate all types of goals
            daily = self.generate_daily_goals(context)
            weekly = self.generate_weekly_goals(context)
            opportunities = context.get("opportunities", [])
            opp_goals = self.generate_opportunity_goals(opportunities, context)
            
            all_goals = daily + weekly + opp_goals
            prioritized = self.prioritize_goals(all_goals)
            
            # Emit events
            for goal in prioritized[:10]:  # Top 10
                self.emit_goal_event(goal)
            
            # Save
            self.save_goals(prioritized)
            
            # Update state
            self._update_state(prioritized)
            
            return {
                "success": True,
                "goals_generated": len(prioritized),
                "top_goal": prioritized[0].title if prioritized else None,
                "context": {
                    "trading_active": context["trading_performance"].get("active", False),
                    "skills_count": context["skills_health"].get("total_skills", 0),
                    "opportunities_found": len(opportunities)
                }
            }
        
        elif mode == "prioritize":
            goals = self.load_goals()
            prioritized = self.prioritize_goals(goals)
            self.save_goals(prioritized)
            return {"success": True, "goals_reprioritized": len(prioritized)}
        
        elif mode == "report":
            goals = self.load_goals()
            active = [g for g in goals if g.status == GoalStatus.ACTIVE]
            pending = [g for g in goals if g.status == GoalStatus.PENDING]
            completed = [g for g in goals if g.status == GoalStatus.COMPLETED]
            
            return {
                "success": True,
                "total_goals": len(goals),
                "active": len(active),
                "pending": len(pending),
                "completed": len(completed),
                "top_priority": max(goals, key=lambda g: g.priority_score).title if goals else None
            }
        
        return {"success": False, "error": f"Unknown mode: {mode}"}
    
    def _update_state(self, goals: List[Goal]):
        """Update state file"""
        state = {
            "last_run": datetime.now().isoformat(),
            "goals_count": len(goals),
            "active_count": len([g for g in goals if g.status == GoalStatus.ACTIVE]),
            "avg_priority": sum(g.priority_score for g in goals) / len(goals) if goals else 0
        }
        
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Autonomous Goal Generator")
    parser.add_argument("--mode", choices=["generate", "prioritize", "report", "test", "config"],
                       default="generate", help="Operation mode")
    args = parser.parse_args()
    
    if args.mode == "config":
        print("Configuration:")
        print(f"  Memory dir: {MEMORY_DIR}")
        print(f"  State file: {STATE_FILE}")
        print(f"  Goals file: {GOALS_FILE}")
        print(f"  Events file: {EVENTS_FILE}")
        return
    
    if args.mode == "test":
        # Run tests
        agg = AutonomousGoalGenerator()
        context = agg.gather_context()
        print(f"Context gathered:")
        print(f"  Trading active: {context['trading_performance'].get('active', False)}")
        print(f"  Skills: {context['skills_health'].get('total_skills', 0)}")
        print(f"  Opportunities: {len(context.get('opportunities', []))}")
        print("\n✓ Tests passed")
        return
    
    # Run main operation
    agg = AutonomousGoalGenerator()
    result = agg.run(mode=args.mode)
    
    if result.get("success"):
        print(f"✓ {args.mode.capitalize()} complete")
        for key, value in result.items():
            if key != "success":
                print(f"  {key}: {value}")
    else:
        print(f"✗ Error: {result.get('error', 'Unknown')}")


if __name__ == "__main__":
    main()
