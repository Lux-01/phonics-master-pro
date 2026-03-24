#!/usr/bin/env python3
"""
🧪 TEST FULL AUTO WITH STORED KEY
Verify that full auto execution works with the stored private key
"""

import sys
sys.path.insert(0, '/home/skux/.openclaw/workspace/agents/lux_trader')

from full_auto_executor import FullAutoExecutor, execute_buy_auto
from secure_key_manager import SecureKeyManager

WALLET = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
TEST_TOKEN = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC

def test_key_loading():
    """Test that key loads correctly"""
    print("\n" + "="*60)
    print("🔐 TEST 1: Key Loading")
    print("="*60)
    
    manager = SecureKeyManager()
    
    print(f"Key file location: {manager.key_file}")
    print(f"Key exists: {manager.key_exists()}")
    
    if manager.key_exists():
        key = manager.get_key()
        if key:
            print(f"✅ Key loaded successfully!")
            print(f"   Length: {len(key)} characters")
            print(f"   Preview: {key[:20]}...")
            return True
        else:
            print("❌ Failed to load key")
            return False
    else:
        print("❌ Key file not found")
        return False


def test_keypair_initialization():
    """Test that keypair initializes from stored key"""
    print("\n" + "="*60)
    print("🔑 TEST 2: Keypair Initialization")
    print("="*60)
    
    executor = FullAutoExecutor(WALLET)
    
    if executor.keypair:
        print("✅ Keypair initialized successfully!")
        print(f"   Public key: {executor.keypair.pubkey()}")
        return True
    else:
        print("❌ Failed to initialize keypair")
        print("   Check that Solana libraries are installed:")
        print("   pip install solders base58")
        return False


def test_0_001_execution():
    """Test 0.001 SOL execution"""
    print("\n" + "="*60)
    print("💰 TEST 3: 0.001 SOL Execution")
    print("="*60)
    
    print(f"\nAttempting to buy 0.001 SOL of USDC...")
    print(f"Wallet: {WALLET}")
    print(f"Token: {TEST_TOKEN}")
    
    result = execute_buy_auto(WALLET, TEST_TOKEN, 0.001, "USDC")
    
    print(f"\nResult:")
    print(f"   Status: {result.get('status', 'unknown')}")
    
    if result.get('status') == 'executed':
        print(f"   ✅ SUCCESS!")
        print(f"   Transaction: {result.get('transaction_signature', 'N/A')}")
        print(f"   Explorer: {result.get('explorer_url', 'N/A')}")
        return True
    elif result.get('status') == 'manual_required':
        print(f"   ⚠️ Manual execution required")
        print(f"   Reason: {result.get('message', 'Unknown')}")
        print(f"   URL: {result.get('manual_url', 'N/A')}")
        return False
    elif result.get('status') == 'failed':
        print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
        return False
    else:
        print(f"   Details: {result}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 FULL AUTO EXECUTION TEST")
    print("="*60)
    print("Testing with stored private key...")
    
    results = []
    
    # Test 1: Key loading
    results.append(("Key Loading", test_key_loading()))
    
    # Test 2: Keypair initialization
    results.append(("Keypair Initialization", test_keypair_initialization()))
    
    # Test 3: 0.001 execution
    results.append(("0.001 SOL Execution", test_0_001_execution()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 FULL AUTO IS READY!")
        print("✅ Private key loads correctly")
        print("✅ Keypair initializes")
        print("✅ Transactions can be signed and sent")
        print("\nLuxTrader will now execute trades automatically!")
    else:
        print("\n⚠️ Some tests failed")
        print("Review errors above")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
