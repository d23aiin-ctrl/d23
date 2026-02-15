#!/bin/bash

# ============================================================
# D23 Platform - Start All Services
# ============================================================
# Usage:
#   ./start.sh              Start all services
#   ./start.sh --stop       Stop all services
#   ./start.sh --status     Check status of all services
#   ./start.sh --logs       Tail logs from all services
#   ./start.sh api          Start only API
#   ./start.sh web          Start only D23Web
#   ./start.sh micro        Start only microservices
# ============================================================

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
API_DIR="$ROOT_DIR/API"
WEB_DIR="$ROOT_DIR/D23Web"
SERVICES_DIR="$API_DIR/services"
LOG_DIR="$ROOT_DIR/.logs"
PID_DIR="$ROOT_DIR/.pids"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

mkdir -p "$LOG_DIR" "$PID_DIR"

# ============================================================
# Service Registry
# ============================================================
# Microservices: name:port:directory
MICROSERVICES=(
    "travel:8004:travel-service-clean"
    "astrology:8003:astrology-service-clean"
    "finance:8007:finance-service-clean"
    "government:8005:government-service-clean"
    "utility:8006:utility-service-clean"
    "vision:8009:vision-service-clean"
    "ai-bot:3002:ai-bot-service"
)

print_banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║               D23 AI Platform - d23.ai                  ║"
    echo "╠══════════════════════════════════════════════════════════╣"
    echo "║  Frontend:  http://localhost:5058  →  d23.ai            ║"
    echo "║  API:       http://localhost:9002  →  api.d23.ai        ║"
    echo "║  Bot:       http://localhost:9003                       ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# ============================================================
# D23Web Frontend
# ============================================================
start_web() {
    echo -e "\n${BOLD}[D23Web Frontend]${NC}"

    if lsof -i :5058 -t > /dev/null 2>&1; then
        echo -e "  ${YELLOW}⚠${NC}  Already running on port 5058"
        return 0
    fi

    cd "$WEB_DIR"

    # Install deps if node_modules missing
    if [ ! -d "node_modules" ]; then
        echo -e "  ${BLUE}→${NC}  Installing npm dependencies..."
        npm install --silent > "$LOG_DIR/web-install.log" 2>&1
    fi

    PORT=5058 nohup npm run dev > "$LOG_DIR/web.log" 2>&1 &
    echo $! > "$PID_DIR/web.pid"

    sleep 3
    if lsof -i :5058 -t > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC}  D23Web started on port 5058"
    else
        echo -e "  ${RED}✗${NC}  D23Web failed to start — check $LOG_DIR/web.log"
    fi
}

stop_web() {
    echo -e "  ${BLUE}→${NC}  Stopping D23Web..."
    lsof -ti:5058 2>/dev/null | xargs kill -9 2>/dev/null
    rm -f "$PID_DIR/web.pid"
    echo -e "  ${GREEN}✓${NC}  D23Web stopped"
}

# ============================================================
# Unified API (main.py — port 9002)
# ============================================================
start_api() {
    echo -e "\n${BOLD}[Unified API]${NC}"

    if lsof -i :9002 -t > /dev/null 2>&1; then
        echo -e "  ${YELLOW}⚠${NC}  Already running on port 9002"
        return 0
    fi

    cd "$API_DIR"

    # Create venv if missing
    if [ ! -d "venv" ]; then
        echo -e "  ${BLUE}→${NC}  Creating Python venv..."
        python3 -m venv venv
        source venv/bin/activate
        echo -e "  ${BLUE}→${NC}  Installing dependencies (this may take a minute)..."
        grep -v "^TTS\|^mlx" requirements.txt | pip install -q -r /dev/stdin > "$LOG_DIR/api-install.log" 2>&1
    else
        source venv/bin/activate
    fi

    nohup python main.py > "$LOG_DIR/api.log" 2>&1 &
    echo $! > "$PID_DIR/api.pid"

    sleep 3
    if lsof -i :9002 -t > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC}  API started on port 9002"
    else
        echo -e "  ${RED}✗${NC}  API failed to start — check $LOG_DIR/api.log"
    fi
}

stop_api() {
    echo -e "  ${BLUE}→${NC}  Stopping API..."
    lsof -ti:9002 2>/dev/null | xargs kill -9 2>/dev/null
    rm -f "$PID_DIR/api.pid"
    echo -e "  ${GREEN}✓${NC}  API stopped"
}

# ============================================================
# WhatsApp Bot (run_bot.py — port 9003)
# ============================================================
start_bot() {
    echo -e "\n${BOLD}[WhatsApp Bot]${NC}"

    if lsof -i :9003 -t > /dev/null 2>&1; then
        echo -e "  ${YELLOW}⚠${NC}  Already running on port 9003"
        return 0
    fi

    cd "$API_DIR"
    source venv/bin/activate 2>/dev/null

    nohup python run_bot.py > "$LOG_DIR/bot.log" 2>&1 &
    echo $! > "$PID_DIR/bot.pid"

    sleep 3
    if lsof -i :9003 -t > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC}  WhatsApp Bot started on port 9003"
    else
        echo -e "  ${RED}✗${NC}  WhatsApp Bot failed to start — check $LOG_DIR/bot.log"
    fi
}

