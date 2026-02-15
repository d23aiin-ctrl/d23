#!/bin/bash

# Start All Microservices - Unified Platform v2
# Usage: ./start-all.sh [--stop] [--status] [--logs]

SERVICES_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$SERVICES_DIR/.logs"
PID_DIR="$SERVICES_DIR/.pids"

# Service definitions: name:port:directory
SERVICES=(
    "travel:8004:travel-service-clean"
    "astrology:8003:astrology-service-clean"
    "finance:8007:finance-service-clean"
    "government:8005:government-service-clean"
    "utility:8006:utility-service-clean"
    "vision:8009:vision-service-clean"
    "ai-bot:3002:ai-bot-service"
)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create directories
mkdir -p "$LOG_DIR" "$PID_DIR"

print_header() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║         Unified Platform v2 - Microservices            ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

start_service() {
    local name=$1
    local port=$2
    local dir=$3
    local full_path="$SERVICES_DIR/$dir"

    if [ ! -d "$full_path" ]; then
        echo -e "  ${RED}✗${NC} $name - Directory not found: $dir"
        return 1
    fi

    # Check if port is already in use
    if lsof -i :$port -t > /dev/null 2>&1; then
        echo -e "  ${YELLOW}⚠${NC} $name (port $port) - Already running"
        return 0
    fi

    # Start the service
    cd "$full_path"

    # Install dependencies if needed (check for venv or use system python)
    if [ ! -f "$PID_DIR/${name}.started" ]; then
        pip3 install -q --break-system-packages -r requirements.txt 2>/dev/null
    fi

    # Start service in background
    nohup python3 main.py > "$LOG_DIR/${name}.log" 2>&1 &
    local pid=$!
    echo $pid > "$PID_DIR/${name}.pid"

    # Wait a moment and check if it started
    sleep 2
    if kill -0 $pid 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} $name started on port $port (PID: $pid)"
        touch "$PID_DIR/${name}.started"
        return 0
    else
        echo -e "  ${RED}✗${NC} $name failed to start - check $LOG_DIR/${name}.log"
        return 1
    fi
}

stop_service() {
    local name=$1
    local port=$2

    # Kill by PID file
    if [ -f "$PID_DIR/${name}.pid" ]; then
        local pid=$(cat "$PID_DIR/${name}.pid")
        if kill -0 $pid 2>/dev/null; then
            kill $pid 2>/dev/null
            echo -e "  ${GREEN}✓${NC} $name stopped (PID: $pid)"
        fi
        rm -f "$PID_DIR/${name}.pid"
    fi

    # Also kill any process on the port
    local pids=$(lsof -i :$port -t 2>/dev/null)
    if [ -n "$pids" ]; then
        echo $pids | xargs kill 2>/dev/null
    fi
}

check_status() {
    local name=$1
    local port=$2

    if lsof -i :$port -t > /dev/null 2>&1; then
        # Try health check
        local health=$(curl -s --connect-timeout 2 "http://localhost:$port/health" 2>/dev/null)
        if [ -n "$health" ]; then
            echo -e "  ${GREEN}●${NC} $name (port $port) - Running"
        else
            echo -e "  ${YELLOW}●${NC} $name (port $port) - Running (no health endpoint)"
        fi
    else
        echo -e "  ${RED}●${NC} $name (port $port) - Stopped"
    fi
}

show_logs() {
    local name=$1
    if [ -f "$LOG_DIR/${name}.log" ]; then
        echo -e "\n${BLUE}=== $name logs ===${NC}"
        tail -20 "$LOG_DIR/${name}.log"
    fi
}

start_all() {
    print_header
    echo -e "${GREEN}Starting all services...${NC}\n"

    for service in "${SERVICES[@]}"; do
        IFS=':' read -r name port dir <<< "$service"
        start_service "$name" "$port" "$dir"
    done

    echo -e "\n${GREEN}All services started!${NC}"
    echo -e "\nAccess points:"
    echo -e "  ${BLUE}AI Bot UI:${NC}     http://localhost:3002"
    echo -e "  ${BLUE}Vision API:${NC}    http://localhost:8009"
    echo -e "  ${BLUE}Travel API:${NC}    http://localhost:8004"
    echo -e "  ${BLUE}Astrology API:${NC} http://localhost:8003"
    echo -e "  ${BLUE}Finance API:${NC}   http://localhost:8007"
    echo -e "  ${BLUE}Govt API:${NC}      http://localhost:8005"
    echo -e "  ${BLUE}Utility API:${NC}   http://localhost:8006"
    echo -e "\nUse ${YELLOW}./start-all.sh --status${NC} to check status"
    echo -e "Use ${YELLOW}./start-all.sh --stop${NC} to stop all services"
}

stop_all() {
    print_header
    echo -e "${RED}Stopping all services...${NC}\n"

    for service in "${SERVICES[@]}"; do
        IFS=':' read -r name port dir <<< "$service"
        stop_service "$name" "$port"
    done

    echo -e "\n${GREEN}All services stopped.${NC}"
}

status_all() {
    print_header
    echo -e "${BLUE}Service Status:${NC}\n"

    for service in "${SERVICES[@]}"; do
        IFS=':' read -r name port dir <<< "$service"
        check_status "$name" "$port"
    done
}

logs_all() {
    for service in "${SERVICES[@]}"; do
        IFS=':' read -r name port dir <<< "$service"
        show_logs "$name"
    done
}

# Main
case "$1" in
    --stop|-s)
        stop_all
        ;;
    --status|-t)
        status_all
        ;;
    --logs|-l)
        logs_all
        ;;
    --help|-h)
        echo "Usage: $0 [option]"
        echo ""
        echo "Options:"
        echo "  (none)      Start all services"
        echo "  --stop      Stop all services"
        echo "  --status    Show status of all services"
        echo "  --logs      Show recent logs"
        echo "  --help      Show this help"
        ;;
    *)
        start_all
        ;;
esac
