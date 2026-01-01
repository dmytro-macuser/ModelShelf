# ModelShelf 🙂 — Implementation Plan (v1)

## Product goal (v1)
Build a lightweight Windows desktop app that helps users browse, download, and organise local LLM model files from the Hub into a tidy "shelf".

Taglines:
- Serious: Tiny app, massive models.
- Primary: Download once. Organise forever.
- Playful: Small app. Big brains.

## Scope
### In-scope (v1)
- Browse/search models
- GGUF-first discovery (detect and prioritise `.gguf` files)
- Clear filters (size, popularity signals, recency signals, quantisation keywords)
- Model details panel (basic metadata + file list)
- Download queue with pause/cancel/retry
- Local "Shelf" view (what's downloaded, where it lives, disk usage)
- Settings (download folder, cache size, optional token storage)
- Export/share: "Open folder", "Copy path", "Reveal in Explorer"

### Out-of-scope (v1)
- Running/inference/chat UI
- Model conversion/quantisation
- Account management beyond token entry (no OAuth flows in v1)
- Multiple hubs/sources (design for it, but ship one source in v1)

## Target platform (v1)
- Windows 10/11 (x64)

## UX principles
- Runner-agnostic language: "Runner integrations" are optional add-ons.
- UK English spelling everywhere (organise, licence, favourite).
- Avoid clutter: show "just enough" info for safe downloading (size, filename, licence tag if available).
- Respect disk space: always show total size before starting downloads.

## App information architecture
Tabs (left sidebar or top tabs):
- Discover
- Downloads
- Shelf
- Settings
- About

### Discover
- Search bar + quick filters
- Results list/grid
- Details pane:
  - Summary
  - Tags
  - Licence (if available)
  - Files (focus on GGUF)

### Downloads
- Queue list with states:
  - Queued, Downloading, Paused, Completed, Failed, Cancelled
- Per-item actions:
  - Pause/Resume, Cancel, Retry, Open folder
- Global actions:
  - Pause all, Resume all, Clear completed

### Shelf
- Local library index
- Sort: size, name, last used, date added
- Actions:
  - Open folder, Remove from shelf (delete), Re-scan folder
- Storage view:
  - Total size + per-model sizes

## Technical architecture
### Key modules
- `ui/` (QML + minimal Python glue)
- `app/` (startup, navigation, dependency wiring)
- `domain/` (pure logic: models, files, downloads, filters)
- `sources/` (Hub adapter interface; v1 implements one source)
- `downloader/` (queue, resumable downloads, verification)
- `library/` (indexing, disk usage, metadata cache)
- `storage/` (SQLite cache, settings, token storage)
- `integrations/` (optional runner folder linking; v1 can be "coming soon")

### Data storage
- SQLite:
  - cached search results
  - cached file lists
  - download history
  - shelf index
- Settings file:
  - download folder path
  - cache limits
  - UI preferences
- Token storage:
  - optional; store securely if available, otherwise "session only"

## Milestones
### M0 — Repo + skeleton (1–2 days)
- Project structure
- Basic QML shell with sidebar navigation
- Settings persistence
- Logging + crash-safe error dialog

### M1 — Hub browsing (3–7 days)
- Model search (paged)
- Basic filters (text + "has GGUF")
- Model details + file listing

Acceptance:
- Search results show quickly and scrolling doesn't freeze UI.

### M2 — Download manager (5–10 days)
- Queue system
- Parallel downloads (configurable max concurrency)
- Resume/retry strategy
- Verify: size matches expected after download

Acceptance:
- Interrupting a download and restarting the app resumes safely.

### M3 — Shelf (3–7 days)
- Shelf index from download history + folder scan
- Disk usage calculation
- Remove from shelf (delete files) with confirmation

Acceptance:
- Shelf accurately reflects real files even after manual moves (via re-scan).

### M4 — Settings + polish (3–5 days)
- Download folder picker
- Cache size controls
- Optional token entry
- Clear UX copy (UK spelling)

Acceptance:
- Fresh install experience is understandable without reading docs.

### M5 — Packaging (2–5 days)
- Windows packaging
- Icon, versioning, installer choice
- Portable build (optional)

Acceptance:
- A clean Windows machine can install and run without Python installed.

### M6 — Docs + first release (2–4 days)
- README + screenshots
- Basic troubleshooting notes
- Licence + third-party notices

Acceptance:
- v1 public release is understandable and reproducible to build.

## Risks to plan for early
- Very large files (timeouts, interruptions, disk full)
- Rate limiting from the Hub (cache + backoff + helpful UI errors)
- Inconsistent repo naming conventions (quantisation detection heuristics)
- Users with slow disks/old machines (keep UI responsive; background threads)
