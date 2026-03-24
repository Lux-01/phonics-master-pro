#!/usr/bin/env python3
"""
🚀 Quick Sell Helper - INCOME Token
Provides the direct link and instructions
"""

TOKEN = "5QmbJw7mM6tcCdXVy8ftc2bu8izded7Etc57TMA2pump"
TOKEN_SYMBOL = "INCOME"
AMOUNT = 490.916016
WALLET = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"

def main():
    print("="*70)
    print("🚀 SELL INCOME TOKEN")
    print("="*70)
    print(f"Token: {TOKEN_SYMBOL}")
    print(f"Amount: {AMOUNT}")
    print(f"Wallet: {WALLET}")
    print("="*70)
    
    print("\n🔗 DIRECT SELL LINK:")
    print("-"*70)
    print(f"https://jup.ag/swap/{TOKEN}-SOL")
    print("-"*70)
    
    print("\n📋 STEPS:")
    print("1. Click the link above")
    print("2. Connect your wallet (should auto-connect)")
    print("3. Set slippage to 15% (⚠️ Important for PumpSwap)")
    print("4. Click 'Swap'")
    print("5. Confirm in wallet")
    
    print("\n💡 TIPS:")
    print("- If it fails, try 20% slippage")
    print("- If still failing, wait 2 minutes and retry")
    print("- Alternative: https://pump.fun/swap")
    
    print("\n💰 Expected Return:")
    print("- ~0.0009-0.001 SOL")
    
    print("\n" + "="*70)
    print("Good luck! 🚀")
    print("="*70)

if __name__ == "__main__":
    main()
