# D23 AI Platform - Feature List

## Overview
D23 AI is a unified AI-powered platform that provides intelligent services through natural language conversation. Supports **English, Hindi, and 11+ Indian languages**.

---

## Core Platform Features

### 1. AI Chat Interface
- Natural language understanding (NLU)
- Multi-language support (Hindi, English, Tamil, Telugu, etc.)
- Context-aware conversations
- Real-time WebSocket chat
- Intent classification with 23+ intents
- Smart entity extraction

### 2. WhatsApp Bot Integration
- Full WhatsApp Business API integration
- Image/document processing
- Voice message support
- Rich message formatting
- Subscription management

---

## Service Modules

### Travel Services (Port 8004)
| Feature | Description |
|---------|-------------|
| PNR Status | Check Indian Railways PNR status |
| Train Schedule | Get complete train timetable |
| Live Train Status | Real-time train running status |
| Train Search | Find trains between stations |

### Astrology Services (Port 8003)
| Feature | Description |
|---------|-------------|
| Daily Horoscope | Zodiac-based daily predictions |
| Kundli Generation | Birth chart calculation |
| Kundli Matching | Compatibility analysis |
| Panchang | Daily Hindu calendar & muhurat |
| Dosha Analysis | Manglik & other dosha checks |

### Finance Services (Port 8007)
| Feature | Description |
|---------|-------------|
| EMI Calculator | Loan EMI calculation with amortization |
| SIP Calculator | Mutual fund SIP returns projection |
| Stock Prices | Real-time Indian stock market data |

### Government Services (Port 8005)
| Feature | Description |
|---------|-------------|
| PM Kisan Status | Check PM-KISAN beneficiary status |
| Driving License | DL status verification |
| Vehicle RC Info | Vehicle registration details |
| E-Challan | Traffic challan check |

### Utility Services (Port 8006)
| Feature | Description |
|---------|-------------|
| Weather | Current weather & forecast |
| Gold Price | Today's gold rates (22K/24K) |
| Fuel Price | Petrol/diesel prices by city |
| Currency Exchange | Real-time forex rates |
| Pincode Lookup | Area details by pincode |
| IFSC Lookup | Bank branch by IFSC code |
| Holiday Calendar | Public holidays list |

### Vision Services (Port 8009)
| Feature | Description |
|---------|-------------|
| Image Description | AI-powered image analysis |
| Text Extraction (OCR) | Extract text from images |
| Object Detection | Identify objects in images |
| Document Analysis | Parse documents & forms |
| Receipt Analysis | Extract receipt/bill data |
| Food Identification | Identify food items |
| Custom Queries | Ask questions about images |

---

## Technical Highlights

### Architecture
- **Microservices Architecture** - 7 independent services
- **Clean Architecture** - Domain-driven design
- **FastAPI** - High-performance async APIs
- **WebSocket** - Real-time communication

### AI/ML Capabilities
- **LLM Integration** - OpenAI GPT-4o-mini
- **Vision AI** - DashScope Qwen VL + Ollama fallback
- **Intent Classification** - Hybrid LLM + rule-based
- **Entity Extraction** - Regex + NLP patterns

### Multi-Language Support
- English
- Hindi (हिंदी)
- Tamil (தமிழ்)
- Telugu (తెలుగు)
- Kannada (ಕನ್ನಡ)
- Malayalam (മലയാളം)
- Bengali (বাংলা)
- Marathi (मराठी)
- Gujarati (ગુજરાતી)
- Punjabi (ਪੰਜਾਬੀ)
- Odia (ଓଡ଼ିଆ)

### DevOps
- Docker containerization
- Single-command service management
- Health monitoring endpoints
- Prometheus metrics ready

---

## Sample Queries

```
"Check PNR 4521678903"
"मेष राशिफल बताओ" (Tell me Aries horoscope)
"Calculate EMI for 50 lakh at 8.5% for 20 years"
"Weather in Mumbai"
"Gold rate today"
"Check vehicle DL01AB1234"
"PM Kisan status for 9876543210"
"Train from Delhi to Mumbai"
```

---

## API Endpoints Summary

| Service | Endpoints |
|---------|-----------|
| Travel | 4 endpoints |
| Astrology | 5 endpoints |
| Finance | 3 endpoints |
| Government | 4 endpoints |
| Utility | 7 endpoints |
| Vision | 7 endpoints |
| **Total** | **30+ API endpoints** |

---

## Access Points

| Service | URL |
|---------|-----|
| AI Chat UI | http://localhost:3002 |
| Travel API | http://localhost:8004 |
| Astrology API | http://localhost:8003 |
| Finance API | http://localhost:8007 |
| Government API | http://localhost:8005 |
| Utility API | http://localhost:8006 |
| Vision API | http://localhost:8009 |

---

## Quick Start

```bash
# Start all services
./services/start-all.sh

# Check status
./services/start-all.sh --status

# Stop all services
./services/start-all.sh --stop
```

---

*Built with Clean Architecture | Powered by AI*
