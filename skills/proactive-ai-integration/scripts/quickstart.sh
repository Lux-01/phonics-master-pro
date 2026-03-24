#!/bin/bash
# Quick Start Script for Proactive AI Integration Layer

echo "=========================================="
echo "Proactive AI Integration - Quick Start"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not installed.${NC}"
    exit 1
fi

# Create necessary directories
echo "Setting up directories..."
mkdir -p memory/proactive_ai/{orchestrator,event_bus,cache,user_model,patterns,outcomes,cross_component,learning}

# Check if orchestrator exists
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ORCHESTRATOR="$SCRIPT_DIR/proactive_ai_orchestrator.py"

if [ ! -f "$ORCHESTRATOR" ]; then
    echo -e "${RED}Error: proactive_ai_orchestrator.py not found in $SCRIPT_DIR${NC}"
    exit 1
fi

# Function to show status
show_status() {
    echo ""
    echo "Checking status..."
    python3 "$ORCHESTRATOR" status
}

# Function to start
start_orchestrator() {
    echo -e "${GREEN}Starting Proactive AI Integration Layer...${NC}"
    echo ""
    python3 "$ORCHESTRATOR" start &
    PID=$!
    echo "Orchestrator started with PID: $PID"
    echo $PID > /tmp/proactive_ai.pid
    echo ""
    echo "To stop: ./quickstart.sh stop"
    echo "To view status: ./quickstart.sh status"
}

# Function to stop
stop_orchestrator() {
    if [ -f /tmp/proactive_ai.pid ]; then
        PID=$(cat /tmp/proactive_ai.pid)
        echo "Stopping Proactive AI (PID: $PID)..."
        kill $PID 2>/dev/null || true
        rm /tmp/proactive_ai.pid
        echo -e "${GREEN}Stopped.${NC}"
    else
        echo -e "${YELLOW}No running instance found.${NC}"
    fi
}

# Function to test
test_orchestrator() {
    echo "Testing event bus..."
    python3 "$ORCHESTRATOR" event user.message
    python3 "$ORCHESTRATOR" event monitor.alert
    python3 "$ORCHESTRATOR" event task.completed
    echo -e "${GREEN}Test events published.${NC}"
}

# Main menu
case "${1:-start}" in
    start)
        start_orchestrator
        ;;
    stop)
        stop_orchestrator
        ;;
    status)
        show_status
        ;;
    test)
        test_orchestrator
        ;;
    restart)
        stop_orchestrator
        sleep 2
        start_orchestrator
        ;;
    *)
        echo "Usage: $0 {start|stop|status|test|restart}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the Proactive AI system"
        echo "  stop    - Stop the Proactive AI system"
        echo "  status  - Show system status"
        echo "  test    - Publish test events"
        echo "  restart - Restart the system"
        exit 1
        ;;
esac
