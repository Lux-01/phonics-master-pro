#!/usr/bin/env python3
"""
Client Proposal Writer
"""

class ClientProposalWriter:
    """Write winning client proposals"""
    
    def write_upwork_proposal(self, job_description, client_info, your_expertise):
        """Write Upwork job proposal"""
        
        # Extract key requirements
        requirements = self._extract_requirements(job_description)
        
        # Build proposal
        proposal = f"""Hi there,

I noticed you're looking for {client_info.get('service', 'help with your project')}. This is exactly what I specialize in.

**Why I'm a great fit:**
{chr(10).join([f"✓ {exp}" for exp in your_expertise[:3]])}

**My approach:**
1. Discovery - Understanding your specific needs
2. Strategy - Planning the optimal solution
3. Implementation - Building with best practices
4. Delivery - Testing and handoff with documentation

**Recent success:**
I recently helped a {client_info.get('industry', 'similar business')} automate their workflow, saving them 15 hours per week and reducing errors by 90%.

**Next steps:**
I'd love to discuss your project in more detail. I'm available for a quick call this week to understand your requirements better.

Looking forward to working with you!

Best regards"""
        
        return proposal
    
    def write_cold_email(self, prospect_info, service_offering):
        """Write cold outreach email"""
        
        email = f"""Subject: Quick question about {prospect_info.get('company', 'your business')}

Hi {prospect_info.get('name', 'there')},

I came across {prospect_info.get('company', 'your company')} and noticed you might benefit from {service_offering}.

Many {prospect_info.get('industry', 'businesses in your industry')} struggle with [specific pain point]. I've helped similar companies [specific result].

Would you be open to a brief 10-minute call to explore if this could help {prospect_info.get('company', 'your team')}?

No pressure - just happy to share insights either way.

Best,
[Your name]"""
        
        return email
    
    def write_pricing_proposal(self, services, total_value):
        """Write pricing proposal"""
        
        proposal = f"""# Project Proposal

## Scope of Work
{chr(10).join([f"- {service}" for service in services])}

## Investment

**Total Project Value:** ${total_value}

**Payment Terms:**
- 50% upfront to begin
- 50% upon completion

**What's Included:**
✓ All deliverables listed above
✓ 2 rounds of revisions
✓ 30 days of support after delivery
✓ Full documentation and handoff

**Timeline:** [X] business days from project start

**Next Steps:**
1. Review and approve proposal
2. Sign agreement and submit deposit
3. Kickoff call to finalize details
4. Project execution begins

Ready to get started? Reply with "APPROVED" and I'll send the agreement.
"""
        
        return proposal
    
    def _extract_requirements(self, job_description):
        """Extract key requirements from job description"""
        # Simple extraction - could be enhanced with NLP
        keywords = ["automation", "AI", "integration", "workflow", "custom", "API"]
        found = [k for k in keywords if k.lower() in job_description.lower()]
        return found if found else ["custom solution"]

def write_proposal(platform, job_description, client_info, your_expertise=None):
    """Main proposal writing function"""
    
    writer = ClientProposalWriter()
    
    if your_expertise is None:
        your_expertise = [
            "5+ years of experience",
            "100+ successful projects",
            "Expert in automation and AI"
        ]
    
    if platform.lower() == "upwork":
        return writer.write_upwork_proposal(job_description, client_info, your_expertise)
    elif platform.lower() == "email":
        return writer.write_cold_email(client_info, "automation services")
    else:
        return writer.write_pricing_proposal(["Custom solution"], 500)

if __name__ == "__main__":
    # Example
    proposal = write_proposal(
        platform="upwork",
        job_description="Need someone to automate our customer service with AI",
        client_info={"industry": "e-commerce", "service": "AI customer service"}
    )
    print(proposal)
