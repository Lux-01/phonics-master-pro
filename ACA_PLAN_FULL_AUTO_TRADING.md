# ACA Plan: Full Auto Trading with Pre-Buy Review

## Step 1: Requirements Analysis

### Problem Statement
User wants full auto execution for LuxTrader v3.0 with:
1. Debug why 0.001 SOL test buy failed
2. Add review step before every buy (verify it's the right coin)
3. Ensure buy once, don't rebuy (duplicate prevention)

### Inputs
- Token signal from scanner (address, symbol, grade, score)
- Wallet address
- Private key (for full auto)
- Position size (0.02 SOL)

### Expected Outputs
- Successful Jupiter swap execution
- Transaction signature
- Trade logged with full details
- Review report before execution

### Constraints
- Must verify token before buying (not a scam/rug)
- Must not buy same token twice
- Must handle network failures gracefully
- Must respect all safety limits
- Private key must be stored securely

### Success Criteria
- 0.001 SOL test trade executes successfully
- Review step shows token details for verification
- Duplicate trades are blocked
- All safety checks pass

---

## Step 2: Architecture Design

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                    FULL AUTO TRADER                          │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Signal     │  │    Review    │  │   Execute    │      │
│  │   Receiver   │→ │    Engine    │→ │    Engine    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                 │                 │               │
│         ↓                 ↓                 ↓               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Duplicate   │  │  Token       │  │  Jupiter     │      │
│  │  Checker     │  │  Validator   │  │  Executor    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                 │                 │               │
│         ↓                 ↓                 ↓               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Trade Logger & State Manager            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Module Breakdown

1. **Signal Receiver**
   - Receives token from scanner
   - Validates basic fields
   - Checks grade/score

2. **Duplicate Checker**
   - Checks if token already in positions
   - Checks trade history for recent buys
   - Prevents rebuys within cooldown period

3. **Review Engine**
   - Fetches token details from Jupiter
   - Verifies price, liquidity, market cap
   - Generates human-readable review report
   - Shows risk assessment

4. **Token Validator**
   - Checks if token is a known scam
   - Verifies liquidity is sufficient
   - Validates price impact is reasonable
   - Confirms token age

5. **Jupiter Executor**
   - Gets quote
   - Builds transaction
   - Signs with private key
   - Sends to blockchain
   - Waits for confirmation

6. **Trade Logger**
   - Logs all attempts
   - Records successes/failures
   - Updates positions
   - Tracks P&L

---

## Step 3: Data Flow

```
1. Scanner detects Grade A token
   ↓
2. Signal received with token data
   ↓
3. DUPLICATE CHECK
   - Is token in active positions? → BLOCK
   - Was token traded in last 24h? → BLOCK
   ↓
4. SAFETY CHECK
   - Daily loss limit? → BLOCK if exceeded
   - Max trades today? → BLOCK if exceeded
   - Drawdown? → BLOCK if exceeded
   ↓
5. TOKEN VALIDATION
   - Fetch Jupiter quote
   - Check price impact < 5%
   - Verify liquidity > $8K
   - Confirm mcap > $15K
   ↓
6. REVIEW GENERATION
   - Create detailed report
   - Show token details
   - Display risk score
   - Log for audit
   ↓
7. EXECUTION DECISION
   - Auto-approve if all checks pass
   - Execute Jupiter swap
   ↓
8. TRANSACTION HANDLING
   - Sign with private key
   - Send to network
   - Wait confirmation (30s timeout)
   - Get transaction signature
   ↓
9. POST-TRADE
   - Log successful trade
   - Add to positions
   - Update capital
   - Send confirmation
   ↓
10. MONITORING
    - Track position for exits
    - Check stop loss
    - Check take profit
    - Execute sell when target hit
```

---

## Step 4: Edge Cases

### Critical Edge Cases

1. **Network Failure**
   - Jupiter API unreachable
   - Solana RPC down
   - DNS resolution fails
   → Retry 3x with exponential backoff, then fail gracefully

2. **Insufficient Funds**
   - Wallet has < 0.001 SOL
   - Token account doesn't exist
   → Check balance before execution, fail fast

3. **Token Already Owned**
   - Position exists from previous trade
   - Partial sell remaining
   → Block duplicate, log reason

4. **High Price Impact**
   - Slippage > 5%
   - Low liquidity
   → Block trade, log warning

5. **Transaction Timeout**
   - Network congestion
   - Transaction not confirmed
   → Wait 60s, check status, retry if needed

6. **Invalid Token**
   - Token doesn't exist
   - Token is frozen
   → Validate before execution

7. **Rate Limiting**
   - Jupiter API rate limit
   - RPC rate limit
   → Add delays, respect limits

8. **Private Key Issues**
   - Key not found
   - Key invalid
   - Key permissions wrong
   → Check before execution, fail fast

9. **Concurrent Trades**
   - Multiple signals at once
   - Race condition on positions
   → Use file locking, queue trades

10. **Partial Fills**
    - Order partially filled
    - Remaining amount small
    → Handle gracefully, log actual amount

---

## Step 5: Tool Constraints

### Jupiter API
- Rate limit: 300 req/min
- Requires: inputMint, outputMint, amount, slippageBps
- Returns: quote with route, price impact, expected output
- Swap endpoint: POST /swap with quoteResponse

### Solana RPC
- Rate limit: 100 req/sec
- Methods: sendTransaction, getSignatureStatuses
- Requires: signed transaction (base64)
- Returns: transaction signature

### Private Key
- Format: Base58 encoded
- Storage: ~/.openclaw/secrets/trading_key.json
- Permissions: 600 (owner only)
- Loading: Use solders library

### File System
- State file: luxtrader_state.json
- Trade log: live_trades.json
- Logs: /tmp/luxtrader_continuous.log
- Permissions: Need read/write access

### Network
- Current session has DNS issues
- Cron jobs have normal network
- Must handle both environments

---

## Step 6: Error Handling Strategy

### Error Categories

1. **Pre-Execution Errors** (Block trade)
   - Duplicate token
   - Safety limit exceeded
   - Invalid token
   - High price impact
   → Log rejection reason, continue scanning

2. **Execution Errors** (Retry then fail)
   - Network timeout
   - Rate limited
   - RPC error
   → Retry 3x, then log failure

3. **Critical Errors** (Stop system)
   - Private key missing
   - Wallet drained
   - Repeated failures
   → Log critical, notify user, halt

### Error Recovery

```python
def execute_with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except NetworkError as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise
        except RateLimitError:
            time.sleep(60)  # Wait for quota
            continue
        except Exception as e:
            raise  # Don't retry unknown errors
```

---

## Step 7: Testing Plan

### Happy Path Tests

1. **Valid Grade A+ Token**
   - Input: Grade A+, score 85, good liquidity
   - Expected: Review generated, trade executed, logged

2. **Valid Grade A Token**
   - Input: Grade A, score 75, acceptable metrics
   - Expected: Review generated, trade executed, logged

3. **Position Sizing**
   - Input: 1.0 SOL capital
   - Expected: 0.012 SOL position (1.2%)

### Edge Case Tests

1. **Duplicate Token**
   - Input: Token already in positions
   - Expected: Blocked, "Already owned" reason

2. **High Price Impact**
   - Input: Token with 10% price impact
   - Expected: Blocked, "High slippage" reason

3. **Safety Limit Exceeded**
   - Input: Daily loss already at -0.10 SOL
   - Expected: Blocked, "Daily loss limit" reason

4. **Network Failure**
   - Input: Jupiter API unreachable
   - Expected: Retry 3x, then fail gracefully

5. **Insufficient Balance**
   - Input: Wallet with 0.0001 SOL
   - Expected: Blocked, "Insufficient funds" reason

### Integration Tests

1. **End-to-End Flow**
   - Signal → Review → Execute → Log
   - Verify all steps complete

2. **Private Key Loading**
   - Store key → Load key → Sign transaction
   - Verify signature valid

3. **State Persistence**
   - Execute trade → Save state → Load state
   - Verify position tracked

4. **Error Recovery**
   - Simulate network failure → Retry → Success
   - Verify resilience

---

## Implementation Notes

### Why 0.001 Test Failed

**Hypothesis 1: Network Issue**
- Current session has DNS resolution problems
- Jupiter API unreachable from this environment
- Cron jobs likely work fine (different network context)

**Hypothesis 2: Missing Dependencies**
- Solana libraries not installed
- Cannot sign transactions without solders

**Hypothesis 3: Code Path Issue**
- execute_trade() may not be calling Jupiter correctly
- Need to verify the execution flow

**Debug Plan:**
1. Add detailed logging to execution path
2. Test with mock Jupiter responses
3. Verify private key loading
4. Check network connectivity from cron context

### Review Step Design

**Before every buy, show:**
```
🎯 PRE-BUY REVIEW
Token: SYMBOL (ADDRESS)
Grade: A+ | Score: 85/100
Price: $0.000123
Liquidity: $45,000
Market Cap: $89,000
Age: 3 hours
Price Impact: 2.3%

Risk Assessment: LOW
✓ Liquidity sufficient
✓ Market cap acceptable
✓ Price impact reasonable
✓ Not a known scam

EXECUTING: 0.02 SOL → ~162,000 tokens
```

**This provides:**
- Clear token identification
- Risk assessment
- Financial details
- Execution confirmation

### Duplicate Prevention

**Strategy:**
1. Check active positions (in-memory + file)
2. Check trade history (last 24h)
3. Use token address as unique key
4. Cooldown period: 24 hours

**Implementation:**
```python
def can_buy_token(token_address: str) -> Tuple[bool, str]:
    # Check active positions
    if token_address in state["positions"]:
        return False, "Already in portfolio"
    
    # Check recent trades
    recent_trades = get_trades_last_24h()
    if token_address in [t["address"] for t in recent_trades]:
        return False, "Traded in last 24h"
    
    return True, "OK"
```

---

## Files to Create/Modify

### New Files
1. `full_auto_trader.py` - Main execution engine
2. `token_reviewer.py` - Pre-buy review generator
3. `duplicate_checker.py` - Rebuy prevention
4. `test_full_auto.py` - Comprehensive tests

### Modified Files
1. `luxtrader_live.py` - Integrate full auto
2. `jupiter_executor.py` - Add signing capability
3. `secure_key_manager.py` - Verify key loading

---

## Success Metrics

- ✅ 0.001 SOL test trade executes
- ✅ Review report generated for every trade
- ✅ Duplicate trades blocked 100%
- ✅ All safety limits respected
- ✅ Transaction signatures obtained
- ✅ Trades logged correctly
- ✅ No crashes or hangs

---

**Plan Complete. Ready for implementation.**
