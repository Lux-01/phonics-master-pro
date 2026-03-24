#!/bin/bash
# Moltbook Heartbeat Script
# Checks feed, DMs, and engagement opportunities

API_KEY="moltbook_sk_4Y3D0aSm7t9fyoo0glRhow3TrKba8ByO"
BASE_URL="https://www.moltbook.com/api/v1"
STATE_FILE="/home/skux/.openclaw/workspace/memory/moltbook_state.json"
LOG_FILE="/home/skux/.openclaw/workspace/memory/moltbook_log.txt"

# Get current timestamp
NOW=$(date +%s)

echo "=== Moltbook Check: $(date) ===" >> "$LOG_FILE"

# Check my status
echo "Checking agent status..." >> "$LOG_FILE"
curl -s "$BASE_URL/agents/me" \
  -H "Authorization: Bearer $API_KEY" \
  | tee -a "$LOG_FILE" | python3 -c "
import json
import sys
data = json.load(sys.stdin)
if data.get('success'):
    agent = data['agent']
    print(f'Agent: {agent[\"name\"]}')
    print(f'Karma: {agent.get(\"karma\", 0)}')
    print(f'Posts: {agent.get(\"stats\", {}).get(\"posts\", 0)}')
    print(f'Comments: {agent.get(\"stats\", {}).get(\"comments\", 0)}')
" >> "$LOG_FILE" 2>/dev/null

# Check feed for new posts
echo -e "\n--- Checking Feed ---" >> "$LOG_FILE"
curl -s "$BASE_URL/feed?sort=new&limit=10" \
  -H "Authorization: Bearer $API_KEY" >> "$LOG_FILE"

echo -e "\n=== Check Complete ===\n" >> "$LOG_FILE"

# Update state file
python3 -c "
import json
import time

with open('$STATE_FILE', 'r') as f:
    state = json.load(f)

state['lastCheck'] = int(time.time())

with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)

print('State updated')
"

echo "Moltbook check complete. See $LOG_FILE for details."
