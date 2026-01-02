# ModelShelf 🙂
*Download once. Organise forever.*  
Tiny app, massive models.

ModelShelf is a lightweight Windows desktop app for browsing, downloading, and organising local LLM model files from Hugging Face into a tidy library ("your shelf").

![Development Status](https://img.shields.io/badge/status-M2%20Complete-green)
![Version](https://img.shields.io/badge/version-0.2.0--dev-blue)
![Licence](https://img.shields.io/badge/licence-MIT-green)

## ✨ Features

### ⬇️ Download Manager (New in M2!)
- **Robust Queue**: Manage multiple downloads with ease
- **Pause & Resume**: Stop downloads and continue them later, even after restarting the app
- **Smart Resumption**: Uses HTTP Range headers to append to partial files
- **Parallel Downloads**: Download up to 3 files simultaneously
- **Real-time Stats**: Track speed, progress, and ETA

### 🔍 Discovery
- **Browse Models**: Search Hugging Face with fast, cached results
- **GGUF-First**: Automatically highlights and prioritises GGUF model files
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

## 📚 Documentation

- [M2 Testing Guide](docs/M2_TESTING.md) - How to test the new download features
- [M1 Testing Guide](docs/M1_TESTING.md) - Discovery features
- [Architecture](docs/ARCHITECTURE.md) - Technical design

## 📝 Roadmap

- [x] **M0**: Project skeleton
- [x] **M1**: Hub browsing
- [x] **M2**: Download manager
- [ ] **M3**: Local shelf (Coming Next!)
- [ ] **M4**: Settings & polish
- [ ] **M5**: Windows packaging
- [ ] **M6**: v1.0 Release

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## 📜 Licence

MIT
