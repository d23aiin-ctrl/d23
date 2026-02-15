# D23 AI Platform

A unified AI-powered platform with 7 microservices, supporting 11+ Indian languages.

## Quick Start

```bash
# Start all microservices
./services/start-all.sh

# Check status
./services/start-all.sh --status

# Stop all services
./services/start-all.sh --stop
```

## Access Points

| Service | URL | Port |
|---------|-----|------|
| AI Chat UI | http://localhost:3002 | 3002 |
| Travel API | http://localhost:8004 | 8004 |
| Astrology API | http://localhost:8003 | 8003 |
| Finance API | http://localhost:8007 | 8007 |
| Government API | http://localhost:8005 | 8005 |
| Utility API | http://localhost:8006 | 8006 |
| Vision API | http://localhost:8009 | 8009 |

## Project Structure

```
unified_platform_v2/
├── common/              # Shared utilities & tools
├── ohgrt_api/           # Main API (port 9002)
├── whatsapp_bot/        # WhatsApp bot (port 9003)
├── services/            # Microservices
│   ├── ai-bot-service/
│   ├── travel-service-clean/
│   ├── astrology-service-clean/
│   ├── finance-service-clean/
│   ├── government-service-clean/
│   ├── utility-service-clean/
│   ├── vision-service-clean/
│   └── start-all.sh
├── docker/              # Docker configuration
│   ├── Dockerfile.api
│   ├── Dockerfile.bot
│   └── docker-compose.yml
├── docs/                # Documentation
│   ├── FEATURES.md
│   ├── ARCHITECTURE_REVIEW.md
│   ├── BACKEND_MODULARIZATION.md
│   ├── ENVIRONMENT_SETUP.md
│   └── PROJECT_OVERVIEW.md
├── scripts/             # Utility scripts
│   └── switch-env.sh
├── data/                # Data files
├── main.py              # Main entry point
├── run_api.py           # API runner (used by Docker)
└── run_bot.py           # Bot runner (used by Docker)
```

## Entry Points

| File | Purpose | Usage |
|------|---------|-------|
| `main.py` | Main application entry | `python main.py` |
| `run_api.py` | OhGrt API server (Docker) | `python run_api.py` (port 9002) |
| `run_bot.py` | WhatsApp Bot server (Docker) | `python run_bot.py` (port 9003) |

## Services Overview

| Service | Features |
|---------|----------|
| **Travel** | PNR status, train schedule, live status, train search |
| **Astrology** | Horoscope, Kundli, matching, Panchang |
| **Finance** | EMI calculator, SIP calculator, stock prices |
| **Government** | PM Kisan, DL status, vehicle RC, e-challan |
| **Utility** | Weather, gold price, fuel price, currency, IFSC |
| **Vision** | OCR, object detection, document analysis |
| **AI Bot** | Chat interface, intent classification, multi-language |

## Tech Stack

- **Backend**: Python, FastAPI, WebSocket
- **AI/ML**: OpenAI GPT-4o-mini, DashScope Qwen VL
- **Architecture**: Clean Architecture, Microservices
- **Languages**: 11+ Indian languages supported

## Docker

```bash
# Build and run with docker-compose
cd docker
docker-compose up

# Build individually
docker build -f docker/Dockerfile.api -t ohgrt-api .
docker build -f docker/Dockerfile.bot -t whatsapp-bot .
```

## Documentation

See `docs/` folder:
- [Features](docs/FEATURES.md)
- [Architecture](docs/ARCHITECTURE_REVIEW.md)
- [Environment Setup](docs/ENVIRONMENT_SETUP.md)
- [Project Overview](docs/PROJECT_OVERVIEW.md)

## License

Proprietary - All rights reserved.
