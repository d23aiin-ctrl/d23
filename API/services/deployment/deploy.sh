#!/bin/bash

# OhGrt Microservices Deployment Script
# Usage: ./deploy.sh [dev|prod|stop|logs|status]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Development deployment
deploy_dev() {
    log_info "Starting development deployment..."
    cd ..
    docker-compose up --build -d
    log_info "Development services started!"
    echo ""
    echo "Services available at:"
    echo "  - Travel:     http://localhost:8001/docs"
    echo "  - Astrology:  http://localhost:8003/docs"
    echo "  - Finance:    http://localhost:8004/docs"
    echo "  - Government: http://localhost:8005/docs"
    echo "  - Utility:    http://localhost:8006/docs"
}

# Production deployment
deploy_prod() {
    log_info "Starting production deployment..."

    # Create SSL directory if not exists
    mkdir -p nginx/ssl

    # Check if SSL certificates exist
    if [ ! -f "nginx/ssl/fullchain.pem" ]; then
        log_warn "SSL certificates not found. Running without HTTPS."
        log_warn "For production, add certificates to deployment/nginx/ssl/"
    fi

    docker-compose -f docker-compose.prod.yml up --build -d

    log_info "Production services started!"
    echo ""
    echo "API Gateway: http://localhost (or your domain)"
    echo ""
    echo "Endpoints:"
    echo "  - /travel/*"
    echo "  - /astrology/*"
    echo "  - /finance/*"
    echo "  - /government/*"
    echo "  - /utility/*"
}

# Stop services
stop_services() {
    log_info "Stopping services..."
    cd ..
    docker-compose down 2>/dev/null || true
    cd deployment
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
    log_info "All services stopped."
}

# Show logs
show_logs() {
    SERVICE=$2
    if [ -z "$SERVICE" ]; then
        cd ..
        docker-compose logs -f
    else
        cd ..
        docker-compose logs -f "$SERVICE"
    fi
}

# Show status
show_status() {
    log_info "Service Status:"
    echo ""
    cd ..
    docker-compose ps
}

# Health check
health_check() {
    log_info "Checking service health..."
    echo ""

    services=("8001:Travel" "8003:Astrology" "8004:Finance" "8005:Government" "8006:Utility")

    for service in "${services[@]}"; do
        port="${service%%:*}"
        name="${service##*:}"

        if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
            echo -e "  ${GREEN}✓${NC} $name (port $port) - Healthy"
        else
            echo -e "  ${RED}✗${NC} $name (port $port) - Not responding"
        fi
    done
}

# Main
case "$1" in
    dev)
        deploy_dev
        ;;
    prod)
        deploy_prod
        ;;
    stop)
        stop_services
        ;;
    logs)
        show_logs "$@"
        ;;
    status)
        show_status
        ;;
    health)
        health_check
        ;;
    *)
        echo "OhGrt Microservices Deployment"
        echo ""
        echo "Usage: $0 {dev|prod|stop|logs|status|health}"
        echo ""
        echo "Commands:"
        echo "  dev     - Start development environment (direct ports)"
        echo "  prod    - Start production environment (with Nginx)"
        echo "  stop    - Stop all services"
        echo "  logs    - Show logs (optionally: logs <service-name>)"
        echo "  status  - Show service status"
        echo "  health  - Check health of all services"
        exit 1
        ;;
esac
