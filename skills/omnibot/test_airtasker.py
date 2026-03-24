#!/usr/bin/env python3
"""
Demo script to test Airtasker integration.
"""

from job_seeker import PlatformScanners, JobPlatform, JobSeeker

# Test Airtasker scanning
seeker = JobSeeker()
seeker.scanners.update_preferences(
    skills=['python', 'web development', 'automation', 'wordpress', 'api'],
    platforms=['airtasker'],
    min_hourly_rate=50,
    min_project_budget=100
)

print('🔍 Scanning Airtasker for real tasks...')
print('=' * 60)

# Scan Airtasker
airtasker_jobs = seeker.scanners.scan_airtasker(
    keywords=['web', 'python', 'automation', 'API', 'developer'],
    min_budget=100
)

print(f'\n✅ Found {len(airtasker_jobs)} matching tasks:\n')

# Show all found tasks
for i, job in enumerate(airtasker_jobs, 1):
    budget = job.budget
    if budget:
        budget_str = f"${budget.get('min', 0)}-${budget.get('max', 0)}"
    else:
        budget_str = 'Negotiable'
    print(f"{i}. \"{job.title}\"")
    print(f"   Budget: {budget_str} AUD")
    print(f"   Skills: {', '.join(job.skills[:5])}")
    print(f"   Posted: {job.posted_date.strftime('%Y-%m-%d %H:%M')}")
    print(f"   Match Score: {job.match_score:.0f}%")
    print()

# Pick the best matching job
if airtasker_jobs:
    best_job = max(airtasker_jobs, key=lambda j: j.match_score)
    print('=' * 60)
    print(f"🎯 SELECTED: \"{best_job.title}\"")
    if best_job.budget:
        print(f"   Budget: ${best_job.budget.get('min', 0)}-${best_job.budget.get('max', 0)} AUD")
    print(f"   Match Score: {best_job.match_score:.0f}%")
    print(f"   Description: {best_job.description[:150]}...")
    print()
    
    # Generate proposal
    print('💬 GENERATING PROPOSAL...')
    print('=' * 60)
    proposal = seeker.generate_proposal(best_job)
    print(f"\nProposal for: {proposal.client_name}")
    rate = proposal.proposed_rate.get('suggested_hourly', 75)
    print(f"Suggested Rate: ${rate}/hr")
    print(f"Estimated Hours: {proposal.estimated_hours}")
    print(f"\n--- PROPOSAL CONTENT ---")
    print(proposal.content)
else:
    print("No matching jobs found.")
