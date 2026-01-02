# ModelShelf Architecture

## Overview

ModelShelf uses a layered architecture separating concerns between UI, business logic, data access, and external integrations.

## Architecture Diagram

```
┌───────────────────────────────┐
│     QML UI Layer (ui/)       │
│  Discover, Downloads, Shelf   │
└───────────┬───────────────────┘
             │
             │ Signals/Slots
             v
┌───────────────────────────────┐
│   Python Bridge (ui/bridge)   │
│  SearchBridge, DownloadBridge │
└───────────┬───────────────────┘
             │
             │ Async calls
             v
┌───────────────────────────────┐
│  Service Layer (app/services) │
│ SearchService, DownloadService│
└────────┬────────────┬──────────┘
         │               │
         v               v
┌──────────┐  ┌──────────────┐
│  Storage  │  │   Sources    │
│  Cache +  │  │ HubAdapter  │
│ Database │  │ (HF, etc.)  │
└──────────┘  └──────────────┘
```

## Layer Descriptions

### 1. UI Layer (`ui/`)
**Technology**: QML (Qt Quick)

**Responsibilities**:
- Declarative UI components
- User interaction handling
- Visual presentation
- Navigation between views

**Key Files**:
- `qml/main.qml` - Application shell
- `qml/Discover.qml` - Model browsing
- `qml/ModelDetailsPanel.qml` - Model info display
- `qml/ModelListItem.qml` - List item component

**Design Principles**:
- Keep QML logic minimal
- Delegate business logic to Python
- Use signals for async updates
- Maintain responsive UI

---

### 2. Bridge Layer (`ui/bridge.py`)
**Technology**: PySide6 with `@QmlElement` decorator

**Responsibilities**:
- Python-QML communication
- Thread management for async operations
- Signal/slot connections
- Data format conversion (Python ↔ QML)

**Key Classes**:
- `SearchBridge` - Search operations
- `SearchThread` - Background search
- `ModelDetailsThread` - Background details loading

**Pattern**:
```python
@QmlElement
class SearchBridge(QObject):
    # Signals for QML
    searchCompleted = Signal(list, int, bool)
    
    @Slot(str, bool, str, int, int)
    def search(self, query, has_gguf, sort_by, page, page_size):
        # Spawn background thread
        thread = SearchThread(...)
        thread.finished.connect(self._on_finished)
        thread.start()
```

---

### 3. Service Layer (`app/services.py`)
**Technology**: Python with asyncio

**Responsibilities**:
- Coordinate between data sources
- Implement business rules
- Cache management
- Error handling and retry logic

**Key Classes**:
- `SearchService` - Model search coordination
- `ServiceManager` - Global service access

**Pattern**:
```python
class SearchService:
    async def search(self, filter: SearchFilter) -> SearchResult:
        # Try cache first
        if cached := self.cache.get(...):
            return cached
        
        # Fetch from hub
        result = await self.hub.search_models(...)
        
        # Cache result
        self.cache.cache_search_result(...)
        
        return result
```

---

### 4. Domain Layer (`domain/`)
**Technology**: Pure Python (dataclasses, enums)

**Responsibilities**:
- Core business entities
- Domain logic
- Value objects
- Utility functions

**Key Files**:
- `models.py` - Domain entities (SearchFilter, DownloadState)

**Design**: 
- No external dependencies
- Immutable where possible
- Rich domain models

---

### 5. Storage Layer (`storage/`)
**Technology**: SQLAlchemy + SQLite

**Responsibilities**:
- Data persistence
- Cache management
- Settings storage
- Query optimization

**Key Files**:
- `database.py` - SQLAlchemy models and manager
- `cache.py` - High-level cache operations
- `settings.py` - Application settings

**Tables**:
- `cached_models` - Model metadata
- `cached_files` - File information
- `search_cache` - Search result cache
- `download_history` - Download tracking

---

### 6. Sources Layer (`sources/`)
**Technology**: Python + Hub SDKs

**Responsibilities**:
- External API integration
- Data fetching
- Response parsing
- Rate limiting (future)

**Key Files**:
- `hub_adapter.py` - Abstract interface
- `huggingface_adapter.py` - HF implementation

**Design Pattern**: Adapter
```python
class HubAdapter(ABC):
    @abstractmethod
    async def search_models(...) -> SearchResult:
        pass

class HuggingFaceAdapter(HubAdapter):
    async def search_models(...) -> SearchResult:
        # HF-specific implementation
```

