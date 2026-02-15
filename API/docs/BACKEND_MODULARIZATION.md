# Backend Modularization Plan

## Current State Analysis

### Directory Structure (As-Is)
```
unified_platform/           (~105K lines Python)
├── common/                 (4.4 MB) - Shared code
│   ├── graph/             (1.2 MB) - Intent detection, nodes
│   ├── tools/             (828 KB) - 24+ tool implementations
│   ├── i18n/              (636 KB) - Translations (22 languages)
│   ├── astro/             (612 KB) - Vedic astrology engine
│   ├── services/          (352 KB) - Shared services
│   ├── data/              (200 KB) - Seed data
│   ├── utils/             (140 KB) - Utilities
│   ├── whatsapp/          (108 KB) - WhatsApp client
│   ├── config/            (96 KB)  - Configuration
│   ├── stores/            (52 KB)  - State stores
│   └── ...
├── whatsapp_bot/           (2.4 MB) - WhatsApp integration
│   ├── graph/nodes/       - 25+ handler nodes
│   └── ...
└── ohgrt_api/              (2.4 MB) - REST API
    ├── services/          - API services
    ├── graph/             - API-specific graphs
    └── ...
```

### Problems Identified

#### 1. **Monolithic Intent Detection** (3,093 lines)
`whatsapp_bot/graph/nodes/intent_v2.py` handles ALL intents:
- 40+ intent types
- Keywords for 22 languages
- Entity extraction
- Domain classification

**Impact**: Hard to maintain, slow to load, merge conflicts

#### 2. **Duplicate Code**
| File | Locations | Lines |
|------|-----------|-------|
| `seed_data.py` | `common/data/`, `whatsapp_bot/data/` | 2,451 each |
| `user_store.py` | `common/stores/`, `whatsapp_bot/stores/` | 592 each |
| `intent.py` | `common/graph/nodes/`, `whatsapp_bot/graph/nodes/` | 1,702 + 3,093 |
| `train_journey.py` | `common/graph/nodes/`, `whatsapp_bot/graph/nodes/` | 637 + 1,052 |

#### 3. **Mixed Domain Logic**
Tools and nodes mix multiple domains:
- `astro_tool.py` (1,101 lines) - Astrology
- `railway_api.py` (666 lines) - Travel
- `serper_search.py` (832 lines) - Search

#### 4. **Tight Coupling**
WhatsApp bot directly imports from common:
```python
from common.graph.state import BotState
from common.tools.serper_search import search_google
from common.i18n.detector import detect_language
```

---

## Proposed Modular Architecture

