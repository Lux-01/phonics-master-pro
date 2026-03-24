"""
AOE v2.0 - Test Suite
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Fix imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from aoe_v2.scanner_base import Token, ScannerBase
from aoe_v2.scorer import OpportunityScorer, ScoreBreakdown


class TestToken:
    """Test Token data class."""
    
    def test_token_creation(self):
        token = Token(
            address="TEST123",
            symbol="TEST",
            name="Test Token"
        )
        assert token.address == "TEST123"
        assert token.symbol == "TEST"
        assert token.sources == [""]
    
    def test_token_properties(self):
        token = Token(
            address="TEST",
            symbol="TST",
            market_cap=100000,
            volume_24h=50000,
            liquidity=30000,
            buys_24h=60,
            sells_24h=40
        )
        
        assert token.vol_mc_ratio == 0.5
        assert token.liq_mc_ratio == 0.3
        assert token.buy_ratio == 0.6


class TestOpportunityScorer:
    """Test opportunity scoring."""
    
    @pytest.fixture
    def sample_token(self):
        token = Token(
            address="TEST",
            symbol="AIOP",
            name="AI Opportunity Token",
            chain_id="solana",
            price=0.001,
            market_cap=500_000,
            liquidity=150_000,
            volume_24h=200_000,
            price_change_1h=-12,
            price_change_24h=45,
            txns_24h=850,
            buys_24h=520,
            sells_24h=330,
            holders=1200
        )
        token.__dict__['narratives'] = ['ai']
        token.__dict__['age_hours'] = 3
        token.__dict__['vol_spike_5m'] = 3.5
        return token
    
    def test_scorer_creation(self):
        scorer = OpportunityScorer(strategy="mean_reversion_microcap")
        assert scorer.strategy == "mean_reversion_microcap"
        assert 'potential' in scorer.weights
    
    def test_score_potential(self, sample_token):
        scorer = OpportunityScorer()
        score = scorer._score_potential(sample_token)
        
        # 500K MC should get good potential score
        assert 50 <= score <= 100
    
    def test_score_probability(self, sample_token):
        scorer = OpportunityScorer()
        score = scorer._score_probability(sample_token)
        
        # High vol/MC ratio should give good score
        assert 40 <= score <= 100
    
    def test_score_speed(self, sample_token):
        scorer = OpportunityScorer()
        score = scorer._score_speed(sample_token)
        
        # 3h age should be time-sensitive
        assert 50 <= score <= 100
    
    def test_score_fit_mean_reversion(self, sample_token):
        scorer = OpportunityScorer(strategy="mean_reversion_microcap")
        score = scorer._score_fit(sample_token)
        
        # -12% dip is ideal for mean reversion
        assert score > 60
    
    def test_score_risk(self, sample_token):
        scorer = OpportunityScorer()
        score = scorer._score_risk(sample_token)
        
        # Should have moderate risk
        assert 20 <= score <= 60
    
    def test_full_score_calculation(self, sample_token):
        scorer = OpportunityScorer()
        total, breakdown = scorer.score(sample_token)
        
        # Should be reasonable score (70-95 range expected)
        assert 50 <= total <= 100
        assert breakdown.total > 0
    
    def test_batch_scoring(self):
        tokens = [
            Token(address=f"TEST{i}", symbol=f"T{i}", market_cap=500000)
            for i in range(5)
        ]
        
        scorer = OpportunityScorer()
        results = scorer.score_batch(tokens)
        
        assert len(results) == 5
        # Should be sorted by score
        scores = [r[1] for r in results]
        assert scores == sorted(scores, reverse=True)


class TestBreakdown:
    """Test score breakdown."""
    
    def test_calculate_total(self):
        weights = {
            "potential": 0.25,
            "probability": 0.25,
            "speed": 0.15,
            "fit": 0.15,
            "alpha": 0.20,
            "risk": 0.20,
            "effort": 0.10
        }
        
        breakdown = ScoreBreakdown(
            potential=80,
            probability=70,
            speed=60,
            fit=75,
            alpha=85,
            risk=30,
            effort=20
        )
        
        total = breakdown.calculate_total(weights)
        
        # Rough check
        assert 50 <= total <= 90
    
    def test_to_dict(self):
        breakdown = ScoreBreakdown(
            potential=80,
            probability=70,
            speed=60,
            fit=75,
            alpha=85,
            risk=30,
            effort=20
        )
        
        d = breakdown.to_dict()
        assert 'potential' in d
        assert 'total' in d
        assert isinstance(d['potential'], float)


class TestAlertManager:
    """Test alert system (requires mocks)."""
    
    @pytest.fixture
    def mock_token(self):
        token = Token(
            address="TEST123",
            symbol="ALERT",
            name="Test Alert Token",
            price=0.001,
            market_cap=500_000,
            volume_24h=200_000,
            price_change_1h=-14,
            price_change_24h=35,
            txns_24h=650,
            buys_24h=420,
            sells_24h=230
        )
        token.__dict__['narratives'] = ['ai']
        token.__dict__['age_hours'] = 2
        return token
    
    def test_determine_action(self):
        # Need to import here after path setup
        from aoe_v2.alerts import AlertManager
        
        alerts = AlertManager()
        
        assert alerts._determine_action(85) == "alert"
        assert alerts._determine_action(78) == "queue"
        assert alerts._determine_action(70) == "log"
    
    def test_format_telegram_message(self, mock_token):
        from aoe_v2.alerts import AlertManager, Alert
        from aoe_v2.scorer import ScoreBreakdown
        
        alerts = AlertManager()
        
        breakdown = ScoreBreakdown(
            potential=80, probability=75, speed=70,
            fit=85, alpha=80, risk=40, effort=25,
            total=85
        )
        
        alert = Alert(
            token=mock_token,
            score=85,
            breakdown=breakdown,
            level="urgent",
            timestamp=datetime.now().isoformat(),
            message="",
            action="Buy"
        )
        
        msg = alerts._format_telegram_message(alert)
        
        assert "ALERT" in msg
        assert "85" in msg
        assert "AI Opportunity Token" in msg


class TestIntegration:
    """Integration tests."""
    
    def test_full_pipeline_mock(self):
        """Test full pipeline with mock data."""
        from aoe_v2.token_pipeline import TokenPipeline
        from aoe_v2.scorer import OpportunityScorer
        
        # Create mock scanner
        mock_scanner = Mock()
        mock_scanner.fetch_with_retry.return_value = [
            Token(
                address=f"ADDR{i}",
                symbol=f"TOK{i}",
                name=f"Token {i}",
                market_cap=500000 + i * 100000,
                volume_24h=100000 + i * 50000,
                price_change_1h=-10 - i
            )
            for i in range(10)
        ]
        mock_scanner.name = "mock"
        
        # Run pipeline
        pipeline = TokenPipeline(
            scanners=[mock_scanner],
            mc_min=100_000,
            mc_max=20_000_000
        )
        
        tokens, stats = pipeline.run(parallel=False)
        
        assert len(tokens) > 0
        assert 'raw_count' in stats
        assert 'unique_count' in stats
        
        # Score
        scorer = OpportunityScorer()
        results = scorer.score_batch(tokens)
        
        assert len(results) > 0
        
        # Get top
        top = scorer.get_top_opportunities(results, min_score=70)
        assert isinstance(top, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
