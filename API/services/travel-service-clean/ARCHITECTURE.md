# Clean Architecture - Travel Service

## Overview

This service follows **Clean Architecture** (also known as Hexagonal/Onion Architecture) to achieve:

- **Testability**: Business logic tested without HTTP, database, or external APIs
- **Scalability**: Easy to add new features without breaking existing code
- **Maintainability**: Clear boundaries between layers
- **Flexibility**: Swap implementations (e.g., change database) without changing business logic

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              INFRASTRUCTURE                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         FastAPI Routers                              │   │
│  │                    (HTTP Request/Response)                           │   │
│  └───────────────────────────┬─────────────────────────────────────────┘   │
│                              │ calls                                        │
│  ┌───────────────────────────▼─────────────────────────────────────────┐   │
│  │                              APPLICATION                             │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │                         Use Cases                            │   │   │
│  │  │  - GetPNRStatusUseCase                                       │   │   │
│  │  │  - GetTrainScheduleUseCase                                   │   │   │
│  │  │  - SearchTrainsUseCase                                       │   │   │
│  │  └─────────────────────────┬───────────────────────────────────┘   │   │
│  │                            │ uses                                   │   │
│  │  ┌─────────────────────────▼───────────────────────────────────┐   │   │
│  │  │                          DOMAIN                              │   │   │
│  │  │  ┌─────────────────┐  ┌────────────────────────────────┐   │   │   │
│  │  │  │    Entities     │  │    Repository Interfaces       │   │   │   │
│  │  │  │  - PNR          │  │  - PNRRepository (abstract)    │   │   │   │
│  │  │  │  - Train        │  │  - TrainRepository (abstract)  │   │   │   │
│  │  │  │  - Passenger    │  │                                │   │   │   │
│  │  │  └─────────────────┘  └────────────────────────────────┘   │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              ▲ implements                                   │
│  ┌───────────────────────────┴─────────────────────────────────────────┐   │
│  │                    Repository Implementations                        │   │
│  │  - MockPNRRepository (for testing)                                   │   │
│  │  - PNRRepositoryImpl (calls Railway API)                            │   │
│  │  - MockTrainRepository (for testing)                                 │   │
│  │  - TrainRepositoryImpl (calls Railway API)                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
travel-service-clean/
├── domain/                          # Core business logic (NO dependencies)
│   ├── entities/
│   │   ├── __init__.py
│   │   ├── pnr.py                  # PNR, Passenger, BookingStatus
│   │   └── train.py                # Train, Station, TrainSchedule
│   └── repositories/
│       ├── __init__.py
│       ├── pnr_repository.py       # Abstract interface
│       └── train_repository.py     # Abstract interface
│
├── application/                     # Application business rules
│   ├── dto/
│   │   ├── __init__.py
│   │   ├── pnr_dto.py              # API response models
│   │   └── train_dto.py
│   └── use_cases/
│       ├── __init__.py
│       ├── get_pnr_status.py       # Single responsibility
│       ├── get_train_schedule.py
│       ├── search_trains.py
│       └── get_live_status.py
│
├── infrastructure/                  # External concerns
│   ├── api/
│   │   ├── routers/
│   │   │   ├── pnr_router.py       # HTTP endpoints
│   │   │   └── train_router.py
│   │   ├── dependencies.py         # Dependency injection
│   │   └── config.py               # Settings
│   └── repositories/
│       ├── mock_pnr_repository.py  # For testing
│       ├── mock_train_repository.py
│       ├── pnr_repository_impl.py  # Production (API calls)
│       └── train_repository_impl.py
│
├── tests/
│   └── unit/
│       ├── test_pnr_use_case.py
│       └── test_train_use_case.py
│
├── main.py                          # Composition root
└── requirements.txt
```

## Key Principles

### 1. Dependency Rule

Dependencies point INWARD:
- Infrastructure depends on Application
- Application depends on Domain
- Domain depends on NOTHING

```python
# GOOD: Infrastructure imports from Application
from application.use_cases import GetPNRStatusUseCase