### Target Structure (To-Be)
```
unified_platform/
├── packages/                          # Independent packages
│   ├── core/                          # Core abstractions
│   │   ├── types/                     # Shared types (BotState, ToolResult)
│   │   ├── config/                    # Base configuration
│   │   ├── utils/                     # Common utilities
│   │   └── errors/                    # Custom exceptions
│   │
│   ├── intents/                       # Intent detection module
│   │   ├── classifier/                # Main classifier
│   │   ├── keywords/                  # Keyword lists by domain
│   │   │   ├── astrology.py
│   │   │   ├── travel.py
│   │   │   ├── government.py
│   │   │   ├── utilities.py
│   │   │   └── hindi.py
│   │   ├── extractors/                # Entity extractors
│   │   │   ├── date_extractor.py
│   │   │   ├── location_extractor.py
│   │   │   └── pnr_extractor.py
│   │   └── llm/                       # LLM-based classification
│   │
│   ├── i18n/                          # Internationalization
│   │   ├── detector.py                # Language detection
│   │   ├── translator.py              # Translation service
│   │   └── templates/                 # Response templates by language
│   │       ├── en.py
│   │       ├── hi.py
│   │       └── ...
│   │
│   ├── astrology/                     # Astrology domain module
│   │   ├── engine/                    # Chart calculations
│   │   │   ├── swiss_ephemeris.py
│   │   │   ├── chart_calculator.py
│   │   │   └── aspect_calculator.py
│   │   ├── services/                  # Business logic
│   │   │   ├── horoscope_service.py
│   │   │   ├── kundli_service.py
│   │   │   ├── dosha_service.py
│   │   │   └── prediction_service.py
│   │   ├── knowledge/                 # Interpretation rules
│   │   │   ├── planets.py
│   │   │   ├── houses.py
│   │   │   └── nakshatras.py
│   │   └── handlers/                  # Graph node handlers
│   │       ├── horoscope_handler.py
│   │       ├── kundli_handler.py
│   │       └── dosha_handler.py
│   │
│   ├── travel/                        # Travel domain module
│   │   ├── providers/                 # External API clients
│   │   │   ├── railway_api.py
│   │   │   ├── metro_api.py
│   │   │   └── bus_api.py
│   │   ├── services/                  # Business logic
│   │   │   ├── pnr_service.py
│   │   │   ├── train_status_service.py
│   │   │   └── journey_planner.py
│   │   └── handlers/                  # Graph node handlers
│   │       ├── pnr_handler.py
│   │       ├── train_status_handler.py
│   │       └── journey_handler.py
│   │
│   ├── government/                    # Government services module
│   │   ├── providers/                 # Portal integrations
│   │   │   ├── pmkisan.py
│   │   │   ├── parivahan.py
│   │   │   ├── crsorgi.py
│   │   │   └── bseb.py
│   │   ├── services/                  # Business logic
│   │   │   ├── scheme_service.py
│   │   │   ├── job_service.py
│   │   │   └── certificate_service.py
│   │   └── handlers/                  # Graph node handlers
│   │
│   ├── utilities/                     # Utility services module
│   │   ├── weather/
│   │   │   ├── provider.py            # OpenWeather API
│   │   │   ├── service.py
│   │   │   └── handler.py
│   │   ├── news/
│   │   │   ├── provider.py
│   │   │   ├── service.py
│   │   │   └── handler.py
│   │   ├── stocks/
│   │   ├── cricket/
│   │   └── search/                    # Tavily, Serper
│   │
│   ├── ai/                            # AI capabilities module
│   │   ├── llm/                       # LLM clients
│   │   │   ├── openai_client.py
│   │   │   └── ollama_client.py
│   │   ├── vision/                    # Image analysis
│   │   ├── image_gen/                 # Image generation (FAL)
│   │   ├── rag/                       # PDF/document Q&A
│   │   └── tts_stt/                   # Voice services
│   │
│   └── messaging/                     # Messaging module
│       ├── whatsapp/
│       │   ├── client.py
│       │   ├── webhook.py
│       │   └── models.py
│       └── email/
│           ├── gmail_service.py
│           └── scheduler.py
│
├── apps/                              # Application layer
│   ├── whatsapp_bot/                  # WhatsApp application
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── graph.py                   # LangGraph workflow
│   │   └── webhook/
│   │
│   └── api/                           # REST API application
│       ├── main.py
│       ├── config.py
│       ├── routers/
│       │   ├── auth.py
│       │   ├── chat.py
│       │   ├── admin.py
│       │   └── ...
│       ├── services/
│       └── db/
│
├── shared/                            # Truly shared code
│   ├── database/                      # DB models & migrations
│   │   ├── models.py
│   │   ├── base.py
│   │   └── migrations/
│   └── stores/                        # State stores
│       ├── redis_store.py
│       └── memory_store.py
│
└── pyproject.toml                     # Workspace definition
```

---

## Module Breakdown

### 1. `packages/core` - Foundation Layer
**Purpose**: Shared abstractions used by all modules

