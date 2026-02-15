# Architecture Review - OhGrt Platform

## Overview

This document provides a technical review of the OhGrt platform architecture, highlighting strengths, areas for improvement, and recommendations.

---

## 🟢 Architectural Strengths

### 1. **LangGraph-Based Orchestration**
The use of LangGraph for workflow orchestration is excellent:
- Enables complex multi-step reasoning
- Maintains state across conversation turns
- Allows conditional routing based on intent
- Easy to add new nodes/handlers

**Code Quality**: The graph definitions in `whatsapp_bot/graph/graph.py` are well-structured with clear routing logic.

### 2. **Clean Separation of Concerns**
```
ohgrt_api/     → API layer (HTTP concerns)
common/        → Shared business logic
whatsapp_bot/  → Channel-specific handling
```
This allows:
- Independent deployment of components
- Code reuse between channels
- Easier testing of individual layers

### 3. **Pydantic-First Data Modeling**
Excellent use of Pydantic models throughout:
- Request/response validation
- Structured LLM outputs (`IntentClassification`)
- Configuration management (`BaseSettings`)
- Type safety with IDE support

### 4. **Async-First Design**
All I/O operations are async:
```python
async def handle_weather(state: BotState) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(...)
```
This enables high concurrency without thread overhead.

### 5. **Intent Detection with Structured Output**
The hybrid approach is smart:
1. **Fast-path**: Keyword matching for common patterns
2. **LLM fallback**: GPT-4o-mini with structured output for ambiguous queries

```python
class IntentClassification(BaseModel):
    intent: str = Field(description="...")
    confidence: float
    entities: dict
```

### 6. **Multi-Language Support Architecture**
Well-designed i18n system:
- Language detection at entry point
- Template-based translations (fast, no API calls)
- Response formatting respects detected language

### 7. **Tool Abstraction**
Each tool returns a consistent `ToolResult`:
```python
@dataclass
class ToolResult:
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None
    tool_name: str
```
This makes error handling uniform across 24+ tools.

---

## 🟡 Areas for Improvement

### 1. **Duplicate Intent Detection Files**
**Issue**: Two intent detection files exist:
- `common/graph/nodes/intent.py` (edited but not used by WhatsApp)
- `whatsapp_bot/graph/nodes/intent_v2.py` (actually used)

**Impact**: Confusion during development, bugs when editing wrong file.

**Recommendation**:
```python
# Consolidate into single source of truth
# common/graph/nodes/intent.py → Master intent detection
# whatsapp_bot/graph/nodes/intent_v2.py → Import from common
```

### 2. **Large Intent Detection Files**
**Issue**: `intent_v2.py` is ~3000 lines with many keyword lists.

**Recommendation**: Break into modules:
```
common/intents/
├── __init__.py
├── classifier.py      # Main IntentClassification logic
├── keywords/
│   ├── astrology.py   # Astrology keywords
│   ├── travel.py      # Travel keywords
│   ├── government.py  # Govt services keywords
│   └── utilities.py   # Weather, news, etc.
└── patterns/
    ├── hindi.py       # Hindi-specific patterns
    └── english.py     # English patterns
```

### 3. **Hardcoded Portal URLs**
**Issue**: URLs like `https://pmkisan.gov.in` are hardcoded in tools.

**Recommendation**: Move to configuration:
```python
# common/config/external_urls.py
class ExternalURLs(BaseSettings):
    PMKISAN_PORTAL: str = "https://pmkisan.gov.in"
    PARIVAHAN_PORTAL: str = "https://parivahan.gov.in"
    CRSORGI_PORTAL: str = "https://crsorgi.gov.in"
```

### 4. **Missing Error Boundaries**
**Issue**: Some nodes don't have comprehensive error handling.

**Recommendation**: Add decorator for consistent error handling:
```python
def node_error_handler(func):
    @wraps(func)
    async def wrapper(state: BotState) -> dict:
        try:
            return await func(state)
        except Exception as e:
            logger.exception(f"Error in {func.__name__}")
            return {
                "response_text": _get_error_message(state),
                "error": str(e),
            }
    return wrapper
```

### 5. **Database Session Management**
**Issue**: Manual session management in some handlers:
```python
db = SessionLocal()
try:
    # ... operations
finally:
    db.close()
```

**Recommendation**: Use dependency injection consistently:
```python
from fastapi import Depends
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/users")
async def get_users(db: Session = Depends(get_db)):
    ...
```

### 6. **Missing Rate Limiting on WhatsApp Webhook**
**Issue**: WhatsApp webhook doesn't have explicit rate limiting.

**Recommendation**: Add rate limiting middleware:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/webhook")
@limiter.limit("100/minute")
async def webhook_handler(request: Request):
    ...
```

### 7. **Astrology Engine Performance**
**Issue**: Swiss Ephemeris calculations are synchronous.

**Recommendation**: Run in thread pool for CPU-bound operations:
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)

async def calculate_chart(birth_data):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        executor,
        _sync_calculate_chart,
        birth_data
    )
```

---

## 🔴 Critical Recommendations

### 1. **Add Comprehensive Logging**
Current logging is inconsistent. Implement structured logging:
```python
import structlog

logger = structlog.get_logger()

logger.info(
    "intent_detected",
    intent=intent,
    confidence=confidence,
    user_id=user_id,
    latency_ms=latency,
)
```

### 2. **Implement Circuit Breakers**
External API calls should have circuit breakers:
```python
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=30)
async def call_railway_api(pnr: str):
    ...
```

