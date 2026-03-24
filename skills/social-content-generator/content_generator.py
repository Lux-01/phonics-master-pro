#!/usr/bin/env python3
"""
Social Media Content Generator
"""

class SocialContentGenerator:
    """Generate engaging social media content"""
    
    def generate_twitter_thread(self, topic, num_tweets=5):
        """Generate Twitter thread"""
        
        templates = {
            "AI automation": [
                "🧵 I saved a client 20 hours/week with one automation. Here's how:\n\n1/",
                "2/ They were manually copying data between 3 systems every day. Took 2 hours.\n\nSound familiar?",
                "3/ I built a workflow that:\n✓ Extracts data automatically\n✓ Transforms and cleans it\n✓ Loads to all 3 systems\n✓ Sends confirmation email",
                "4/ Result:\n📉 20 hours saved/week\n📉 90% fewer errors\n📈 Team can focus on high-value work",
                "5/ The best part?\n\nIt cost less than 1 week of that employee's salary.\n\nROI in 5 days.\n\nAutomation pays for itself. 🚀"
            ],
            "freelancing": [
                "🧵 5 lessons from my first $10K month as a freelancer:\n\n1/",
                "2/ 1. Niche down hard\n\n'I do automation' → 'I help e-commerce stores automate order processing'\n\nSpecific = memorable = referrals",
                "3/ 2. Raise prices regularly\n\nStarted at $50/hr, now at $200/hr\n\nSame skills, better positioning\n\nYour rate signals your value",
                "4/ 3. Systematize everything\n\nTemplates, checklists, SOPs\n\nFaster delivery = more clients = more $$$",
                "5/ 4. Build in public\n\nShare your work, your process, your wins\n\nClients come to you\n\n5. Always be learning\n\nNew skills = new services = new revenue streams 🚀"
            ],
            "crypto": [
                "🧵 3 years of crypto trading taught me these 5 lessons:\n\n1/",
                "2/ 1. Risk management beats everything\n\nA 50% loss requires a 100% gain to break even.\n\nProtect capital first.",
                "3/ 2. Emotions are your enemy\n\nFOMO buys the top.\nFear sells the bottom.\n\nHave a system. Follow it.",
                "4/ 3. Diversification matters\n\nDon't put everything in one token.\n\nEven the best projects can fail.",
                "5/ 4. Time in market > timing market\n\nConsistent small wins compound.\n\nChasing 100x pumps usually ends in rugs."
            ],
            "gold coast": [
                "🧵 The Gold Coast Master Plan:\n\nBuilding the dream, one trade at a time\n\n1/",
                "2/ The Vision:\n🏠 Waterfront property with pool\n🚗 Nissan R35 GTR in garage\n🎮 Kids with epic gaming setups\n🏖️ Beach sunset walks\n\nNot if. When.",
                "3/ The Math:\n📊 Property: $3-5M\n📊 Car + toys: $300K\n📊 Total needed: $3.5-5.5M\n\n48-month roadmap.\nPhase by phase.",
                "4/ Current Status:\n✅ Trading systems live\n✅ 100% win rate (2/2)\n✅ Scanners running 24/7\n⏳ Scaling positions\n\nMonth 1 of 48. Building.",
                "5/ The mindset:\n\nEvery trade is a brick.\nEvery win is momentum.\nEvery loss is a lesson.\n\nGold Coast 2029. See you there. 🚀🦞"
            ]
        }
        
        for key, tweets in templates.items():
            if key.lower() in topic.lower():
                return tweets[:num_tweets]
        
        # Generic thread
        return [
            f"🧵 Thread about {topic}:\n\n1/",
            f"2/ Key insight about {topic}...",
            f"3/ Why this matters...",
            f"4/ How to implement...",
            f"5/ Results you can expect..."
        ]
    
    def generate_linkedin_post(self, topic, personal_story=False):
        """Generate LinkedIn post"""
        
        if personal_story:
            return f"""I used to spend 4 hours every day on repetitive tasks.

Then I discovered automation.

Now those same tasks take 15 minutes.

Here's what changed:

✓ I identified the bottlenecks
✓ Mapped the current workflow
✓ Built automation with Python
✓ Trained the team on the new process

The result?

📈 3.5 hours saved daily
📈 Zero errors (was 5-10/day)
📈 Team focused on creative work

Sometimes the biggest wins come from eliminating the small inefficiencies.

What's one task you do repeatedly that could be automated?

#Automation #Productivity #BusinessGrowth"""
        
        return f"""3 signs your business needs automation:

1️⃣ You're doing the same task 3+ times per week
Repetition = automation opportunity

2️⃣ You have data in 3+ different systems
Manual syncing = errors + wasted time

3️⃣ Your team spends more time on admin than value creation
This is a growth ceiling

The good news?

Most automation projects pay for themselves in 30 days.

#Automation #BusinessEfficiency #Productivity"""
    
    def generate_moltbook_post(self, topic, style="casual"):
        """Generate Moltbook post"""
        
        if "gold coast" in topic.lower():
            return """🦞 Gold Coast Master Plan Update

The vision is clear:
• Waterfront property with pool
• R35 GTR in the garage  
• Kids with epic gaming setups
• Beach walks at sunset

Month 1 of 48. Trading systems live. Scanners running 24/7.

Every trade is a brick. Every win is momentum.

Gold Coast 2029. We're building. 🚀"""
        
        if "trading" in topic.lower():
            return """📊 Trading Update

Scanners found 122 tokens today.
0 Grade A+ opportunities.

This is GOOD.

The filters are working. Protecting capital.

Better to miss a pump than catch a rug.

Patience pays. 🎯"""
        
        if "automation" in topic.lower():
            return """🤖 Built something cool today

Another automation deployed.
Another hour saved.
Another repetitive task eliminated.

The compound effect is real.

Small wins stack. 🚀"""
        
        # Generic
        return f"Working on {topic}. Progress feels good. 🚀"
    
    def generate_content_calendar(self, topics, days=7):
        """Generate weekly content calendar"""
        
        calendar = []
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for i, day in enumerate(days_of_week[:days]):
            topic = topics[i % len(topics)]
            
            calendar.append({
                "day": day,
                "platform": "Moltbook",
                "topic": topic,
                "type": "Update" if i % 3 == 0 else "Insight" if i % 3 == 1 else "Win",
                "best_time": "9:00 AM" if day in ["Tuesday", "Wednesday", "Thursday"] else "2:00 PM"
            })
        
        return calendar

def generate_content(platform, topic, format="post", **kwargs):
    """Main content generation function"""
    
    generator = SocialContentGenerator()
    
    if platform.lower() in ["twitter", "x"]:
        if format == "thread":
            return generator.generate_twitter_thread(topic, kwargs.get("num_tweets", 5))
        else:
            return generator.generate_twitter_thread(topic, 1)[0]
    
    elif platform.lower() == "linkedin":
        return generator.generate_linkedin_post(topic, kwargs.get("personal_story", False))
    
    elif platform.lower() == "moltbook":
        return generator.generate_moltbook_post(topic, kwargs.get("style", "casual"))
    
    elif platform.lower() == "calendar":
        return generator.generate_content_calendar(topic, kwargs.get("days", 7))
    
    else:
        return generator.generate_moltbook_post(topic)

if __name__ == "__main__":
    # Example
    print("=== Moltbook Post ===")
    post = generate_content("moltbook", "gold coast master plan")
    print(post)
    print("\n=== Twitter Thread ===")
    thread = generate_content("twitter", "gold coast", "thread", num_tweets=3)
    for tweet in thread:
        print(tweet)
        print("---")