# BAD: Domain imports from Infrastructure
from infrastructure.api.routers import router  # NEVER do this
```

### 2. Dependency Inversion

Domain defines interfaces, Infrastructure implements them:

```python
# domain/repositories/pnr_repository.py (INTERFACE)
class PNRRepository(ABC):
    @abstractmethod
    async def get_by_pnr(self, pnr_number: str) -> Optional[PNR]:
        pass

# infrastructure/repositories/pnr_repository_impl.py (IMPLEMENTATION)
class PNRRepositoryImpl(PNRRepository):
    async def get_by_pnr(self, pnr_number: str) -> Optional[PNR]:
        # Actual API call here
        response = await self.client.get(f"/pnr/{pnr_number}")
        return self._to_entity(response.json())
```

### 3. Use Cases are Single Responsibility

Each use case does ONE thing:

```python
@dataclass
class GetPNRStatusUseCase:
    pnr_repository: PNRRepository

    async def execute(self, pnr_number: str) -> PNRResponse:
        # 1. Validate
        self._validate_pnr(pnr_number)
        # 2. Get data
        pnr = await self.pnr_repository.get_by_pnr(pnr_number)
        # 3. Transform
        return self._to_response(pnr)
```

### 4. Entities Have Business Logic

Entities are not just data containers:

```python
@dataclass
class PNR:
    passengers: List[Passenger]

    @property
    def all_confirmed(self) -> bool:
        """Business logic lives in entities."""
        return all(p.is_confirmed for p in self.passengers)

    def validate(self) -> List[str]:
        """Entities can validate themselves."""
        errors = []
        if len(self.pnr_number) != 10:
            errors.append("PNR must be 10 digits")
        return errors
```

## Testing

### Unit Tests (Fast, Isolated)

```python
@pytest.fixture
def use_case():
    # Inject mock repository
    return GetPNRStatusUseCase(
        pnr_repository=MockPNRRepository()
    )

@pytest.mark.asyncio
async def test_get_pnr_success(use_case):
    result = await use_case.execute("1234567890")
    assert result.success is True
```

### Integration Tests (With Real Dependencies)

```python
@pytest.fixture
def use_case():
    # Inject real repository
    return GetPNRStatusUseCase(
        pnr_repository=PNRRepositoryImpl(api_url="...", api_key="...")
    )
```

## Dependency Injection

Using FastAPI's Depends:

```python
# infrastructure/api/dependencies.py
def get_pnr_repository() -> PNRRepository:
    if settings.USE_MOCK_DATA:
        return MockPNRRepository()
    return PNRRepositoryImpl(...)

def get_pnr_use_case() -> GetPNRStatusUseCase:
    return GetPNRStatusUseCase(
        pnr_repository=get_pnr_repository()
    )

# infrastructure/api/routers/pnr_router.py
@router.get("/{pnr_number}")
async def get_pnr_status(
    pnr_number: str,
    use_case: Annotated[GetPNRStatusUseCase, Depends(get_pnr_use_case)]
):
    return await use_case.execute(pnr_number)
```

## Benefits

| Aspect | Simple Architecture | Clean Architecture |
|--------|--------------------|--------------------|
| Test business logic | Need to mock HTTP | Just inject mock repository |
| Change database | Rewrite services | Just swap repository |
| Add caching | Modify service code | Add CachingRepository decorator |
| Understand code | Follow call chain | Clear layer boundaries |
| Onboard new devs | Learn entire codebase | Learn one layer at a time |

## How to Scale

1. **Add new use cases**: Create new file in `application/use_cases/`
2. **Add new entity**: Create in `domain/entities/`
3. **Add new data source**: Implement repository interface in `infrastructure/repositories/`
4. **Add caching**: Create `CachingPNRRepository` that wraps another repository
5. **Add different API**: Create `OtherAPIPNRRepository` implementing same interface

## Running

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run service
python main.py
# or
uvicorn main:app --port 8004 --reload
```
