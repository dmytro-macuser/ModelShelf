# ModelShelf 😊
*Download once. Organise forever.*  
Tiny app, massive models.

ModelShelf is a lightweight Windows desktop app for browsing, downloading, and organising local LLM model files from Hugging Face into a beautiful visual library.

![Development Status](https://img.shields.io/badge/status-M3%20Complete-green)
![Version](https://img.shields.io/badge/version-0.3.0--dev-blue)
![Licence](https://img.shields.io/badge/licence-MIT-green)

## ✨ Features

### 📚 Beautiful Bookshelf (New in M3!)
- **Visual Library**: Your models displayed as colorful book spines on wooden shelves
- **Smart Organization**: Automatic indexing of downloaded models
- **Quick Actions**: Click any book to view details, open folder, or delete
- **GGUF Indicators**: Green badges show GGUF file counts at a glance
- **Disk Usage**: See total library size and model counts
- **Empty State**: Beautiful placeholder shelves when starting fresh

### ⬇️ Download Manager
- **Robust Queue**: Manage multiple downloads with ease
- **Pause & Resume**: Stop downloads and continue them later
- **Parallel Downloads**: Download up to 3 files simultaneously
- **Real-time Stats**: Track speed, progress, and ETA

### 🔍 Discovery
- **Browse Models**: Search Hugging Face with fast, cached results
- **GGUF-First**: Automatically highlights GGUF model files
- **Smart Filters**: Filter by tag, sort by popularity or recency
- **Detailed Info**: View model cards, licences, and file lists

## 🚀 Quick Start

### Requirements
- Python 3.11+
- Windows 10/11 (primary target)

### Installation

```bash
# Clone
git clone https://github.com/dmytro-macuser/ModelShelf.git
cd ModelShelf

# Setup
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Run
python main.py
```

## 📸 Screenshots

*Coming soon - the bookshelf is beautiful! 📚*

## 📚 Documentation

- [M3 Testing Guide](docs/M3_TESTING.md) - How to test the bookshelf library
- [M2 Testing Guide](docs/M2_TESTING.md) - Download features
- [M1 Testing Guide](docs/M1_TESTING.md) - Discovery features
- [Architecture](docs/ARCHITECTURE.md) - Technical design

## 📝 Roadmap

- [x] **M0**: Project skeleton
- [x] **M1**: Hub browsing
- [x] **M2**: Download manager
- [x] **M3**: Bookshelf library view
- [ ] **M4**: Settings & polish (Coming Next!)
- [ ] **M5**: Windows packaging
- [ ] **M6**: v1.0 Release

## 🎨 Design Philosophy

**Visual First**: ModelShelf uses a bookshelf metaphor to make your local model library feel tangible and organized, just like a real library.

**GGUF-Focused**: While supporting all file types, ModelShelf highlights GGUF models since they're the most common format for local LLM inference.

**Lightweight**: No bloat, no unnecessary features. Just the essentials done well.

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## 📜 Licence

MIT
