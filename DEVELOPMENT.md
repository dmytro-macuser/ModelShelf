# ModelShelf Development Status

## Current Milestone: M0 ✅ COMPLETE

### M0: Repo + skeleton (1–2 days)
**Status**: ✅ Complete

#### Completed:
- [x] Project structure created
- [x] Module directories established
  - [x] `ui/` - QML interface
  - [x] `app/` - Application core
  - [x] `domain/` - Business logic
  - [x] `sources/` - Hub adapters
  - [x] `downloader/` - Download management
  - [x] `library/` - Model indexing
  - [x] `storage/` - Settings & database
  - [x] `integrations/` - External tools
- [x] Basic QML shell with sidebar navigation
- [x] Settings persistence (JSON-based)
- [x] Logging configured
- [x] Error handling framework
- [x] Configuration management
- [x] Development documentation

---

## Next Milestone: M1 - Hub Browsing

### M1: Hub browsing (3–7 days)
**Status**: ⏳ Not Started

#### Tasks:
- [ ] Implement Hugging Face Hub API adapter
- [ ] Model search with pagination
- [ ] Basic filters:
  - [ ] Text search
  - [ ] "Has GGUF" filter
  - [ ] Size filter
  - [ ] Popularity sort
- [ ] Model details panel:
  - [ ] Metadata display
  - [ ] File list with GGUF highlighting
  - [ ] Licence information
  - [ ] Tags display
- [ ] Result caching (SQLite)
- [ ] UI responsiveness testing

**Acceptance Criteria**:
- Search results show quickly and scrolling doesn't freeze UI
- GGUF files are clearly prioritised in file listings
- Cached results load instantly on repeat searches

---

## Upcoming Milestones

### M2: Download Manager (5–10 days)
**Status**: 📅 Planned

### M3: Shelf (3–7 days)
**Status**: 📅 Planned

### M4: Settings + Polish (3–5 days)
**Status**: 📅 Planned

### M5: Packaging (2–5 days)
**Status**: 📅 Planned

### M6: Docs + First Release (2–4 days)
**Status**: 📅 Planned

---

## Development Notes

### Current Architecture
- **UI Framework**: PySide6 (Qt for Python) with QML
- **Settings**: JSON file storage
- **Database**: SQLite (to be implemented in M1)
- **Logging**: Python logging module with file output

### Key Decisions
1. **UK English**: All UI text and docs use UK spelling
2. **Runner-agnostic**: ModelShelf is a library manager, not an inference tool
3. **Single source (v1)**: Hugging Face Hub only; architecture supports future sources
4. **GGUF-first**: Prioritise GGUF files in discovery and listings

### Testing Strategy
(To be defined in M1)

---

## Version History

### v0.1.0-dev (Current)
- M0 complete: Basic skeleton and project structure
- Repository initialised: [github.com/dmytro-macuser/ModelShelf](https://github.com/dmytro-macuser/ModelShelf)
- Development environment configured

---

## How to Contribute

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

### Quick Start for Contributors
```bash
# Clone and setup
git clone https://github.com/dmytro-macuser/ModelShelf.git
cd ModelShelf
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Run
python main.py
```

---

**Last Updated**: 2026-01-01  
**Current Version**: 0.1.0-dev  
**Active Milestone**: M0 → M1 transition
