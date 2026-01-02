# ModelShelf Development Status

## Current Milestone: M2 ✅ COMPLETE

### M2: Download Manager (5–10 days)
**Status**: ✅ Complete

#### Completed:
- [x] Download Manager core logic
  - [x] Queue management
  - [x] Chunked downloading with `httpx`
  - [x] Resumable downloads (Range headers)
  - [x] Concurrency control (default 3 active)
- [x] Download Service & Bridge
  - [x] Python-QML communication
  - [x] Progress signals (speed, ETA, %)
- [x] UI Implementation
  - [x] Downloads tab with list view
  - [x] Progress bars and status indicators
  - [x] Pause, Resume, Cancel, Retry controls
  - [x] "Add to Queue" integration in Discover details

#### Acceptance Criteria Met:
- ✅ Interrupting a download and restarting allows resumption (partial files saved)
- ✅ Parallel downloads work as expected
- ✅ UI updates in real-time without freezing

---

### M0: Repo + skeleton
**Status**: ✅ Complete

### M1: Hub browsing
**Status**: ✅ Complete

---

## Next Milestone: M3 - Shelf

### M3: Shelf (3–7 days)
**Status**: 📅 Planned

#### Planned Tasks:
- [ ] Local model indexing (scanning download folder)
- [ ] Shelf UI view (grid/list of downloaded models)
- [ ] Disk usage calculation and visualization
- [ ] "Open in Explorer" actions
- [ ] Delete/Remove functionality

---

## Upcoming Milestones

### M4: Settings + Polish
**Status**: 📅 Planned

### M5: Packaging
**Status**: 📅 Planned

### M6: Docs + First Release
**Status**: 📅 Planned

---

## Version History

### v0.2.0-dev (M2)
- Added full download management
- Downloads tab active
- Queue system implemented

### v0.1.0-dev (M1)
- Hub browsing and search

---

**Last Updated**: 2026-01-02
