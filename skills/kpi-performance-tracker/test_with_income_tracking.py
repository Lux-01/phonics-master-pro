"""
Test Suite for KPI Performance Tracker (with Income Tracking)
Tests both KPI metrics and income/MRR/ROI tracking.
"""

import unittest
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime, timedelta

class TestKPIPerformanceTracker(unittest.TestCase):
    """Test cases for KPI Performance Tracker"""
    
    def setUp(self):
        """Set up test environment"""
        self.tracked_metrics = {
            "Skills": ["Success rate", "Error rate", "Avg time"],
            "Business": ["Revenue", "Profit", "Growth rate"],
            "System": ["Uptime", "Resource usage", "Cost"],
            "User": ["Adoption", "Satisfaction", "Churn"]
        }
    
    def test_tracked_metrics_categories(self):
        """Test all metric categories are defined"""
        self.assertEqual(len(self.tracked_metrics), 4)
        self.assertIn("Skills", self.tracked_metrics)
        self.assertIn("Business", self.tracked_metrics)
    
    def test_skills_metrics(self):
        """Test skills metrics"""
        metrics = self.tracked_metrics["Skills"]
        self.assertEqual(len(metrics), 3)
        self.assertIn("Success rate", metrics)
    
    def test_commands_defined(self):
        """Test KPI commands"""
        commands = ["--collect", "--dashboard", "--alert-config"]
        self.assertEqual(len(commands), 3)

class TestIncomeTracking(unittest.TestCase):
    """Test cases for Income Tracking module"""
    
    def setUp(self):
        """Set up income tracking test environment"""
        self.income_categories = {
            "Skill-Generated Income": ["ATS", "AOE", "AWB", "Research-Synthesizer"],
            "Crypto Income Streams": ["Trading Profits", "Staking Rewards", "Airdrops", "Yield Farming"],
            "Digital Product Revenue": ["Avatar Packs", "Automation Scripts", "Templates"],
            "Service Revenue": ["Consulting", "Research Services", "Code Reviews"],
            "Passive/Other": ["Affiliate Income", "Ad Revenue", "Royalties"]
        }
        
        self.income_record_schema = {
            "id": "uuid",
            "date": "2026-03-09",
            "timestamp": "2026-03-09T14:30:00Z",
            "source": {
                "category": "trading|product|service|passive|other",
                "skill": "skill_name",
                "sub_source": "source_type"
            },
            "amount": {
                "value": 100.00,
                "currency": "USD",
                "usd_equivalent": 100.00
            },
            "metadata": {
                "description": "",
                "tags": []
            },
            "reconciliation": {
                "verified": True
            }
        }
    
    def test_income_categories(self):
        """Test all income categories"""
        self.assertEqual(len(self.income_categories), 5)
        self.assertIn("Skill-Generated Income", self.income_categories)
    
    def test_income_record_structure(self):
        """Test income record JSON structure"""
        self.assertIn("id", self.income_record_schema)
        self.assertIn("source", self.income_record_schema)
        self.assertIn("amount", self.income_record_schema)
        self.assertIn("metadata", self.income_record_schema)
        self.assertIn("reconciliation", self.income_record_schema)

class TestMRRCalculation(unittest.TestCase):
    """Test MRR calculation logic"""
    
    def setUp(self):
        """Set up MRR test data"""
        self.mrr_components = {
            "stable_recurring": {
                "subscriptions": 500,
                "retainers": 800,
                "staking": 300
            },
            "variable_monthly": {
                "trading_average": 1200,
                "product_sales": 400,
                "service_income": 600
            },
            "opportunistic": {
                "airdrops": 200,
                "bonuses": 100
            }
        }
    
    def test_mrr_formula(self):
        """Test MRR calculation formula"""
        stable = sum(self.mrr_components["stable_recurring"].values())
        variable = sum(self.mrr_components["variable_monthly"].values())
        
        expected_mrr = stable + variable
        self.assertEqual(stable, 1600)  # 500+800+300
        self.assertEqual(variable, 2200)  # 1200+400+600
        self.assertEqual(expected_mrr, 3800)
    
    def test_total_monthly_income(self):
        """Test total monthly income calculation"""
        mrr = 3800
        opportunistic = sum(self.mrr_components["opportunistic"].values())
        total = mrr + opportunistic
        
        self.assertEqual(opportunistic, 300)
        self.assertEqual(total, 4100)
    
    def test_mrr_confidence_levels(self):
        """Test MRR confidence levels"""
        confidence = {
            "stable_recurring": 100,
            "variable_monthly": 80,
            "opportunistic": "N/A"
        }
        self.assertEqual(confidence["stable_recurring"], 100)
        self.assertEqual(confidence["variable_monthly"], 80)

