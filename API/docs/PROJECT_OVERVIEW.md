# OhGrt - AI-Powered Super App Platform

## Executive Summary

OhGrt is a **production-ready AI platform** that delivers intelligent services through multiple channels—WhatsApp, iOS app, and Web. Built with a modern event-driven architecture, it uses LLM-powered intent detection to route users to 40+ specialized services including astrology, government services, travel, and more.

**Think of it as**: The backend infrastructure for building India's next super-app, similar to WeChat or Grab but AI-native.

---

## The Problem We Solve

Indian users need access to multiple services daily:
- Checking train PNR status
- Getting horoscopes
- Finding government scheme eligibility
- Checking vehicle challans
- Reading emails

Currently, users must:
1. Download multiple apps
2. Navigate complex government portals
3. Remember multiple logins
4. Deal with non-vernacular interfaces

**OhGrt consolidates all these into a single conversational interface** that works in 22 Indian languages.

---

## Platform Capabilities

### 🔮 Astrology Suite (AstroTalk-like)
- Daily/Weekly/Monthly horoscopes
- Birth chart (Kundli) generation
- Marriage compatibility (Gun Milan)
- Dosha analysis (Manglik, Kaal Sarp, Sade Sati)
- Life predictions (career, marriage, children)
- Panchang & Muhurta finder
- Remedy suggestions (gemstones, mantras)

### 🏛️ Government Services (Bihar Focus, Expanding)
- **PM-KISAN**: Beneficiary status, installment info
- **Driving License**: Application status via Parivahan
- **Birth/Death Certificates**: CRSORGI portal guidance
- **Property Registration**: Stamp duty calculator
- **BSEB Results**: Bihar Board matric results
- **E-Challan**: Vehicle fine lookup
- **Sarkari Naukri**: Government job notifications
- **Welfare Schemes**: Eligibility checker

### 🚆 Travel Services
- PNR status (Indian Railways)
- Live train running status
- Multi-city journey planning
- Metro routes & fares (Delhi, Bangalore)

### 🛠️ Utility Services
- Weather forecasts (any city)
- News aggregation (topic-based)
- Stock prices & market data
- Live cricket scores
- Restaurant & local business discovery
- Event finder (concerts, IPL, shows)
- Reminders & scheduled notifications

### 🤖 AI Features
- Multi-turn conversations with memory
- Image generation (text-to-image)
- Image analysis (describe, extract text)
- PDF upload & Q&A (RAG)
- Fact-checking service
- Smart language detection & translation

---

## Technical Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
├─────────────┬─────────────────┬─────────────────────────────────┤
│  WhatsApp   │    iOS App      │         Web (D23Web)            │
│  (Meta API) │  (SwiftUI)      │      (Next.js/React)            │
└──────┬──────┴────────┬────────┴────────────────┬────────────────┘
       │               │                         │
       ▼               ▼                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY (FastAPI)                       │
│  • JWT Auth  • Rate Limiting  • CORS  • Health Checks           │
└─────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INTENT DETECTION (GPT-4o-mini)                │
│  • 40+ intent types  • Entity extraction  • Confidence scoring  │
└─────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LANGGRAPH ORCHESTRATION                       │
│  • Conditional routing  • State management  • Multi-agent flow  │
└─────────────────────────────────────────────────────────────────┘
       │
       ├──────────────────────────────────────────┐
       ▼                                          ▼
┌──────────────────┐                    ┌──────────────────────────┐
│  TOOL HANDLERS   │                    │    EXTERNAL SERVICES     │
│  (36+ Nodes)     │                    │                          │
├──────────────────┤                    │  • OpenAI (LLM)          │
│ • Astrology      │                    │  • Railway API           │
│ • Travel         │                    │  • Weather API           │
│ • Government     │                    │  • News API              │
│ • Utilities      │                    │  • FAL.ai (Images)       │
│ • AI Features    │                    │  • Tavily (Search)       │
└──────────────────┘                    └──────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                  │
├─────────────────────┬───────────────────────────────────────────┤
│  PostgreSQL         │  Redis                                    │
│  • Users            │  • Session cache                          │
│  • Chat history     │  • Rate limits                            │
│  • OAuth tokens     │  • Context store                          │
│  • Scheduled tasks  │  • Tool cache                             │
└─────────────────────┴───────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **API Framework** | FastAPI 0.109+, Uvicorn (ASGI) |
| **LLM Orchestration** | LangGraph 0.2+, LangChain 1.0+ |
| **AI Models** | OpenAI GPT-4o-mini, GPT-4V (vision) |
| **Database** | PostgreSQL 12+ with pgvector |
| **Cache** | Redis 5.0+ |
| **Auth** | Firebase Admin SDK + JWT |
| **Image Gen** | FAL.ai (FLUX models) |
| **TTS/STT** | Edge TTS, MLX Whisper |
| **Search** | Tavily, Serper (Google) |
| **Messaging** | Meta WhatsApp Cloud API |
| **iOS** | SwiftUI, Async/Await, Clean Architecture |
| **Web** | Next.js 14, React 18, TypeScript |

