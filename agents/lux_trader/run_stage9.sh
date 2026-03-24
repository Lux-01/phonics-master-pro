#!/bin/bash
# Stage 9 Semi-Autonomous Trading Launcher
# Usage: ./run_stage9.sh [check|approve|reject|status]

STAGE9_DIR="/home/skux/.openclaw/workspace/agents/lux_trader"
STAGE9_SCRIPT="$STAGE9_DIR/luxtrader_stage9_semi.py"
PROPOSALS_FILE="$STAGE9_DIR/stage9_proposals.json"
TRADES_FILE="$STAGE9_DIR/stage9_trades.json"
STATE_FILE="$STAGE9_DIR/stage9_state.json"

cd /home/skux/.openclaw/workspace

case "$1" in
    check|scan)
        echo "🔍 Stage 9: Checking for opportunities..."
        python3 "$STAGE9_SCRIPT"
        ;;
    
    approve)
        PROPOSAL_ID="$2"
        if [ -z "$PROPOSAL_ID" ]; then
            echo "❌ Usage: ./run_stage9.sh approve <proposal_id>"
            echo "   Or use './run_stage9.sh approve-latest'"
            exit 1
        fi
        
        if [ "$PROPOSAL_ID" = "latest" ] || [ "$PROPOSAL_ID" = "approve-latest" ]; then
            # Get latest pending proposal
            LATEST=$(python3 -c "
import json
with open('$PROPOSALS_FILE') as f:
    data = json.load(f)
if data.get('pending'):
    print(data['pending'][0]['id'])
" 2>/dev/null)
            if [ -n "$LATEST" ]; then
                PROPOSAL_ID="$LATEST"
            else
                echo "❌ No pending proposals found"
                exit 1
            fi
        fi
        
        echo "✅ Approving proposal: $PROPOSAL_ID"
        python3 -c "
import json
import sys
sys.path.insert(0, '/home/skux/.openclaw/workspace')
from agents.lux_trader.luxtrader_stage9_semi import Stage9SemiAutonomousTrader

trader = Stage9SemiAutonomousTrader()

# Load proposal
with open('$PROPOSALS_FILE') as f:
    data = json.load(f)

proposal = None
for p in data['pending']:
    if p['id'] == '$PROPOSAL_ID':
        proposal = p
        break

if proposal:
    # Execute trade
    success = trader.execute_trade(proposal)
    if success:
        # Move to history
        p['status'] = 'EXECUTED'
        data['history'].append(p)
        data['pending'] = [x for x in data['pending'] if x['id'] != '$PROPOSAL_ID']
        
        with open('$PROPOSALS_FILE', 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f'✅ Trade executed for {proposal[\"token\"][\"symbol\"]}')
    else:
        print('❌ Execution failed')
else:
    print(f'❌ Proposal not found: $PROPOSAL_ID')
"
        ;;
    
    reject)
        PROPOSAL_ID="$2"
        if [ -z "$PROPOSAL_ID" ]; then
            echo "❌ Usage: ./run_stage9.sh reject <proposal_id>"
            exit 1
        fi
        
        echo "❌ Rejecting proposal: $PROPOSAL_ID"
        python3 -c "
import json
with open('$PROPOSALS_FILE') as f:
    data = json.load(f)

for p in data['pending']:
    if p['id'] == '$PROPOSAL_ID':
        p['status'] = 'REJECTED'
        data['history'].append(p)
        data['pending'] = [x for x in data['pending'] if x['id'] != '$PROPOSAL_ID']
        
        with open('$PROPOSALS_FILE', 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f'Rejected proposal for {p[\"token\"][\"symbol\"]}')
        break
"
        ;;
    
    status)
        echo "📊 Stage 9 Status"
        echo "=================="
        
        # Show state
        python3 -c "
import json
from datetime import datetime

try:
    with open('$STATE_FILE') as f:
        state = json.load(f)
    
    print(f\"Status: {state.get('status', 'UNKNOWN')}\")
    print(f\"Trades today: {state.get('trades_today', 0)}/5\")
    print(f\"Loss today: {state.get('loss_today_sol', 0)}/0.5 SOL\")
    print(f\"Total trades: {state.get('total_trades', 0)}\")
    print(f\"Successful: {state.get('successful_trades', 0)}\")
    
    last = state.get('last_trade_time')
    if last:
        print(f\"Last trade: {last}\")
except:
    print('No state file found')
"
        
        # Show pending proposals
        python3 -c "
import json
try:
    with open('$PROPOSALS_FILE') as f:
        data = json.load(f)
    
    pending = data.get('pending', [])
    if pending:
        print(f'\\n⏳ Pending Proposals: {len(pending)}')
        for p in pending:
            print(f\"  • {p['id']}: {p['token']['symbol']} (expires {p.get('expires_at', 'N/A')})\")
    else:
        print('\\n✅ No pending proposals')
except:
    print('\\nNo proposals file')
"
        
        # Show recent trades
        python3 -c "
import json
try:
    with open('$TRADES_FILE') as f:
        data = json.load(f)
    
    trades = data.get('trades', [])
    if trades:
        print(f'\\n📈 Recent Trades (last 5):')
        for t in trades[-5:]:
            status = t.get('status', 'UNKNOWN')
            symbol = t.get('token', {}).get('symbol', 'N/A')
            pnl = t.get('pnl_pct', 0)
            print(f\"  • {symbol}: {status} ({pnl:+.1f}%)\")
    else:
        print('\\nNo trades yet')
except:
        print('\\nNo trades file')
"
        ;;
    
    *)
        echo "🎯 Stage 9 - Semi-Autonomous Trading"
        echo ""
        echo "Commands:"
        echo "  check        - Scan for opportunities and generate proposals"
        echo "  approve      - Approve a proposal for execution"
        echo "  reject       - Reject a proposal"
        echo "  status       - Show current status and pending proposals"
        echo ""
        echo "Examples:"
        echo "  ./run_stage9.sh check"
        echo "  ./run_stage9.sh approve <proposal_id>"
        echo "  ./run_stage9.sh approve-latest"
        echo "  ./run_stage9.sh status"
        ;;
esac
