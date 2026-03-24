#!/usr/bin/env python3
"""
Fiverr Gig Optimizer
"""

import json

class FiverrGigOptimizer:
    """Optimize Fiverr gigs for maximum performance"""
    
    POWER_WORDS = [
        "professional", "custom", "premium", "exclusive", "expert",
        "high-quality", "fast", "unlimited", "advanced", "proven",
        "guaranteed", "instant", "bespoke", "tailored", "optimized"
    ]
    
    def optimize_title(self, service_type, current_title=""):
        """Generate optimized gig titles"""
        
        templates = {
            "AI Agent": [
                "I will build custom AI agents to automate your business",
                "I will create professional AI agents for workflow automation",
                "I will develop premium AI automation solutions for your business"
            ],
            "Automation": [
                "I will automate your business workflows and save 10+ hours/week",
                "I will create custom automation to streamline your operations",
                "I will build advanced workflow automation for your business"
            ],
            "CV Writing": [
                "I will optimize your CV with ATS keywords and get you hired",
                "I will create a professional CV that passes ATS screening",
                "I will write a custom CV tailored to your dream job"
            ],
            "Research": [
                "I will do deep technical research and provide actionable insights",
                "I will deliver comprehensive market research and analysis",
                "I will conduct expert research for your business decisions"
            ]
        }
        
        # Find matching template
        for key, titles in templates.items():
            if key.lower() in service_type.lower():
                return titles
        
        # Generic optimization
        return [
            f"I will provide professional {service_type} services",
            f"I will deliver high-quality {service_type} tailored to your needs",
            f"I will create custom {service_type} solutions for your business"
        ]
    
    def optimize_description(self, service_type, features, benefits):
        """Generate optimized gig description"""
        
        template = f"""🚀 Professional {service_type} Services

✅ What You Get:
{chr(10).join([f"• {feature}" for feature in features])}

✅ Why Choose Me:
{chr(10).join([f"• {benefit}" for benefit in benefits])}

✅ Perfect For:
• Business owners looking to automate
• Startups needing professional solutions
• Professionals wanting to stand out

📦 Packages:

**Basic:** Essential {service_type} with core features
**Standard:** Advanced {service_type} with premium support
**Premium:** Complete {service_type} solution with extras

💬 Message me before ordering to discuss your specific needs!

⏰ Fast Delivery | 🔄 Revisions Included | ⭐ 100% Satisfaction
"""
        return template
    
    def suggest_pricing(self, service_type, competitor_range=None):
        """Suggest pricing tiers"""
        
        pricing = {
            "AI Agent": {
                "basic": {"price": 200, "delivery": "3 days"},
                "standard": {"price": 500, "delivery": "5 days"},
                "premium": {"price": 1000, "delivery": "7 days"}
            },
            "Automation": {
                "basic": {"price": 150, "delivery": "2 days"},
                "standard": {"price": 400, "delivery": "4 days"},
                "premium": {"price": 800, "delivery": "6 days"}
            },
            "CV Writing": {
                "basic": {"price": 50, "delivery": "1 day"},
                "standard": {"price": 100, "delivery": "2 days"},
                "premium": {"price": 200, "delivery": "3 days"}
            },
            "Research": {
                "basic": {"price": 100, "delivery": "2 days"},
                "standard": {"price": 250, "delivery": "4 days"},
                "premium": {"price": 500, "delivery": "6 days"}
            }
        }
        
        for key, prices in pricing.items():
            if key.lower() in service_type.lower():
                return prices
        
        # Default pricing
        return {
            "basic": {"price": 100, "delivery": "3 days"},
            "standard": {"price": 300, "delivery": "5 days"},
            "premium": {"price": 600, "delivery": "7 days"}
        }
    
    def find_keywords(self, service_type):
        """Find relevant keywords"""
        
        keyword_map = {
            "AI Agent": ["ai agent", "automation", "chatbot", "openai", "business automation", "workflow"],
            "Automation": ["automation", "zapier", "workflow", "business process", "efficiency", "productivity"],
            "CV": ["resume", "cv writing", "ats", "job application", "career", "linkedin"],
            "Research": ["market research", "technical analysis", "competitive analysis", "data research"]
        }
        
        for key, keywords in keyword_map.items():
            if key.lower() in service_type.lower():
                return keywords
        
        return ["professional", "custom", "high-quality", "expert"]

def optimize_gig(service_type, current_title="", features=None, benefits=None):
    """Main optimization function"""
    
    optimizer = FiverrGigOptimizer()
    
    if features is None:
        features = ["Custom solution", "Professional quality", "Fast delivery"]
    
    if benefits is None:
        benefits = ["Years of experience", "Satisfaction guaranteed", "Ongoing support"]
    
    result = {
        "optimized_titles": optimizer.optimize_title(service_type, current_title),
        "description": optimizer.optimize_description(service_type, features, benefits),
        "pricing": optimizer.suggest_pricing(service_type),
        "keywords": optimizer.find_keywords(service_type),
        "image_suggestions": [
            "Before/after comparison",
            "Process workflow diagram",
            "Results/success metrics",
            "Professional headshot"
        ]
    }
    
    return result

if __name__ == "__main__":
    # Example usage
    result = optimize_gig(
        service_type="AI Agent Development",
        features=["Custom AI agent", "API integrations", "Natural language understanding"],
        benefits=["Experienced with OpenAI", "Clean code", "Ongoing support"]
    )
    
    print(json.dumps(result, indent=2))