---

## Key Differentiators

### 1. **LangGraph-Powered Routing**
Unlike simple chatbots, we use a graph-based workflow engine that:
- Intelligently routes to specialized handlers
- Maintains conversation state across turns
- Handles complex multi-step tasks
- Falls back gracefully when uncertain

### 2. **True Multi-Language Support**
- 22 Indian languages (Hindi, Bengali, Tamil, Telugu, Kannada, etc.)
- Auto-detection on first message
- Template-based translations (no API latency)
- Supports non-Latin scripts natively

### 3. **Production-Grade Infrastructure**
- Async/await throughout (handles 1000s of concurrent users)
- Redis caching for sub-100ms responses
- Health checks for Kubernetes deployment
- Prometheus metrics for monitoring
- LangSmith integration for LLM debugging

### 4. **Modular & Extensible**
- Add new intents in ~50 lines of code
- Shared tools between WhatsApp and API
- OAuth integrations ready (Gmail, Slack, GitHub, Jira)
- MCP (Model Context Protocol) for custom tool servers

---

## Business Metrics Potential

| Metric | Description |
|--------|-------------|
| **MAU** | WhatsApp reach: 500M+ users in India |
| **Engagement** | Astrology users check horoscope daily |
| **Retention** | Government services create recurring need |
| **Monetization** | Premium horoscopes, priority support, API access |

---

## Code Quality

```
📊 Codebase Stats
─────────────────────────────
Lines of Code:     ~50,000+
Test Coverage:     Unit + Integration
Type Safety:       Pydantic models throughout
Documentation:     Inline + API docs (Swagger)
Architecture:      Clean Architecture / DDD principles
```

**Code Organization:**
```
unified_platform/
├── ohgrt_api/          # REST API (FastAPI)
│   ├── auth/           # Authentication
│   ├── chat/           # Chat endpoints
│   ├── services/       # Business logic
│   └── db/             # Database models
├── whatsapp_bot/       # WhatsApp integration
│   ├── webhook/        # Meta webhook handler
│   └── graph/          # Intent routing (36 nodes)
├── common/             # Shared components
│   ├── tools/          # 24+ specialized tools
│   ├── astro/          # Vedic astrology engine
│   ├── services/       # Shared services
│   └── i18n/           # Internationalization
├── D23Web/             # Next.js web frontend
└── OhGrtApp/           # iOS SwiftUI app
```

---

## Security & Compliance

- ✅ Firebase authentication (Google-grade security)
- ✅ JWT with refresh token rotation
- ✅ HMAC-SHA256 webhook verification
- ✅ Environment-based secrets management
- ✅ CORS and security headers
- ✅ Rate limiting per user/IP
- ✅ No PII stored in logs

---

## Deployment Ready

```bash
# Local development
docker-compose up

# Production (Kubernetes)
kubectl apply -f k8s/

# Health checks
GET /health/live   # Liveness probe
GET /health/ready  # Readiness probe
GET /metrics       # Prometheus metrics
```

---

## Roadmap

### Completed ✅
- WhatsApp bot with 40+ intents
- iOS app (SwiftUI)
- Web frontend (Next.js)
- Astrology suite
- Government services (Bihar)
- Travel services
- Utility services

### In Progress 🚧
- Gmail integration (read/send via chat)
- Email scheduling
- Voice message support

### Planned 📋
- Payment integration (UPI)
- Expand government services (all states)
- B2B API marketplace
- White-label solution

---

## Why This Architecture?

| Traditional Approach | OhGrt Approach |
|---------------------|----------------|
| Monolithic chatbot | Microservices + LangGraph |
| Rule-based routing | LLM intent detection |
| Single language | 22 languages |
| One channel | WhatsApp + iOS + Web |
| Static responses | Dynamic tool execution |

---

## Team & Contact

Built by a team with experience in:
- Large-scale distributed systems
- AI/ML production deployments
- Mobile app development
- Government tech projects

---

## Quick Demo

**Try these on WhatsApp:**
```
"मेरा राशिफल बताओ"          → Daily horoscope in Hindi
"PNR status 1234567890"     → Railway booking status
"PM Kisan status"           → Check PM-KISAN beneficiary
"Weather in Patna"          → Current weather
"जन्म प्रमाण पत्र"            → Birth certificate guidance
"Generate image of sunset"  → AI image generation
```

---

## Summary

OhGrt is **not just a chatbot**—it's a full-stack AI platform that:

1. **Understands** natural language in 22 Indian languages
2. **Routes** intelligently to 40+ specialized services
3. **Executes** complex tasks (API calls, calculations, searches)
4. **Responds** in the user's preferred language
5. **Scales** to millions of users with production infrastructure

**The future of Indian digital services is conversational. We're building it.**

---

*For technical deep-dives, API documentation, or partnership discussions, contact the team.*