stop_bot() {
    echo -e "  ${BLUE}→${NC}  Stopping WhatsApp Bot..."
    lsof -ti:9003 2>/dev/null | xargs kill -9 2>/dev/null
    rm -f "$PID_DIR/bot.pid"
    echo -e "  ${GREEN}✓${NC}  WhatsApp Bot stopped"
}

# ============================================================
# Microservices
# ============================================================
start_microservices() {
    echo -e "\n${BOLD}[Microservices]${NC}"

    for service in "${MICROSERVICES[@]}"; do
        IFS=':' read -r name port dir <<< "$service"
        local full_path="$SERVICES_DIR/$dir"

        if [ ! -d "$full_path" ]; then
            echo -e "  ${RED}✗${NC}  $name — directory not found: $dir"
            continue
        fi

        if lsof -i :$port -t > /dev/null 2>&1; then
            echo -e "  ${YELLOW}⚠${NC}  $name already running on port $port"
            continue
        fi

        cd "$full_path"
        pip3 install -q --break-system-packages -r requirements.txt 2>/dev/null
        nohup python3 main.py > "$LOG_DIR/${name}.log" 2>&1 &
        echo $! > "$PID_DIR/${name}.pid"

        sleep 1
        if kill -0 $! 2>/dev/null; then
            echo -e "  ${GREEN}✓${NC}  $name started on port $port"
        else
            echo -e "  ${RED}✗${NC}  $name failed — check $LOG_DIR/${name}.log"
        fi
    done
}

stop_microservices() {
    echo -e "  ${BLUE}→${NC}  Stopping microservices..."
    for service in "${MICROSERVICES[@]}"; do
        IFS=':' read -r name port dir <<< "$service"
        lsof -ti:$port 2>/dev/null | xargs kill -9 2>/dev/null
        rm -f "$PID_DIR/${name}.pid"
    done
    echo -e "  ${GREEN}✓${NC}  All microservices stopped"
}

# ============================================================
# Status
# ============================================================
check_status() {
    print_banner
    echo -e "${BOLD}Service Status:${NC}\n"

    # Core services
    for label_port in "D23Web:5058" "Unified API:9002" "WhatsApp Bot:9003"; do
        IFS=':' read -r label port <<< "$label_port"
        if lsof -i :$port -t > /dev/null 2>&1; then
            echo -e "  ${GREEN}●${NC}  $label (port $port) — Running"
        else
            echo -e "  ${RED}●${NC}  $label (port $port) — Stopped"
        fi
    done

    echo ""

    # Microservices
    for service in "${MICROSERVICES[@]}"; do
        IFS=':' read -r name port dir <<< "$service"
        if lsof -i :$port -t > /dev/null 2>&1; then
            echo -e "  ${GREEN}●${NC}  $name (port $port) — Running"
        else
            echo -e "  ${RED}●${NC}  $name (port $port) — Stopped"
        fi
    done
}

# ============================================================
# Logs
# ============================================================
show_logs() {
    echo -e "${BOLD}Tailing all logs (Ctrl+C to stop)...${NC}\n"
    tail -f "$LOG_DIR"/*.log
}

# ============================================================
# Start / Stop All
# ============================================================
start_all() {
    print_banner
    echo -e "${GREEN}${BOLD}Starting D23 Platform...${NC}"
    start_web
    start_api
    start_bot
    start_microservices

    echo -e "\n${GREEN}${BOLD}All services started!${NC}"
    echo -e "\nAccess:"
    echo -e "  ${CYAN}Frontend:${NC}    http://localhost:5058"
    echo -e "  ${CYAN}API Docs:${NC}    http://localhost:9002/docs"
    echo -e "  ${CYAN}Bot Health:${NC}  http://localhost:9003/health"
    echo -e "\n  Logs: ${YELLOW}./start.sh --logs${NC}"
    echo -e "  Stop: ${YELLOW}./start.sh --stop${NC}"
}

stop_all() {
    print_banner
    echo -e "${RED}${BOLD}Stopping D23 Platform...${NC}\n"
    stop_web
    stop_api
    stop_bot
    stop_microservices
    echo -e "\n${GREEN}${BOLD}All services stopped.${NC}"
}

# ============================================================
# Main
# ============================================================
case "$1" in
    --stop|-s)
        stop_all
        ;;
    --status|-t)
        check_status
        ;;
    --logs|-l)
        show_logs
        ;;
    web)
        print_banner
        start_web
        ;;
    api)
        print_banner
        start_api
        ;;
    bot)
        print_banner
        start_bot
        ;;
    micro)
        print_banner
        start_microservices
        ;;
    --help|-h)
        print_banner
        echo "Usage: ./start.sh [command]"
        echo ""
        echo "Commands:"
        echo "  (none)      Start all services"
        echo "  web         Start only D23Web frontend"
        echo "  api         Start only Unified API"
        echo "  bot         Start only WhatsApp Bot"
        echo "  micro       Start only microservices"
        echo "  --stop      Stop all services"
        echo "  --status    Check status of all services"
        echo "  --logs      Tail all logs"
        echo "  --help      Show this help"
        ;;
    *)
        start_all
        ;;
esac
