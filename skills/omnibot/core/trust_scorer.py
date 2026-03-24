"""
Trust Scoring System.
Provides confidence scores and reasoning for all outputs.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import re

@dataclass
class TrustScore:
    """Trust scoring result."""
    confidence: float  # 0-100
    reasoning: str
    risk_level: str  # low, medium, high
    alternative_approaches: List[str]
    verification_checks: List[str]

class TrustScorer:
    """
    Calculates trust scores for Omnibot outputs.
    Builds user trust through transparency.
    """
    
    def __init__(self):
        self.scoring_history = []
    
    def calculate(self, output_type: str, data: Dict) -> TrustScore:
        """
        Calculate trust score for an output.
        
        Args:
            output_type: Type of output (code, research, design, etc.)
            data: Output data and metadata
            
        Returns:
            TrustScore with confidence and reasoning
        """
        # Base confidence
        base_confidence = self._calculate_base_confidence(output_type, data)
        
        # Apply modifiers
        modifiers = self._apply_confidence_modifiers(output_type, data)
        confidence = max(0, min(100, base_confidence + modifiers))
        
        # Generate reasoning
        reasoning = self._generate_reasoning(output_type, data, confidence)
        
        # Determine risk level
        risk_level = self._assess_risk(output_type, data)
        
        # Suggest alternatives
        alternatives = self._suggest_alternatives(output_type, data)
        
        # Verification checklist
        checks = self._generate_verification_checks(output_type, data)
        
        score = TrustScore(
            confidence=confidence,
            reasoning=reasoning,
            risk_level=risk_level,
            alternative_approaches=alternatives,
            verification_checks=checks
        )
        
        self.scoring_history.append({
            "type": output_type,
            "confidence": confidence,
            "data_summary": str(data)[:500]
        })
        
        return score
    
    def _calculate_base_confidence(self, output_type: str, data: Dict) -> float:
        """Calculate base confidence based on output type."""
        base_scores = {
            "code": 75,  # Code can have bugs
            "research": 70,  # Information may be outdated
            "design": 80,  # Design is subjective
            "calculation": 95,  # Math is precise
            "file_read": 99,  # File reads are deterministic
            "external_api": 60,  # APIs can fail or change
            "recommendation": 65,  # Recommendations are opinionated
            "prediction": 50   # Predictions are uncertain
        }
        
        for pattern, score in base_scores.items():
            if pattern in output_type.lower():
                return score
        
        return 70  # Default
    
    def _apply_confidence_modifiers(self, output_type: str, data: Dict) -> float:
        """Apply confidence modifiers based on data quality."""
        modifiers = []
        
        # Data completeness
        if data.get("complete", False):
            modifiers.append(5)
        else:
            modifiers.append(-10)
        
        # Verified sources
        if data.get("verified_sources"):
            modifiers.append(10)
        
        # Error presence
        if data.get("errors") or data.get("warnings"):
            modifiers.append(-15)
        
        # User confirmation
        if data.get("user_confirmed"):
            modifiers.append(10)
        
        # Auto-generated vs curated
        if data.get("auto_generated", False):
            modifiers.append(-5)
        
        return sum(modifiers)
    
    def _generate_reasoning(self, output_type: str, data: Dict, 
                          confidence: float) -> str:
        """Generate human-readable reasoning for confidence score."""
        reasons = []
        
        if confidence >= 90:
            reasons.append("High confidence based on verifiable data and established patterns.")
        elif confidence >= 70:
            reasons.append("Good confidence with some assumptions or incomplete information.")
        elif confidence >= 50:
            reasons.append("Moderate confidence; verify before acting on this information.")
        else:
            reasons.append("Low confidence; significant uncertainty or missing data.")
        
        # Add specific reasonings
        if output_type == "code":
            if data.get("tested"):
                reasons.append("Code has been tested.")
            else:
                reasons.append("Code has not been executed/tested yet.")
        
        if output_type == "research":
            if data.get("sources"):
                reasons.append(f"Based on {len(data['sources'])} sources.")
            else:
                reasons.append("No source verification performed.")
        
        return " ".join(reasons)
    
    def _assess_risk(self, output_type: str, data: Dict) -> str:
        """Assess risk level of the output."""
        high_risk_types = ["delete", "modify_production", "financial", "security"]
        
        for risk_type in high_risk_types:
            if risk_type in output_type.lower() or risk_type in str(data).lower():
                return "high"
        
        if data.get("irreversible", False):
            return "high"
        
        if data.get("financial_impact"):
            return "medium"
        
        return "low"
    
    def _suggest_alternatives(self, output_type: str, data: Dict) -> List[str]:
        """Suggest alternative approaches if confidence is low."""
        alternatives = []
        
        if output_type == "code":
            alternatives.append("Consider running the code in a sandbox first.")
            alternatives.append("Have another agent review the code.")
        
        if output_type == "research":
            alternatives.append("Cross-reference with additional sources.")
            alternatives.append("Request user confirmation of findings.")
        
        if output_type == "design":
            alternatives.append("Get feedback from design perspective.")
            alternatives.append("Consider A/B testing the design.")
        
        return alternatives
    
    def _generate_verification_checks(self, output_type: str, data: Dict) -> List[str]:
        """Generate verification checklist items."""
        checks = []
        
        if output_type == "code":
            checks.append("☐ Code reviewed for syntax errors")
            checks.append("☐ No hardcoded secrets or credentials")
            checks.append("☐ Error handling implemented")
            checks.append("☐ Test cases considered")
        
        if output_type == "research":
            checks.append("☐ Sources verified")
            checks.append("☐ Timestamp checked for freshness")
            checks.append("☐ Information cross-referenced")
        
        if output_type == "design":
            checks.append("☐ WCAG accessibility standards met")
            checks.append("☐ Mobile responsive considered")
            checks.append("☐ Color contrast sufficient")
        
        return checks
    
    def format_score(self, score: TrustScore) -> str:
        """Format trust score for display."""
        lines = [
            f"📊 Trust Score: {score.confidence}% ({score.risk_level} risk)",
            f"",
            f"📝 Reasoning:",
            f"   {score.reasoning}",
            f"",
            f"✅ Verification:",
        ]
        for check in score.verification_checks:
            lines.append(f"   {check}")
        
        if score.alternative_approaches:
            lines.extend([
                f"",
                f"💡 Alternatives:",
            ])
            for alt in score.alternative_approaches:
                lines.append(f"   • {alt}")
        
        return "\n".join(lines)