---

## Data Flow

### Search Flow

```
1. User types query in QML
   ↓
2. QML calls SearchBridge.search()
   ↓
3. SearchBridge creates SearchThread
   ↓
4. SearchThread calls SearchService.search()
   ↓
5. SearchService checks cache
   │
   ├─ Cache hit → return cached
   │
   └─ Cache miss:
      ↓
      6. Call HuggingFaceAdapter.search_models()
      ↓
      7. Parse API response
      ↓
      8. Cache result
      ↓
      9. Return SearchResult
   ↓
10. SearchThread emits finished signal
   ↓
11. SearchBridge converts to QML format
   ↓
12. SearchBridge emits searchCompleted
   ↓
13. QML updates UI
```

---

## Key Design Decisions

### 1. Why QML?
- Declarative UI is easier to maintain
- Excellent performance for dynamic lists
- Native look and feel
- Hot reload during development

### 2. Why SQLite?
- Embedded (no server setup)
- Fast for read-heavy workloads
- ACID transactions
- Cross-platform

### 3. Why Async?
- Non-blocking network I/O
- Responsive UI
- Parallel operations
- Better resource utilization

### 4. Why Adapter Pattern for Hubs?
- Easy to add new sources (GitHub, etc.)
- Testable (mock adapters)
- Separation of concerns
- Future-proof

### 5. Why Cache?
- Reduce API calls (avoid rate limits)
- Faster user experience
- Offline capability (partial)
- Lower bandwidth usage

---

## Concurrency Model

### UI Thread
- Handles all QML rendering
- Processes user events
- Updates visual elements

**Rule**: Never block UI thread

### Background Threads (QThread)
- Search operations
- Model details loading
- File downloads (M2)
- Database operations

**Communication**: Signals/Slots

### Async Event Loop
- HTTP requests
- API calls
- I/O operations

**Pattern**: `asyncio.run()` in background threads

---

## Error Handling Strategy

### Layers
1. **Hub Adapter**: Catches HTTP/API errors
2. **Service**: Logs errors, returns safe defaults
3. **Bridge**: Emits error signals to QML
4. **UI**: Shows user-friendly messages

### Example
```python
try:
    result = await api_call()
except httpx.HTTPError as e:
    logger.error(f"API error: {e}")
    return empty_result()
except Exception as e:
    logger.error(f"Unexpected: {e}", exc_info=True)
    return empty_result()
```

---

## Testing Strategy

### Unit Tests (Future)
- Domain logic
- Utility functions
- Cache operations

### Integration Tests (Future)
- Service layer
- Database operations
- API adapters (with mocks)

### Manual Tests (Current)
- UI workflows
- User interactions
- Performance checks

See [M1_TESTING.md](M1_TESTING.md)

---

## Performance Considerations

### Optimizations
1. **Lazy loading**: Load details only when needed
2. **Pagination**: Limit results per page
3. **Caching**: Aggressive caching strategy
4. **Thread pooling**: Reuse threads where possible
5. **Database indexes**: Speed up queries

### Bottlenecks to Watch
- Network latency (cache helps)
- Large file lists (pagination needed)
- UI list rendering (QML handles well)
- Database growth (periodic cleanup)

---

## Security Considerations

### Current (M1)
- No password storage
- Optional HF token (not implemented yet)
- HTTPS for all API calls
- No code execution from downloads

### Future (M4+)
- Secure token storage (keyring)
- File verification (SHA256)
- Download source validation
- Sandboxed operations

---

## Extensibility Points

### Adding a New Hub Source
1. Implement `HubAdapter` interface
2. Register in `ServiceManager`
3. Add UI selector (M4)

### Adding a New View
1. Create QML file in `ui/qml/`
2. Add bridge class in `ui/bridge.py`
3. Update `main.qml` navigation

### Adding a New Feature
1. Define domain models
2. Implement service layer
3. Create bridge
4. Build UI

---

## Future Architecture Changes

### Planned (M2-M6)
- Download manager with queue
- Plugin system for runners
- Multiple hub sources
- Settings UI with validation

### Under Consideration
- Local model analysis (size, format detection)
- Model conversion tools
- Community features (ratings, comments)
- Offline mode

---

For more details, see:
- [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md)
- [DEVELOPMENT.md](../DEVELOPMENT.md)
