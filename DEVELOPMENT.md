# ModelShelf Development Status

## Current Milestone: M1 ⏳ IN PROGRESS

### M0: Repo + skeleton (1–2 days)
**Status**: ✅ Complete

#### Completed:
- [x] Project structure created
- [x] Module directories established
- [x] Basic QML shell with sidebar navigation
- [x] Settings persistence (JSON-based)
- [x] Logging configured
- [x] Error handling framework
- [x] Configuration management
- [x] Development documentation

---

### M1: Hub browsing (3–7 days)
**Status**: ⏳ In Progress

#### Completed:
- [x] Hub adapter interface defined
- [x] Hugging Face API integration
  - [x] Model search with pagination
  - [x] GGUF detection and prioritisation
  - [x] Quantisation pattern recognition
  - [x] File listing with metadata
- [x] SQLite cache layer
  - [x] Search result caching
  - [x] Model metadata caching
  - [x] Automatic expiry management
- [x] SearchService with cache coordination
- [x] Discover UI implementation
  - [x] Search bar with filters
  - [x] GGUF filter checkbox
  - [x] Sort options (downloads, likes, recent, trending)
  - [x] Model list with pagination
  - [x] Model details panel
  - [x] File list with GGUF highlighting
- [x] Python-QML bridge for async operations
- [x] Threaded search to keep UI responsive

#### In Progress:
- [ ] Testing & bug fixes
- [ ] Performance optimization

#### Acceptance Criteria:
- ✅ Search results show quickly
- ✅ Scrolling doesn't freeze UI
- ✅ GGUF files are clearly prioritised
- ⏳ Cached results load instantly on repeat searches

---

## Next Milestone: M2 - Download Manager

### M2: Download Manager (5–10 days)
**Status**: 📅 Planned

#### Planned Tasks:
- [ ] Download queue system
- [ ] Parallel downloads (configurable max concurrency)
- [ ] Resume/retry strategy
- [ ] File verification (size + SHA256)
- [ ] Download UI with progress bars
- [ ] Pause/cancel/retry controls

**Acceptance Criteria**:
- Interrupting a download and restarting the app resumes safely

---

## Upcoming Milestones

### M3: Shelf (3–7 days)
**Status**: 📅 Planned

### M4: Settings + Polish (3–5 days)
**Status**: 📅 Planned

### M5: Packaging (2–5 days)
**Status**: 📅 Planned

### M6: Docs + First Release (2–4 days)
**Status**: 📅 Planned

---

## Technical Implementation Notes

### M1 Architecture

**Hub Integration:**
- Abstract `HubAdapter` interface supports multiple sources
- `HuggingFaceAdapter` implementation uses `huggingface-hub` SDK
- GGUF detection via filename patterns (Q4_K_M, Q8_0, etc.)
- Async operations using `httpx` for non-blocking I/O

**Caching Strategy:**
- SQLite database for persistence
- 6-hour cache for search results
- 24-hour cache for model metadata
- Automatic expiry cleanup
- Hash-based query identification

**UI Architecture:**
- QML for declarative UI
- Python bridge classes with `@QmlElement` decorator
- QThread for background operations
- Signal/slot pattern for async updates
- Responsive design with proper loading states

**Key Files:**
- `sources/hub_adapter.py` - Abstract interface
- `sources/huggingface_adapter.py` - HF implementation
- `storage/database.py` - SQLAlchemy models
- `storage/cache.py` - Cache manager
- `app/services.py` - Business logic layer
- `ui/bridge.py` - Python-QML bridge
- `ui/qml/Discover.qml` - Main discover view
- `ui/qml/ModelDetailsPanel.qml` - Model details

---

## Testing Strategy

### Manual Testing (M1)
1. Search for "llama" - should show results quickly
2. Enable GGUF filter - should filter to GGUF models only
3. Click on a model - details panel should load
4. Check file list - GGUF files should be highlighted
5. Scroll model list - should remain smooth
6. Repeat search - should load from cache (faster)

### Known Limitations
- HF rate limiting not yet handled with backoff
- Network errors show generic error messages
- No retry mechanism for failed API calls
- Cache size not configurable yet

---

## Version History

### v0.1.0-dev (Current - M1)
- M0 complete: Basic skeleton and project structure
- M1 in progress: Hub browsing with search and caching
- Repository: [github.com/dmytro-macuser/ModelShelf](https://github.com/dmytro-macuser/ModelShelf)

---

## How to Test M1

```bash
# Setup
git clone https://github.com/dmytro-macuser/ModelShelf.git
cd ModelShelf
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Run
python main.py

# Test search
# 1. App should open to Discover tab
# 2. Try searching for "llama" or "mistral"
# 3. Enable "GGUF files only" filter
# 4. Click on a model to see details
# 5. Check that GGUF files are highlighted in green
```

---

**Last Updated**: 2026-01-02  
**Current Version**: 0.1.0-dev  
**Active Milestone**: M1 (Hub Browsing) - ~80% complete
