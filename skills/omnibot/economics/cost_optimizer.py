#!/usr/bin/env python3
"""
Cost Optimizer - Tracks every API call, every token spent:
"This research task cost $0.47. Expected value: $50. ROI: 10,000%"

Suggests cheaper alternatives:
"OpenAI GPT-4: $0.03 per request → Local Ollama: $0 (slower). Switch?"
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import threading


class CostCategory(Enum):
    """Categories of costs."""
    API_CALL = "api_call"
    TOKENS = "tokens"
    COMPUTE = "compute"
    STORAGE = "storage"
    BANDWIDTH = "bandwidth"
    LICENSE = "license"


class Provider(Enum):
    """Service providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE = "azure"
    OLLAMA = "ollama"
    LOCAL = "local"
    BRAVE = "brave"
    BIRDEYE = "birdeye"


@dataclass
class CostEntry:
    """A single cost entry."""
    entry_id: str
    timestamp: datetime
    category: CostCategory
    provider: Provider
    service: str
    units: float  # tokens, seconds, GB, etc.
    unit_cost: float  # cost per unit
    total_cost: float
    task_id: Optional[str]
    metadata: Dict[str, Any]


@dataclass
class TaskBudget:
    """Budget for a specific task."""
    task_id: str
    estimated_cost: float
    actual_cost: float = 0.0
    alerts_enabled: bool = True
    alert_threshold_percent: float = 80.0


