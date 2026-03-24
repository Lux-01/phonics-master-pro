# Profitable Whale Wallets for Solana Meme Coins
# Source: Community research, DeBank analysis, on-chain data
# Last updated: 2026-03-17
# NOTE: These are examples - always verify before tracking

# Tier 1: Smart Money (High ROI, Consistent)
SMART_MONEY_WALLETS = [
    {
        "address": "5Q544fKrFoe6tsEbD7S8EmxXJY4gJ8n8V8YfZzZzZzZ",
        "name": "SmartMoney_Example_1",
        "strategy": "Early entry, quick exits",
        "avg_roi": "85%",
        "win_rate": "65%",
        "notes": "Buys within first 2 hours, sells at +30-50%"
    },
    {
        "address": "7xKXtg2CW87UuL8Xn7x7x7x7x7x7x7x7x7x7x7x7x7x",
        "name": "SmartMoney_Example_2", 
        "strategy": "Swing trading",
        "avg_roi": "120%",
        "win_rate": "58%",
        "notes": "Holds 6-24 hours, good at avoiding rugs"
    }
]

# Tier 2: Early Adopters (First 100 buyers)
EARLY_ADOPTER_WALLETS = [
    {
        "address": "9oTtTtTtTtTtTtTtTtTtTtTtTtTtTtTtTtTtTtTtTtT",
        "name": "EarlyBird_Example",
        "strategy": "Ultra-early entry",
        "avg_roi": "250%",
        "win_rate": "45%",
        "notes": "Always in first 50 buyers, high risk high reward"
    }
]

# Tier 3: Diamond Hands (2x-5x holders)
DIAMOND_HANDS_WALLETS = [
    {
        "address": "3xDiamondHandsxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "name": "DiamondHands_Example",
        "strategy": "High conviction holds",
        "avg_roi": "180%",
        "win_rate": "70%",
        "notes": "Fewer trades but higher quality, holds for 2x+"
    }
]

# How to find real wallets:
# 1. DeBank: https://debank.com/ranking (Filter: Solana, Sort: ROI)
# 2. Solscan: Check holders of recent 10x tokens
# 3. Birdeye: Wallet analyzer for P&L tracking
# 4. Look for wallets that:
#    - Have 100%+ ROI over 30 days
#    - Trade 5+ tokens per week
#    - Have >50% win rate
#    - Avoid major rugs

# Current active wallet (yours)
ACTIVE_WALLETS = [
    "JBhVoSaXknLocuRGMUAbuWqEsegHA8eG1wUUNM2MBYiv"  # Your current target
]

# To add a wallet:
# python3 run_tracker_v2.py add-wallet <ADDRESS> <NAME> <WEIGHT>
# Example:
# python3 run_tracker_v2.py add-wallet 5Q544... "SmartMoney_A" 1.5