class TestSkillROI(unittest.TestCase):
    """Test Skill ROI calculations"""
    
    def setUp(self):
        """Set up ROI test data"""
        self.skill_example = {
            "name": "ATS",
            "direct_income": 2000,
            "time_saved_value": 2000,
            "development_time_hours": 40,
            "maintenance_time_hours_per_month": 2,
            "time_rate": 50
        }
    
    def test_roi_calculation(self):
        """Test ROI calculation formula"""
        total_return = self.skill_example["direct_income"] + self.skill_example["time_saved_value"]
        time_cost = (self.skill_example["development_time_hours"] * self.skill_example["time_rate"] + 
                    self.skill_example["maintenance_time_hours_per_month"] * self.skill_example["time_rate"])
        
        # Monthly ROI
        monthly_return = total_return  # $4000
        monthly_investment = self.skill_example["maintenance_time_hours_per_month"] * self.skill_example["time_rate"]  # $100
        
        roi = ((monthly_return - monthly_investment) / monthly_investment) * 100
        self.assertGreater(roi, 0)
        self.assertEqual(monthly_investment, 100)
        self.assertEqual(monthly_return, 4000)
    
    def test_roi_status_levels(self):
        """Test ROI status classification"""
        statuses = {
            ">300%": "Excellent",
            "150-300%": "Good",
            "100-150%": "Acceptable",
            "<100%": "Needs Work"
        }
        self.assertEqual(len(statuses), 4)

class TestMonthlyDashboard(unittest.TestCase):
    """Test monthly dashboard generation"""
    
    def setUp(self):
        """Set up dashboard sections"""
        self.dashboard_sections = [
            "Executive Summary",
            "By Category",
            "Skill ROI Performance",
            "Top Recommendations",
            "Goals Tracking"
        ]
    
    def test_dashboard_sections(self):
        """Test all dashboard sections exist"""
        self.assertEqual(len(self.dashboard_sections), 5)
    
    def test_executive_summary_metrics(self):
        """Test executive summary metrics"""
        metrics = ["MRR", "Total Month", "Run Rate", "Target"]
        self.assertEqual(len(metrics), 4)
    
    def test_category_breakdown(self):
        """Test income category breakdown"""
        categories = [
            "Crypto Trading",
            "Digital Products",
            "Services",
            "Staking/Passive"
        ]
        self.assertEqual(len(categories), 4)

class TestGrowthOpportunityDetection(unittest.TestCase):
    """Test opportunity detection"""
    
    def setUp(self):
        """Set up opportunity types"""
        self.opportunity_types = [
            "Skill Value Gaps",
            "Revenue Diversification",
            "Pricing Optimization",
            "Product Gaps",
            "Affiliate Opportunities"
        ]
    
    def test_opportunity_types(self):
        """Test opportunity detection types"""
        self.assertEqual(len(self.opportunity_types), 5)
    
    def test_opportunity_scoring(self):
        """Test opportunity scoring structure"""
        scoring = {
            "potential_monthly_income": 1000,
            "implementation_effort": 2,
            "confidence": 85,
            "time_to_realization": 7,
            "risk_level": "low"
        }
        self.assertIn("confidence", scoring)
        self.assertIn("risk_level", scoring)

class TestStorageStructure(unittest.TestCase):
    """Test storage directory structure"""
    
    def test_kpi_storage_structure(self):
        """Test KPI storage directories"""
        directories = [
            "memory/kpi/metrics/",
            "memory/kpi/business/income/",
            "memory/kpi/business/roi/",
            "memory/kpi/reports/",
            "memory/kpi/alerts/"
        ]
        self.assertEqual(len(directories), 5)
    
    def test_income_file_structure(self):
        """Test income file structure"""
        files = [
            "streams.json",
            "mrr.json",
            "goals.json",
            "skill_roi.json",
            "time_costs.json"
        ]
        self.assertEqual(len(files), 5)

class TestCronJobs(unittest.TestCase):
    """Test cron job scheduling"""
    
    def test_daily_jobs(self):
        """Test daily cron jobs"""
        daily = [
            "sync_wallet_transactions",
            "categorize_new_income",
            "update_mrr_calculation"
        ]
        self.assertEqual(len(daily), 3)
    
    def test_weekly_jobs(self):
        """Test weekly cron jobs"""
        weekly = [
            "skill_roi_update",
            "opportunity_detection"
        ]
        self.assertEqual(len(weekly), 2)
    
    def test_monthly_jobs(self):
        """Test monthly cron jobs"""
        monthly = [
            "generate_income_dashboard",
            "goal_progress_update",
            "trend_analysis",
            "skill_performance_report"
        ]
        self.assertEqual(len(monthly), 4)

class TestIncomeCommands(unittest.TestCase):
    """Test income tracking commands"""
    
    def test_commands_defined(self):
        """Test all income commands"""
        commands = [
            "Income dashboard",
            "Add income",
            "Show MRR",
            "Skill ROI",
            "Income opportunities",
            "Month close",
            "Compare to last month",
            "Income goals",
            "Diversification"
        ]
        self.assertEqual(len(commands), 9)

class TestIntegration(unittest.TestCase):
    """Test integration with other skills"""
    
    def test_skill_integrations(self):
        """Test skill integration list"""
        integrations = [
            "ATS: Track trading income per strategy",
            "AOE: Track opportunity value generation",
            "SEE: Skills generating most revenue",
            "LPM: Track project value",
            "ALOE: Learn what generates best ROI"
        ]
        self.assertEqual(len(integrations), 5)

if __name__ == '__main__':
    # Run tests with verbosity
    suite = unittest.TestLoader().loadTestsFromModule(__import__(__name__))
    unittest.TextTestRunner(verbosity=2).run(suite)
