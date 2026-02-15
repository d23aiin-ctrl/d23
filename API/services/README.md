# OhGrt Microservices Architecture

This directory contains the microservices implementation of the OhGrt platform.
Each service is independently deployable and can be accessed by D23Web directly.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENTS                                         │
│   D23Web (Next.js)  │  iOS App (Swift)  │  WhatsApp  │  Android             │
└───────────┬─────────────────┬───────────────────┬────────────────────────────┘
            │                 │                   │
            ▼                 ▼                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY (Port 8000)                              │
│   • Request Routing    • Authentication    • Rate Limiting    • CORS        │
└───────────┬─────────────────┬───────────────────┬────────────────────────────┘
            │                 │                   │
    ┌───────┴────┬────────────┼───────────┬───────┴────┬─────────────┐
    ▼            ▼            ▼           ▼            ▼             ▼
┌────────┐ ┌────────┐ ┌───────────┐ ┌────────┐ ┌──────────┐ ┌────────────┐
│  Auth  │ │  Chat  │ │ Astrology │ │ Travel │ │Government│ │  Utility   │
│ :8001  │ │ :8002  │ │   :8003   │ │ :8004  │ │  :8005   │ │   :8006    │
└────────┘ └────────┘ └───────────┘ └────────┘ └──────────┘ └────────────┘

┌────────┐ ┌────────┐ ┌───────────┐ ┌────────┐ ┌──────────┐
│Finance │ │  Jobs  │ │  Health   │ │  Agri  │ │ Document │
│ :8007  │ │ :8008  │ │   :8009   │ │ :8010  │ │  :8011   │
└────────┘ └────────┘ └───────────┘ └────────┘ └──────────┘

┌──────────────┐
│ Notification │
│    :8012     │
└──────────────┘
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| api-gateway | 8000 | Central routing, auth validation, rate limiting |
| auth-service | 8001 | Firebase auth, JWT tokens, OAuth flows |
| chat-service | 8002 | LLM orchestration, intent routing |
| astrology-service | 8003 | Horoscope, Kundli, Matching, Dosha, Panchang |
| travel-service | 8004 | PNR, Train schedule, Running status |
| government-service | 8005 | PM-KISAN, DL, Certificates, E-Challan |
| utility-service | 8006 | Weather, News, Gold/Fuel prices |
| finance-service | 8007 | EMI calculator, Loans, Stocks, MF |
| jobs-service | 8008 | Sarkari Naukri, Job alerts |
| health-service | 8009 | Symptom checker, Medicine info |
| agriculture-service | 8010 | Mandi prices, Crop advisory |
| document-service | 8011 | DigiLocker, Exam results |
| notification-service | 8012 | WhatsApp, Email, SMS, Push |

## Quick Start

### Docker (Clean Architecture Services)

```bash
cd services/

# Build and start all Clean Architecture services
docker-compose up --build

# Run in background (detached mode)
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

**Service URLs after starting:**
| Service | API Docs | Health Check |
|---------|----------|--------------|
| Travel | http://localhost:8001/docs | http://localhost:8001/health |
| Astrology | http://localhost:8003/docs | http://localhost:8003/health |
| Finance | http://localhost:8004/docs | http://localhost:8004/health |
| Government | http://localhost:8005/docs | http://localhost:8005/health |
| Utility | http://localhost:8006/docs | http://localhost:8006/health |

### Local Development (without Docker)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn pydantic pytest pytest-asyncio httpx

# Start individual service
cd astrology-service-clean
python main.py
```

### Environment Setup

```bash
# Copy environment template
cp .env.example .env.microservices

# Edit with your API keys
nano .env.microservices
```

## Directory Structure

```
services/
├── api-gateway/          # Central API Gateway
├── auth-service/         # Authentication & Authorization
├── chat-service/         # LLM & Intent Orchestration
├── astrology-service/    # Vedic Astrology
├── travel-service/       # Railways & Travel
├── government-service/   # Government Services
├── utility-service/      # Weather, News, Utilities
├── finance-service/      # Financial Tools
├── jobs-service/         # Employment & Alerts
├── health-service/       # Healthcare
├── agriculture-service/  # Farming & Mandi
├── document-service/     # Documents & Results
└── notification-service/ # Messaging & Notifications

shared/
├── ohgrt-core/          # Core types, errors, utilities
├── ohgrt-auth/          # Auth middleware & JWT
└── ohgrt-clients/       # Service client libraries
```

## Communication

- **Sync (REST)**: Direct HTTP calls between services
- **Async (Redis Pub/Sub)**: Event-driven notifications
- **Service Discovery**: Docker DNS / Kubernetes DNS

## D23Web Integration

D23Web can call services in two ways:

1. **Through Gateway** (Recommended):
   ```typescript
   fetch('https://api.ohgrt.com/astrology/horoscope', { ... })
   ```

2. **Direct Service Call** (High-performance):
   ```typescript
   fetch('https://astrology.ohgrt.com/horoscope', { ... })
   ```

## Deployment

### Docker Compose (Development)
```bash
docker-compose -f docker-compose.microservices.yml up -d
```

### Kubernetes (Production)
```bash
kubectl apply -f kubernetes/
```

## Monitoring

- **Metrics**: Prometheus + Grafana (port 9090, 3001)
- **Tracing**: Jaeger (port 16686)
- **Logs**: ELK Stack or Loki

## Adding a New Service

1. Create service directory: `services/my-service/`
2. Copy template from `services/_template/`
3. Update `docker-compose.microservices.yml`
4. Add route in `api-gateway/routes.py`
5. Create client in `shared/ohgrt-clients/`
