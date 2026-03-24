#!/usr/bin/env python3
"""
Advanced Budget Calculator - Income, expenses, savings goals, trip planning
"""
import json
from pathlib import Path
from datetime import datetime, timedelta

class BudgetCalculator:
    def __init__(self):
        self.data_file = Path.home() / ".openclaw" / "workspace" / "memory" / "budget_data.json"
        self.data = self._load_data()
    
    def _load_data(self):
        if self.data_file.exists():
            with open(self.data_file) as f:
                return json.load(f)
        return {"profiles": {}, "savings_goals": [], "trips": []}
    
    def _save_data(self):
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.data_file, "w") as f:
            json.dump(self.data, f, indent=2)
    
    def calculate_weekly(self, income, expenses_dict):
        """Calculate weekly budget"""
        total_expenses = sum(expenses_dict.values())
        surplus = income - total_expenses
        monthly_surplus = surplus * 4.33
        yearly_surplus = surplus * 52
        
        return {
            "income": income,
            "expenses": total_expenses,
            "surplus": surplus,
            "monthly_surplus": monthly_surplus,
            "yearly_surplus": yearly_surplus,
            "breakdown": expenses_dict
        }
    
    def calculate_savings_timeline(self, target_amount, weekly_savings):
        """Calculate how long to reach savings goal"""
        if weekly_savings <= 0:
            return None
        
        weeks_needed = target_amount / weekly_savings
        target_date = datetime.now() + timedelta(weeks=weeks_needed)
        
        return {
            "weeks": round(weeks_needed, 1),
            "months": round(weeks_needed / 4.33, 1),
            "target_date": target_date.strftime("%Y-%m-%d"),
            "weekly_savings": weekly_savings
        }
    
    def compare_scenarios(self, scenarios):
        """Compare multiple budget scenarios"""
        results = []
        for name, (income, expenses) in scenarios.items():
            calc = self.calculate_weekly(income, expenses)
            calc["name"] = name
            results.append(calc)
        
        return results
    
    def affordability_check(self, weekly_surplus, target_cost, weeks_available=4):
        """Check if target is affordable"""
        total_available = weekly_surplus * weeks_available
        
        if total_available >= target_cost:
            return {
                "affordable": True,
                "cost": target_cost,
                "available": total_available,
                "remaining": total_available - target_cost,
                "weeks_needed": weeks_available
            }
        else:
            shortfall = target_cost - total_available
            weeks_needed = shortfall / weekly_surplus if weekly_surplus > 0 else float('inf')
            
            return {
                "affordable": False,
                "cost": target_cost,
                "available": total_available,
                "shortfall": shortfall,
                "weeks_needed": round(weeks_needed, 1)
            }
    
    def interactive(self):
        """Interactive budget session"""
        print("=" * 60)
        print("      LUX BUDGET CALCULATOR v2.0")
        print("=" * 60)
        print()
        
        # Get income
        print("💰 INCOME")
        print("-" * 40)
        weekly = float(input("Weekly income: $").strip() or "0")
        print()
        
        # Get expenses
        print("💸 EXPENSES")
        print("-" * 40)
        print("(Press Enter for $0)\n")
        
        expenses = {}
        categories = [
            ("rent", "Rent/Mortgage"),
            ("car", "Car payment"),
            ("fuel", "Fuel"),
            ("insurance", "Insurance"),
            ("groceries", "Groceries"),
            ("dining", "Dining out"),
            ("utilities", "Utilities"),
            ("subscriptions", "Subscriptions"),
            ("entertainment", "Entertainment"),
            ("savings", "Savings contribution"),
            ("other", "Other expenses")
        ]
        
        for key, label in categories:
            val = input(f"  {label:<20} $").strip()
            expenses[key] = float(val) if val else 0
        
        # Calculate
        budget = self.calculate_weekly(weekly, expenses)
        
        # Display
        print()
        print("=" * 60)
        print("      BUDGET BREAKDOWN")
        print("=" * 60)
        print()
        
        print(f"  Weekly Income:     ${budget['income']:>12,.2f}")
        print(f"  Weekly Expenses:   ${budget['expenses']:>12,.2f}")
        print(f"  Weekly Surplus:    ${budget['surplus']:>12,.2f}")
        print()
        print(f"  Monthly Surplus:   ${budget['monthly_surplus']:>12,.2f}")
        print(f"  Yearly Surplus:    ${budget['yearly_surplus']:>12,.2f}")
        print()
        
        # Expense breakdown
        print("  EXPENSE BREAKDOWN:")
        for key, amount in expenses.items():
            if amount > 0:
                pct = (amount / weekly * 100) if weekly > 0 else 0
                print(f"    {key:<18} ${amount:>10,.2f} ({pct:5.1f}%)")
        print()
        
        # Status
        if budget['surplus'] > 0:
            print(f"  ✅ POSITIVE: +${budget['surplus']:,.2f}/week")
            print(f"     Yearly savings potential: ${budget['yearly_surplus']:,.2f}")
        elif budget['surplus'] < 0:
            print(f"  ❌ NEGATIVE: ${budget['surplus']:,.2f}/week")
            print(f"     Deficit: ${abs(budget['surplus']):,.2f}/week")
        else:
            print(f"  ⚖️  BREAK EVEN")
        
        print()
        
        # Savings goals
        print("=" * 60)
        print("      SAVINGS GOALS")
        print("=" * 60)
        print()
        
        if budget['surplus'] > 0:
            target = float(input("Savings goal amount: $").strip() or "0")
            if target > 0:
                timeline = self.calculate_savings_timeline(target, budget['surplus'])
                if timeline:
                    print(f"\n  💰 Target: ${target:,.2f}")
                    print(f"  📅 Timeline: {timeline['weeks']} weeks ({timeline['months']} months)")
                    print(f"  🎯 Date: {timeline['target_date']}")
                    print(f"  💵 Weekly savings: ${timeline['weekly_savings']:,.2f}")
                else:
                    print("\n  ❌ Impossible with current surplus")
        
        # Affordability check
        print()
        print("=" * 60)
        print("      AFFORDABILITY CHECK")
        print("=" * 60)
        print()
        
        if budget['surplus'] > 0:
            target = float(input("Cost of item/trip: $").strip() or "0")
            if target > 0:
                weeks = int(input("Weeks to save (default 4): ").strip() or "4")
                result = self.affordability_check(budget['surplus'], target, weeks)
                
                print()
                if result['affordable']:
                    print(f"  ✅ AFFORDABLE")
                    print(f"     Cost: ${result['cost']:,.2f}")
                    print(f"     Available: ${result['available']:,.2f}")
                    print(f"     Remaining: ${result['remaining']:,.2f}")
                else:
                    print(f"  ❌ NOT AFFORDABLE")
                    print(f"     Cost: ${result['cost']:,.2f}")
                    print(f"     Shortfall: ${result['shortfall']:,.2f}")
                    print(f"     Need {result['weeks_needed']} more weeks")
        
        print()
        print("=" * 60)
        
        # Save profile
        save = input("\nSave this budget profile? (y/n): ").strip().lower()
        if save == 'y':
            name = input("Profile name: ").strip() or f"budget_{datetime.now().strftime('%Y%m%d')}"
            self.data["profiles"][name] = {
                "weekly_income": weekly,
                "expenses": expenses,
                "created": datetime.now().isoformat()
            }
            self._save_data()
            print(f"✅ Saved profile: {name}")

if __name__ == "__main__":
    calc = BudgetCalculator()
    calc.interactive()
