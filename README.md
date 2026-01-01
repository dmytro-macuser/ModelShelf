# ModelShelf 🙂
*Download once. Organise forever.*  
Tiny app, massive models.

ModelShelf is a lightweight Windows desktop app for browsing, downloading, and organising local LLM model files from the Hub into a tidy library ("your shelf").

## Features
- Discover models with clear, concise filters.
- GGUF-first file browsing (quickly find the right downloads).
- Download queue with pause/resume, retry, and progress tracking.
- Shelf view: see what you have, where it is stored, and how much space it uses.
- Runner-agnostic: works as a model library manager (no built-in chat/inference).

## Install (Windows)
### Option A: Installer (recommended)
1. Download the latest release from the Releases page.
2. Run the installer.
3. Launch ModelShelf from the Start menu.

### Option B: Portable ZIP
1. Download the portable build.
2. Extract anywhere (e.g., `D:\Apps\ModelShelf\`).
3. Run `ModelShelf.exe`.

## Quick start
1. Open **Discover**.
2. Search for a model.
3. Open the model details and choose the file(s) you want.
4. Add to **Downloads**.
5. Once complete, view it in **Shelf**.

## Settings
- Download folder: Choose where model files are stored.
- Cache: Controls how much metadata is cached for faster browsing.
- Token (optional): For users who need access to gated resources.

## Development
### Requirements
- Python 3.11+
- PySide6 (Qt for Python)

### Run locally
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Project Status
Currently in development. See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for the full roadmap.

## Licence
MIT
