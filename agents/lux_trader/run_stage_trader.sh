#!/bin/bash
# ✨ LUXTRADER STAGE LAUNCHER
# Unified interface for Stages 7-10

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

clear

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║     ✨ LUXTRADER STAGE SYSTEM LAUNCHER ✨                    ║"
echo "║                                                              ║"
echo "║     Stages 7-10: Virtually Autonomous → Fully Automatic    ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Show current status
echo -e "${BLUE}Current Status:${NC}"
echo ""

# Check Stage 7 status
if [ -f "$SCRIPT_DIR/virtual_portfolio.json" ]; then
    VIRTUAL_SOL=$(python3 -c "import json; print(f\"{json.load(open('$SCRIPT_DIR/virtual_portfolio.json'))['virtual_sol']:.3f}\")" 2>/dev/null || echo "0.000")
    STARTING=$(python3 -c "import json; print(f\"{json.load(open('$SCRIPT_DIR/virtual_portfolio.json'))['starting_capital']:.3f}\")" 2>/dev/null || echo "10.000")
    TRADES=$(python3 -c "import json; print(json.load(open('$SCRIPT_DIR/virtual_portfolio.json'))['total_trades'])" 2>/dev/null || echo "0")
    echo -e "  ${GREEN}Stage 7 (Virtual):${NC} ${VIRTUAL_SOL} SOL / ${STARTING} SOL (${TRADES} trades)"
else
    echo -e "  ${YELLOW}Stage 7 (Virtual):${NC} Not started"
fi

# Check Stage 10 status
if [ -f "$SCRIPT_DIR/stage10_state.json" ]; then
    MODE=$(python3 -c "import json; print(json.load(open('$SCRIPT_DIR/stage10_state.json'))['mode'])" 2>/dev/null || echo "SUPERVISED")
    TRADES_TODAY=$(python3 -c "import json; print(json.load(open('$SCRIPT_DIR/stage10_state.json'))['trades_today'])" 2>/dev/null || echo "0")
    SUCCESS=$(python3 -c "import json; print(json.load(open('$SCRIPT_DIR/stage10_state.json'))['successful_trades'])" 2>/dev/null || echo "0")
    if [ "$SUCCESS" -ge 10 ]; then
        echo -e "  ${GREEN}Stage 10 (Auto):${NC} AUTO-PILOT (${TRADES_TODAY} today, ${SUCCESS} total)"
    else
        echo -e "  ${YELLOW}Stage 10 (Auto):${NC} SUPERVISED (${TRADES_TODAY} today, ${SUCCESS}/10 to auto)"
    fi
else
    echo -e "  ${YELLOW}Stage 10 (Auto):${NC} Not started"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Select Stage:                                               ║"
echo "║                                                              ║"
echo "║  ${CYAN}[7]${NC} Stage 7: Virtual Paper Trading                     ║"
echo "║      → Virtual SOL, learns patterns, no risk               ║"
echo "║                                                              ║"
echo "║  ${CYAN}[8]${NC} Stage 8: Live Execution (LuxTrader)                ║"
echo "║      → Real money, safety limits, your wallet              ║"
echo "║                                                              ║"
echo "║  ${CYAN}[9]${NC} Stage 9: Proactive Trading                       ║"
echo "║      → Auto-scan, notify, execute with countdown           ║"
echo "║                                                              ║"
echo "║  ${CYAN}[10]${NC} Stage 10: Full Autonomy                          ║"
echo "║      → Auto-execute after 10 successful trades             ║"
echo "║      → Pattern learning active                             ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${YELLOW}Stage 7 Commands:${NC}"
echo "  (1) Reset virtual portfolio"
echo "  (2) Run single cycle"
echo "  (3) Start continuous trading (5min intervals)"
echo "  (4) View stats"
echo ""
echo -e "${YELLOW}Stage 10 Commands:${NC}"
echo "  (5) Check status"
echo "  (6) Run single cycle"
echo "  (7) Start continuous auto-trading"
echo ""
echo -e "${RED}[Q]${NC} Quit"
echo ""

read -p "Enter choice: " choice

case $choice in
    1)
        echo -e "\n${YELLOW}Resetting virtual portfolio...${NC}"
        python3 "$SCRIPT_DIR/luxtrader_stage7_virtual.py" --reset
        echo -e "${GREEN}✅ Virtual portfolio reset to 10 SOL${NC}"
        ;;
    2)
        echo -e "\n${CYAN}Running Stage 7 single cycle...${NC}"
        python3 "$SCRIPT_DIR/luxtrader_stage7_virtual.py" --mode once
        ;;
    3)
        echo -e "\n${CYAN}Starting Stage 7 continuous mode...${NC}"
        echo -e "${YELLOW}Press Ctrl+C to stop${NC}\n"
        python3 "$SCRIPT_DIR/luxtrader_stage7_virtual.py" --mode continuous --interval 5
        ;;
    4)
        echo -e "\n${CYAN}Stage 7 Statistics:${NC}\n"
        python3 "$SCRIPT_DIR/luxtrader_stage7_virtual.py" --stats
        ;;
    5)
        echo -e "\n${CYAN}Stage 10 Status:${NC}\n"
        python3 "$SCRIPT_DIR/luxtrader_stage10_auto.py" --status
        ;;
    6)
        echo -e "\n${CYAN}Running Stage 10 single cycle...${NC}"
        python3 "$SCRIPT_DIR/luxtrader_stage10_auto.py" --mode once
        ;;
    7)
        echo -e "\n${CYAN}Starting Stage 10 continuous auto-trading...${NC}"
        echo -e "${RED}⚠️  This will auto-execute trades!${NC}"
        echo -e "${YELLOW}Press Ctrl+C to stop${NC}\n"
        read -p "Press Enter to continue..."
        python3 "$SCRIPT_DIR/luxtrader_stage10_auto.py" --mode continuous --interval 15
        ;;
    q|Q)
        echo -e "\n${GREEN}Goodbye!${NC}"
        exit 0
        ;;
    *)
        echo -e "\n${RED}Invalid choice${NC}"
        ;;
esac

echo ""
read -p "Press Enter to continue..."
bash "$0"