```python
# packages/core/types/state.py
from typing import TypedDict, Optional, Dict, Any

class BotState(TypedDict, total=False):
    """Standard state for all graph workflows."""
    whatsapp_message: Dict[str, Any]
    intent: str
    intent_confidence: float
    extracted_entities: Dict[str, Any]
    response_text: str
    response_type: str
    detected_language: str
    error: Optional[str]

# packages/core/types/result.py
@dataclass
class ToolResult:
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None
    tool_name: str = ""
```

**Dependencies**: None (leaf package)

---

### 2. `packages/intents` - Intent Detection
**Purpose**: Centralized intent classification

**Before** (3,093 lines in one file):
```python
# whatsapp_bot/graph/nodes/intent_v2.py
pmkisan_keywords = [...]  # 50 lines
dl_status_keywords = [...]  # 40 lines
certificate_keywords = [...]  # 30 lines
# ... 40+ more keyword lists
```

**After** (modular):
```python
# packages/intents/keywords/government.py
PMKISAN_KEYWORDS = {
    "en": ["pm kisan", "kisan samman", ...],
    "hi": ["पीएम किसान", "किसान सम्मान", ...],
}

DL_STATUS_KEYWORDS = {
    "en": ["driving license", "dl status", ...],
    "hi": ["ड्राइविंग लाइसेंस", ...],
}

# packages/intents/classifier/main.py
from packages.intents.keywords import astrology, travel, government, utilities

class IntentClassifier:
    def __init__(self):
        self.keyword_matchers = [
            KeywordMatcher(government.PMKISAN_KEYWORDS, "pmkisan_status"),
            KeywordMatcher(government.DL_STATUS_KEYWORDS, "dl_status"),
            KeywordMatcher(astrology.HOROSCOPE_KEYWORDS, "get_horoscope"),
            # ...
        ]

    async def classify(self, message: str, lang: str) -> IntentResult:
        # Try keyword matching first
        for matcher in self.keyword_matchers:
            if matcher.matches(message, lang):
                return IntentResult(intent=matcher.intent, confidence=0.95)

        # Fall back to LLM
        return await self.llm_classify(message)
```

**Benefits**:
- Each domain owns its keywords
- Easy to add new intents
- Testable in isolation
- ~300 lines per file instead of 3,000

---

### 3. `packages/astrology` - Astrology Domain
**Purpose**: Complete astrology feature set

```
packages/astrology/
├── __init__.py
├── engine/
│   ├── __init__.py
│   ├── chart_calculator.py      # Swiss Ephemeris integration
│   ├── aspect_calculator.py     # Planetary aspects
│   └── position_calculator.py   # Planet positions
├── services/
│   ├── __init__.py
│   ├── horoscope_service.py     # Daily/weekly horoscopes
│   ├── kundli_service.py        # Birth chart generation
│   ├── dosha_service.py         # Manglik, Kaal Sarp, etc.
│   ├── matching_service.py      # Kundli matching
│   └── prediction_service.py    # Life predictions
├── knowledge/
│   ├── __init__.py
│   ├── planets.py               # Planet interpretations
│   ├── houses.py                # House meanings
│   ├── nakshatras.py            # Nakshatra data
│   └── yogas.py                 # Yoga definitions
├── handlers/
│   ├── __init__.py
│   ├── horoscope_handler.py     # Graph node for horoscope
│   ├── kundli_handler.py        # Graph node for kundli
│   └── dosha_handler.py         # Graph node for dosha
└── schemas/
    ├── __init__.py
    ├── birth_details.py
    ├── chart.py
    └── prediction.py
```

**Public API**:
```python
# packages/astrology/__init__.py
from .services.horoscope_service import HoroscopeService
from .services.kundli_service import KundliService
from .handlers import (
    handle_horoscope,
    handle_kundli,
    handle_dosha,
)

__all__ = [
    "HoroscopeService",
    "KundliService",
    "handle_horoscope",
    "handle_kundli",
    "handle_dosha",
]
```

---

### 4. `packages/travel` - Travel Domain
**Purpose**: All travel-related features