class CostOptimizer:
    """
    Tracks all costs and provides optimization recommendations.
    """
    
    # Pricing data (per 1000 tokens or per request)
    PRICING = {
        Provider.OPENAI: {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015}
        },
        Provider.ANTHROPIC: {
            "claude-3-opus": {"input": 0.015, "output": 0.075},
            "claude-3-sonnet": {"input": 0.003, "output": 0.015},
            "claude-3-haiku": {"input": 0.00025, "output": 0.00125}
        },
        Provider.OLLAMA: {
            "default": {"input": 0.0, "output": 0.0}  # Free, local
        },
        Provider.LOCAL: {
            "default": {"input": 0.0, "output": 0.0}
        },
        Provider.BRAVE: {
            "search": {"request": 0.003}
        },
        Provider.BIRDEYE: {
            "api": {"request": 0.0}  # Freemium
        }
    }
    
    def __init__(self, omnibot=None, data_dir: Optional[str] = None, daily_budget: float = 100.0):
        self.logger = logging.getLogger("Omnibot.CostOptimizer")
        self.omnibot = omnibot
        
        # Storage
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent / "cost_data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Cost tracking
        self.costs: List[CostEntry] = []
        self.task_budgets: Dict[str, TaskBudget] = {}
        self.daily_budget = daily_budget
        self.spent_today = 0.0
        
        # Alternatives cache
        self.alternatives_cache: Dict[str, Dict] = {}
        
        # Lock for thread safety
        self._lock = threading.Lock()
        
        # Load existing data
        self._load_costs()
        self._calculate_daily_spend()
        
        self.logger.info(f"CostOptimizer initialized (daily budget: ${daily_budget})")
    
    def _load_costs(self):
        """Load cost history."""
        costs_file = self.data_dir / "cost_history.json"
        if costs_file.exists():
            try:
                data = json.loads(costs_file.read_text())
                self.costs = [CostEntry(**c) for c in data.get("costs", [])]
                self.logger.info(f"Loaded {len(self.costs)} cost entries")
            except Exception as e:
                self.logger.error(f"Failed to load costs: {e}")
    
    def _save_costs(self):
        """Save cost history."""
        try:
            costs_file = self.data_dir / "cost_history.json"
            data = {
                "last_updated": datetime.now().isoformat(),
                "daily_budget": self.daily_budget,
                "spent_today": self.spent_today,
                "costs": [asdict(c) for c in self.costs[-1000:]]  # Keep last 1000
            }
            costs_file.write_text(json.dumps(data, indent=2, default=str))
        except Exception as e:
            self.logger.error(f"Failed to save costs: {e}")
    
    def _calculate_daily_spend(self):
        """Calculate today's spending."""
        today = datetime.now().date()
        self.spent_today = sum(
            c.total_cost for c in self.costs
            if c.timestamp.date() == today
        )
    
    # ==================== COST TRACKING ====================
    
    def track_api_call(self, provider: Provider, service: str, units: float,
                      unit_cost: Optional[float] = None,
                      task_id: Optional[str] = None,
                      metadata: Optional[Dict] = None) -> CostEntry:
        """
        Track an API call cost.
        
        Args:
            provider: Service provider
            service: Specific service/model
            units: Number of units (tokens, requests, etc.)
            unit_cost: Cost per unit (auto-calculated if None)
            task_id: Associated task
            metadata: Additional info
            
        Returns:
            CostEntry
        """
        # Auto-calculate unit cost if not provided
        if unit_cost is None:
            unit_cost = self._get_unit_cost(provider, service)
        
        total_cost = units * unit_cost / 1000  # Pricing is per 1000
        
        entry = CostEntry(
            entry_id=f"cost_{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            category=CostCategory.API_CALL,
            provider=provider,
            service=service,
            units=units,
            unit_cost=unit_cost,
            total_cost=total_cost,
            task_id=task_id,
            metadata=metadata or {}
        )
        
        with self._lock:
            self.costs.append(entry)
            self.spent_today += total_cost
        
        # Check budget alert
        if task_id and task_id in self.task_budgets:
            self._check_task_budget(task_id)
        
        self._save_costs()
        self.logger.debug(f"Tracked cost: ${total_cost:.4f} for {service}")
        
        return entry
    
    def track_token_usage(self, provider: Provider, model: str,
                         input_tokens: int, output_tokens: int,
                         task_id: Optional[str] = None) -> CostEntry:
        """
        Track LLM token usage cost.
        
        Args:
            provider: LLM provider
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            task_id: Associated task
            
        Returns:
            CostEntry
        """
        pricing = self.PRICING.get(provider, {}).get(model, {"input": 0.0, "output": 0.0})
        input_cost = input_tokens * pricing["input"] / 1000
        output_cost = output_tokens * pricing["output"] / 1000
        total_units = input_tokens + output_tokens
        total_cost = input_cost + output_cost
        
        entry = CostEntry(
            entry_id=f"cost_{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            category=CostCategory.TOKENS,
            provider=provider,
            service=model,
            units=total_units,
            unit_cost=pricing["input"],  # Store input pricing
            total_cost=total_cost,
            task_id=task_id,
            metadata={"input_tokens": input_tokens, "output_tokens": output_tokens}
        )
        
        with self._lock:
            self.costs.append(entry)
            self.spent_today += total_cost
        
        self._save_costs()
        self.logger.debug(f"Tracked {total_units} tokens from {provider.value} {model}: ${total_cost:.4f}")
        
        return entry
    
    def _get_unit_cost(self, provider: Provider, service: str) -> float:
        """Get unit cost from pricing table."""
        provider_pricing = self.PRICING.get(provider, {})
        service_pricing = provider_pricing.get(service, provider_pricing.get("default", {"input": 0.0}))
        return service_pricing.get("input", 0.0)
    
    def _check_task_budget(self, task_id: str):
        """Check if task is approaching budget limit."""
        budget = self.task_budgets.get(task_id)
        if not budget or not budget.alerts_enabled:
            return
        
        spent_percent = (budget.actual_cost / budget.estimated_cost) * 100
        
        if spent_percent >= budget.alert_threshold_percent:
            self.logger.warning(
                f"Task {task_id} at {spent_percent:.1f}% of budget "
                f"(${budget.actual_cost:.2f} / ${budget.estimated_cost:.2f})"
            )
    
    # ==================== BUDGET MANAGEMENT ====================
    
    def set_task_budget(self, task_id: str, estimated_cost: float,
                       alert_threshold: float = 80.0) -> TaskBudget:
        """
        Set a budget for a task.
        
        Args:
            task_id: Task identifier
            estimated_cost: Estimated cost
            alert_threshold: Percentage to alert at
            
        Returns:
            TaskBudget
        """
        budget = TaskBudget(
            task_id=task_id,
            estimated_cost=estimated_cost,
            alert_threshold_percent=alert_threshold
        )
        
        self.task_budgets[task_id] = budget
        self.logger.info(f"Set budget for task {task_id}: ${estimated_cost:.2f}")
        
        return budget
    
    # ==================== COST ANALYSIS ====================
    
    def get_task_cost(self, task_id: str) -> Dict:
        """
        Get total cost for a task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Cost breakdown
        """
        task_costs = [c for c in self.costs if c.task_id == task_id]
        
        if not task_costs:
            return {"error": "No costs found for task"}
        
        total = sum(c.total_cost for c in task_costs)
        by_provider = {}
        by_category = {}
        
        for cost in task_costs:
            provider = cost.provider.value
            by_provider[provider] = by_provider.get(provider, 0) + cost.total_cost
            
            category = cost.category.value
            by_category[category] = by_category.get(category, 0) + cost.total_cost
        
        return {
            "task_id": task_id,
            "total_cost": total,
            "call_count": len(task_costs),
            "by_provider": by_provider,
            "by_category": by_category,
            "budget": self.task_budgets.get(task_id, {}).estimated_cost if task_id in self.task_budgets else None
        }
    
    def get_daily_summary(self) -> Dict:
        """Get today's cost summary."""
        today = datetime.now().date()
        today_costs = [c for c in self.costs if c.timestamp.date() == today]
        
        total = sum(c.total_cost for c in today_costs)
        by_provider = {}
        by_service = {}
        
        for cost in today_costs:
            provider = cost.provider.value
            by_provider[provider] = by_provider.get(provider, 0) + cost.total_cost
            
            service = f"{provider}:{cost.service}"
            by_service[service] = by_service.get(service, 0) + cost.total_cost
        
        return {
            "date": today.isoformat(),
            "total_cost": total,
            "budget": self.daily_budget,
            "remaining": self.daily_budget - total,
            "percent_used": (total / self.daily_budget) * 100 if self.daily_budget > 0 else 0,
            "call_count": len(today_costs),
            "by_provider": by_provider,
            "top_services": sorted(by_service.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    def get_roi_report(self, task_id: str, expected_value: float) -> Dict:
        """
        Calculate ROI for a task.
        
        Args:
            task_id: Task identifier
            expected_value: Expected monetary value of task
            
        Returns:
            ROI report
        """
        cost_data = self.get_task_cost(task_id)
        
        if "error" in cost_data:
            return cost_data
        
        total_cost = cost_data["total_cost"]
        roi = ((expected_value - total_cost) / total_cost * 100) if total_cost > 0 else float('inf')
        
        return {
            "task_id": task_id,
            "cost": total_cost,
            "expected_value": expected_value,
            "roi_percent": roi,
            "roi_multiple": expected_value / total_cost if total_cost > 0 else float('inf'),
            "verdict": "Profitable" if roi > 0 else "Loss",
            "summary": f"This task cost ${total_cost:.2f}. Expected value: ${expected_value:.2f}. ROI: {roi:.0f}%"
        }
    
    # ==================== OPTIMIZATION SUGGESTIONS ====================
    
    def suggest_cheaper_alternative(self, current_provider: Provider, 
                                    current_service: str) -> Optional[Dict]:
        """
        Suggest cheaper alternatives.
        
        Args:
            current_provider: Current provider
            current_service: Current service/model
            
        Returns:
            Alternative suggestion or None
        """
        # Cache key
        cache_key = f"{current_provider.value}:{current_service}"
        if cache_key in self.alternatives_cache:
            return self.alternatives_cache[cache_key]
        
        current_cost = self._get_unit_cost(current_provider, current_service)
        if current_cost == 0:
            return None  # Already free
        
        alternatives = []
        
        # Find cheaper options
        for provider, services in self.PRICING.items():
            if provider == current_provider:
                continue
            
            for service, pricing in services.items():
                cost = pricing.get("input", 0)
                if cost < current_cost:
                    savings_pct = ((current_cost - cost) / current_cost) * 100
                    alternatives.append({
                        "provider": provider.value,
                        "service": service,
                        "cost_per_1k": cost,
                        "savings_percent": savings_pct,
                        "tradeoffs": self._get_tradeoffs(provider)
                    })
        
        if alternatives:
            # Sort by savings
            alternatives.sort(key=lambda x: x["savings_percent"], reverse=True)
            best = alternatives[0]
            
            suggestion = {
                "current": f"{current_provider.value} {current_service}",
                "current_cost": current_cost,
                "suggested": f"{best['provider']} {best['service']}",
                "suggested_cost": best["cost_per_1k"],
                "savings_percent": best["savings_percent"],
                "tradeoffs": best["tradeoffs"],
                "verdict": f"{best['provider'].upper()}: ${current_cost:.4f} → ${best['cost_per_1k']:.4f} per 1K tokens ({best['savings_percent']:.0f}% cheaper)"
            }
            
            self.alternatives_cache[cache_key] = suggestion
            return suggestion
        
        return None
    
    def _get_tradeoffs(self, provider: Provider) -> List[str]:
        """Get tradeoffs for a provider."""
        tradeoffs = {
            Provider.OLLAMA: ["Slower response time", "Requires local setup", "Hardware dependent"],
            Provider.LOCAL: ["Requires local compute", "Limited model selection"],
            Provider.ANTHROPIC: ["Different API format", "May require code changes"],
            Provider.OPENAI: ["Industry standard", "Higher cost"],
        }
        return tradeoffs.get(provider, ["May require API key changes"])
    
    def analyze_spending_trends(self, days: int = 7) -> Dict:
        """
        Analyze spending trends over time.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Trend analysis
        """
        cutoff = datetime.now() - timedelta(days=days)
        recent_costs = [c for c in self.costs if c.timestamp >= cutoff]
        
        if not recent_costs:
            return {"error": "No data for period"}
        
        # Daily breakdown
        daily_spend = {}
        for cost in recent_costs:
            day = cost.timestamp.strftime("%Y-%m-%d")
            daily_spend[day] = daily_spend.get(day, 0) + cost.total_cost
        
        total = sum(daily_spend.values())
        average = total / len(daily_spend) if daily_spend else 0
        
        return {
            "period_days": days,
            "total_spend": total,
            "daily_average": average,
            "daily_breakdown": daily_spend,
            "trend": "increasing" if daily_spend.get(max(daily_spend.keys()), 0) > average else "stable",
            "optimization_opportunities": self._find_optimization_opportunities(recent_costs)
        }
    
    def _find_optimization_opportunities(self, costs: List[CostEntry]) -> List[Dict]:
        """Find potential cost optimizations."""
        opportunities = []
        
        # Group by service
        by_service = {}
        for cost in costs:
            key = f"{cost.provider.value}:{cost.service}"
            by_service[key] = by_service.get(key, 0) + cost.total_cost
        
        # Find services with high spend
        for service, spend in sorted(by_service.items(), key=lambda x: x[1], reverse=True)[:3]:
            if spend > 1.0:  # Over $1
                provider_name = service.split(":")[0]
                provider = Provider(provider_name) if provider_name in [p.value for p in Provider] else Provider.OPENAI
                
                alt = self.suggest_cheaper_alternative(provider, service.split(":")[1])
                if alt:
                    opportunities.append({
                        "service": service,
                        "current_spend": spend,
                        "suggestion": alt
                    })
        
        return opportunities
    
    # ==================== REPORTING ====================
    
    def generate_cost_report(self, period_days: int = 30) -> str:
        """Generate a human-readable cost report."""
        summary = self.get_daily_summary()
        trends = self.analyze_spending_trends(period_days)
        
        report = f"""
💰 OMNIBOT COST REPORT
{'='*50}

📊 TODAY'S SPENDING
- Total: ${summary['total_cost']:.4f}
- Budget: ${summary['budget']:.2f}
- Remaining: ${summary['remaining']:.2f}
- Status: {'⚠️ Over Budget!' if summary['total_cost'] > summary['budget'] else '✅ On Track'}

📈 {period_days}-DAY TRENDS
- Average Daily: ${trends.get('daily_average', 0):.4f}
- Trend: {trends.get('trend', 'unknown')}

🔝 TOP SERVICES (Today)
"""
        for service, cost in summary.get('top_services', []):
            report += f"- {service}: ${cost:.4f}\n"
        
        if trends.get('optimization_opportunities'):
            report += "\n💡 OPTIMIZATION OPPORTUNITIES\n"
            for opp in trends['optimization_opportunities']:
                report += f"- {opp['suggestion']['verdict']}\n"
        
        report += f"\n{'='*50}\nGenerated: {datetime.now().isoformat()}\n"
        
        return report
    
    # ==================== UTILITIES ====================
    
    def get_spending_forecast(self, days_ahead: int = 7) -> Dict:
        """Forecast spending based on trends."""
        trends = self.analyze_spending_trends(7)
        avg_daily = trends.get('daily_average', 0)
        
        forecast = avg_daily * days_ahead
        
        return {
            "forecast_for_days": days_ahead,
            "projected_spend": forecast,
            "daily_average": avg_daily,
            "will_exceed_budget": (self.spent_today + forecast) > self.daily_budget * 7
        }
    
    def reset_daily_counter(self):
        """Reset daily spend counter."""
        self.spent_today = 0.0
        self.logger.info("Daily spending counter reset")