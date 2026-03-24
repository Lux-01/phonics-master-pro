#!/usr/bin/env python3
"""
Negotiation Helper - Assist with rate and scope negotiations.
"""

import logging


class NegotiationHelper:
    """Assist with client negotiations."""
    
    def __init__(self, min_rate: float = 50.0):
        self.logger = logging.getLogger("Omnibot.NegotiationHelper")
        self.min_rate = min_rate
    
    def analyze_offer(self, offered_rate: float, scope: str) -> dict:
        """Analyze if offer is acceptable."""
        analysis = {
            "acceptable": offered_rate >= self.min_rate,
            "min_rate": self.min_rate,
            "offered_rate": offered_rate,
            "gap_percent": ((self.min_rate - offered_rate) / self.min_rate * 100) if offered_rate < self.min_rate else 0
        }
        
        if offered_rate < self.min_rate:
            analysis["suggested_counter"] = self.min_rate * 1.1
            analysis["reasoning"] = f"Your minimum is ${self.min_rate}, consider countering at ${analysis['suggested_counter']:.2f}"
        else:
            analysis["reasoning"] = "Offer meets your minimum rate"
        
        return analysis
    
    def suggest_counter_offer(self, offered_rate: float, reasoning: str) -> str:
        """Generate counter offer language."""
        counter = self.min_rate * 1.1
        
        return f"""Thank you for the offer. Based on the scope ({reasoning}), 
my rate for this project would be ${counter:.2f}/hour. 

This reflects my expertise in delivering similar projects successfully. 
I'm open to discussing a fixed-price arrangement if that works better for your budget.

Looking forward to finding a structure that works for both of us."""