```
packages/travel/
├── __init__.py
├── providers/
│   ├── __init__.py
│   ├── railway_api.py           # RapidAPI Indian Railways
│   ├── metro_api.py             # DMRC, BMRC APIs
│   └── train_scraper.py         # Fallback scraper
├── services/
│   ├── __init__.py
│   ├── pnr_service.py
│   ├── train_status_service.py
│   └── journey_planner.py
├── handlers/
│   ├── __init__.py
│   ├── pnr_handler.py
│   ├── train_status_handler.py
│   └── journey_handler.py
└── models/
    ├── __init__.py
    ├── pnr.py
    └── train.py
```

---

### 5. `packages/government` - Government Services
**Purpose**: All government service integrations

```
packages/government/
├── __init__.py
├── providers/
│   ├── __init__.py
│   ├── pmkisan.py               # PM-KISAN portal
│   ├── parivahan.py             # DL/RC status
│   ├── crsorgi.py               # Birth/death certificates
│   ├── bseb.py                  # Bihar Board results
│   └── echallan.py              # Traffic challans
├── services/
│   ├── __init__.py
│   ├── scheme_service.py        # Government schemes
│   ├── job_service.py           # Sarkari naukri
│   └── certificate_service.py
├── handlers/
│   └── ...
└── data/
    ├── bihar_districts.py
    ├── rto_codes.py
    └── scheme_info.py
```

---

### 6. `packages/utilities` - Utility Services
**Purpose**: Weather, news, stocks, cricket, search

```
packages/utilities/
├── weather/
│   ├── provider.py              # OpenWeather API
│   ├── service.py               # Business logic
│   └── handler.py               # Graph node
├── news/
│   ├── provider.py              # News API
│   ├── service.py
│   └── handler.py
├── stocks/
│   ├── provider.py              # Stock API
│   ├── service.py
│   └── handler.py
├── cricket/
│   └── ...
└── search/
    ├── tavily.py
    ├── serper.py
    └── service.py
```

---

### 7. `apps/whatsapp_bot` - WhatsApp Application
**Purpose**: WhatsApp-specific orchestration

```python
# apps/whatsapp_bot/graph.py
from langgraph.graph import StateGraph, START, END
from packages.core.types import BotState
from packages.intents import IntentClassifier
from packages.astrology.handlers import handle_horoscope, handle_kundli
from packages.travel.handlers import handle_pnr, handle_train_status
from packages.government.handlers import handle_pmkisan, handle_dl_status
from packages.utilities.weather import handle_weather

def create_graph() -> StateGraph:
    graph = StateGraph(BotState)

    # Add nodes from packages
    graph.add_node("intent", IntentClassifier().classify)
    graph.add_node("horoscope", handle_horoscope)
    graph.add_node("pnr", handle_pnr)
    graph.add_node("weather", handle_weather)
    graph.add_node("pmkisan", handle_pmkisan)
    # ...

    return graph
```

**Benefits**:
- WhatsApp bot is thin orchestration layer
- All business logic in packages
- Easy to add/remove features
- Clear dependency graph

---

## Migration Strategy

### Phase 1: Extract Core (Week 1)
1. Create `packages/core/` with types and utilities
2. Update imports across codebase
3. Run tests to verify no breakage

### Phase 2: Extract Intents (Week 2)
1. Create `packages/intents/` structure
2. Move keyword lists to domain files
3. Create `IntentClassifier` class
4. Update WhatsApp bot to use new classifier
5. Delete old `intent_v2.py`

### Phase 3: Extract Domains (Weeks 3-5)
1. **Week 3**: Extract `packages/astrology/`
2. **Week 4**: Extract `packages/travel/` and `packages/government/`
3. **Week 5**: Extract `packages/utilities/` and `packages/ai/`

### Phase 4: Restructure Apps (Week 6)
1. Move `whatsapp_bot/` to `apps/whatsapp_bot/`
2. Move `ohgrt_api/` to `apps/api/`
3. Update imports and configs
4. Final integration testing