### 3. **Add Request Tracing**
Implement distributed tracing for debugging:
```python
# Add trace_id to all requests
@app.middleware("http")
async def add_trace_id(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
    with structlog.contextvars.bound_contextvars(trace_id=trace_id):
        response = await call_next(request)
        response.headers["X-Trace-ID"] = trace_id
        return response
```

### 4. **Implement Caching Strategy**
Many API responses can be cached:
```python
# Weather: 10 min cache
# News: 5 min cache
# Stock prices: 1 min cache
# Horoscopes: 1 hour cache

from functools import lru_cache
import aioredis

async def get_cached_weather(city: str):
    cache_key = f"weather:{city}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    result = await fetch_weather(city)
    await redis.setex(cache_key, 600, json.dumps(result))
    return result
```

---

## 📊 Architecture Diagram (Current)

```
                                    ┌──────────────────┐
                                    │   Meta WhatsApp  │
                                    │   Cloud API      │
                                    └────────┬─────────┘
                                             │
┌────────────────┐   ┌────────────────┐     │     ┌────────────────┐
│   iOS App      │   │   Web (D23)    │     │     │   Other APIs   │
│   (SwiftUI)    │   │   (Next.js)    │     │     │   (Future)     │
└───────┬────────┘   └───────┬────────┘     │     └───────┬────────┘
        │                    │              │             │
        └────────────────────┼──────────────┼─────────────┘
                             │              │
                             ▼              ▼
                    ┌─────────────────────────────────┐
                    │         Load Balancer           │
                    └─────────────────┬───────────────┘
                                      │
                    ┌─────────────────┴───────────────┐
                    │                                 │
                    ▼                                 ▼
           ┌───────────────┐                ┌───────────────┐
           │   OhGrt API   │                │  WhatsApp Bot │
           │   (FastAPI)   │                │   (FastAPI)   │
           └───────┬───────┘                └───────┬───────┘
                   │                                │
                   └────────────────┬───────────────┘
                                    │
                                    ▼
                    ┌─────────────────────────────────┐
                    │         Common Module           │
                    │  (Intent Detection, Tools,      │
                    │   Services, Astrology Engine)   │
                    └─────────────────┬───────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
              ▼                       ▼                       ▼
     ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
     │  PostgreSQL │         │    Redis    │         │  External   │
     │  (Primary)  │         │   (Cache)   │         │    APIs     │
     └─────────────┘         └─────────────┘         └─────────────┘
```

---

## 📈 Recommended Architecture (Future)

```
                              ┌─────────────────┐
                              │   API Gateway   │
                              │   (Kong/Envoy)  │
                              └────────┬────────┘
                                       │
         ┌─────────────────────────────┼─────────────────────────────┐
         │                             │                             │
         ▼                             ▼                             ▼
┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐
│  Auth Service   │          │   Chat Service  │          │  Intent Service │
│  (Firebase +    │          │   (FastAPI)     │          │  (LangGraph)    │
│   JWT)          │          └────────┬────────┘          └────────┬────────┘
└─────────────────┘                   │                            │
                                      │                            │
                              ┌───────┴────────┐                   │
                              │                │                   │
                              ▼                ▼                   ▼
                    ┌─────────────┐   ┌─────────────┐   ┌─────────────────┐
                    │  Astrology  │   │   Travel    │   │   Government    │
                    │   Service   │   │   Service   │   │    Service      │
                    └─────────────┘   └─────────────┘   └─────────────────┘
                              │                │                   │
                              └────────────────┼───────────────────┘
                                               │
                              ┌────────────────┴────────────────┐
                              │         Message Queue           │
                              │      (RabbitMQ / Kafka)         │
                              └────────────────┬────────────────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    │                          │                          │
                    ▼                          ▼                          ▼
           ┌─────────────┐            ┌─────────────┐            ┌─────────────┐
           │  PostgreSQL │            │    Redis    │            │   S3/MinIO  │
           │  (Primary)  │            │  (Cache +   │            │   (Files)   │
           │             │            │   Pub/Sub)  │            │             │
           └─────────────┘            └─────────────┘            └─────────────┘
```

---

## 🎯 Priority Action Items

| Priority | Item | Effort | Impact |
|----------|------|--------|--------|
| **P0** | Consolidate intent detection files | 2 days | High |
| **P0** | Add structured logging | 1 day | High |
| **P1** | Implement caching for external APIs | 3 days | High |
| **P1** | Add circuit breakers | 2 days | Medium |
| **P2** | Break up large intent file | 3 days | Medium |
| **P2** | Add request tracing | 2 days | Medium |
| **P3** | Move URLs to config | 1 day | Low |
| **P3** | Add rate limiting to webhook | 1 day | Medium |

---

## 🏆 Overall Assessment

| Category | Score | Notes |
|----------|-------|-------|
| **Code Quality** | 8/10 | Well-structured, needs minor cleanup |
| **Architecture** | 9/10 | Excellent use of LangGraph, clean separation |
| **Scalability** | 7/10 | Good foundation, needs caching & queues |
| **Security** | 8/10 | Auth solid, add rate limiting |
| **Maintainability** | 7/10 | Good, but consolidate duplicate code |
| **Documentation** | 6/10 | Inline docs good, needs API docs |
| **Testing** | 5/10 | Needs more coverage |

**Overall: 7.5/10** - Production-ready with room for optimization

---

## Conclusion

The OhGrt platform demonstrates **solid engineering fundamentals** with a well-thought-out architecture. The use of LangGraph for orchestration, Pydantic for type safety, and async-first design shows mature engineering decisions.

The main areas for improvement are:
1. Consolidating duplicate code
2. Adding caching and circuit breakers
3. Improving observability (logging, tracing)
4. Expanding test coverage

With these improvements, the platform is well-positioned for scale.

---

*Review conducted: February 2026*