---

## Dependency Graph (After Modularization)

```
┌─────────────────────────────────────────────────────────────────┐
│                         APPLICATIONS                             │
│  ┌─────────────────┐                    ┌─────────────────┐     │
│  │  WhatsApp Bot   │                    │    REST API     │     │
│  └────────┬────────┘                    └────────┬────────┘     │
└───────────┼──────────────────────────────────────┼──────────────┘
            │                                      │
            ▼                                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DOMAIN PACKAGES                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │ Astrology│ │  Travel  │ │Government│ │Utilities │            │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘            │
└───────┼────────────┼────────────┼────────────┼──────────────────┘
        │            │            │            │
        ▼            ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FOUNDATION PACKAGES                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │  Intents │ │   i18n   │ │    AI    │ │ Messaging│            │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘            │
└───────┼────────────┼────────────┼────────────┼──────────────────┘
        │            │            │            │
        └────────────┴────────────┴────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         CORE PACKAGE                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │  Types   │ │  Config  │ │  Utils   │ │  Errors  │            │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Package Management Options

### Option 1: Monorepo with Workspaces (Recommended)
```toml
# pyproject.toml
[tool.poetry]
name = "ohgrt-platform"
packages = [
    { include = "packages/core", from = "." },
    { include = "packages/intents", from = "." },
    { include = "packages/astrology", from = "." },
    { include = "packages/travel", from = "." },
    { include = "packages/government", from = "." },
    { include = "packages/utilities", from = "." },
    { include = "apps/whatsapp_bot", from = "." },
    { include = "apps/api", from = "." },
]
```

### Option 2: Separate Packages (pip installable)
```
ohgrt-core           # pip install ohgrt-core
ohgrt-intents        # pip install ohgrt-intents
ohgrt-astrology      # pip install ohgrt-astrology
ohgrt-travel         # pip install ohgrt-travel
ohgrt-government     # pip install ohgrt-government
ohgrt-utilities      # pip install ohgrt-utilities
ohgrt-whatsapp       # pip install ohgrt-whatsapp
ohgrt-api            # pip install ohgrt-api
```

### Option 3: Hybrid (Internal packages, external apps)
- Packages stay in monorepo (fast iteration)
- Apps can be deployed independently
- Packages published to private PyPI when stable

---

## Benefits Summary

| Metric | Before | After |
|--------|--------|-------|
| **Largest file** | 3,093 lines | ~300 lines |
| **Duplicate code** | ~10,000 lines | 0 lines |
| **Test isolation** | Difficult | Easy (per-package) |
| **Deployment** | Monolith | Independent apps |
| **Onboarding** | Overwhelming | Domain-focused |
| **CI/CD time** | Full rebuild | Affected packages only |

---

## Quick Wins (Start Today)

### 1. Extract Intent Keywords (2 hours)
```bash
# Create keyword files
mkdir -p packages/intents/keywords
# Move keyword lists from intent_v2.py to separate files
```

### 2. Delete Duplicate Files (30 mins)
```bash
# Remove duplicates, use symlinks or imports
rm whatsapp_bot/data/seed_data.py  # Use common/data/
rm -rf whatsapp_bot/stores/        # Use common/stores/
```

### 3. Create Core Types (1 hour)
```bash
mkdir -p packages/core/types
# Extract BotState, ToolResult to shared location
```

---

## Conclusion

The backend is well-architected but has grown organically. Modularization will:

1. **Improve maintainability** - Smaller, focused files
2. **Enable parallel development** - Teams own domains
3. **Reduce merge conflicts** - Isolated changes
4. **Speed up CI/CD** - Test only affected packages
5. **Support future scaling** - Deploy domains independently

**Recommended approach**: Start with Phase 1 (Core extraction) and Phase 2 (Intents), which provide the highest ROI with lowest risk.
