# ModelShelf 🙂
*Download once. Organise forever.*  
Tiny app, massive models.

ModelShelf is a lightweight Windows desktop app for browsing, downloading, and organising local LLM model files from Hugging Face into a tidy library ("your shelf").

![Development Status](https://img.shields.io/badge/status-M1%20In%20Progress-yellow)
![Version](https://img.shields.io/badge/version-0.1.0--dev-blue)
![Licence](https://img.shields.io/badge/licence-MIT-green)

## ✨ Features (M1 - In Progress)

### ✅ Currently Working
- **Discover models** from Hugging Face with fast search
- **GGUF-first browsing**: GGUF files are highlighted and prioritised
- **Smart filters**: Text search, GGUF-only filter, sort by downloads/likes/recent/trending
- **Model details**: View description, tags, licence, download stats, and complete file lists
- **Intelligent caching**: Search results and metadata cached for instant repeat access
- **Responsive UI**: Background loading keeps the interface smooth
- **Quantisation detection**: Automatically identifies Q4_K_M, Q8_0, and other GGUF variants

### 🚧 Coming Soon
- **Downloads** (M2): Queue management with pause/resume/retry
- **Shelf** (M3): Local library view with disk usage tracking
- **Settings** (M4): Configure download folder, cache size, HF token
- **Packaging** (M5): Windows installer and portable builds

## 🚀 Quick Start

### Requirements
- Python 3.11+
- Windows 10/11 (primary target)
- Internet connection for browsing models

### Installation

```bash
# Clone the repository
git clone https://github.com/dmytro-macuser/ModelShelf.git
cd ModelShelf

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

### First Use

1. **Discover Tab** opens automatically
2. Try searching for "llama" or "mistral"
3. Enable **"GGUF files only"** to filter results
4. Click on a model to view details
5. Notice GGUF files highlighted in green with quantisation info

## 📚 Documentation

- [Implementation Plan](IMPLEMENTATION_PLAN.md) - Full roadmap and milestones
- [Development Status](DEVELOPMENT.md) - Current progress and technical notes
- [Contributing Guide](CONTRIBUTING.md) - How to contribute

## 🛠️ Architecture

```
ModelShelf/
├── ui/              # QML interface + Python bridge
├── app/             # Application core & services
├── domain/          # Business logic & models
├── sources/         # Hub adapters (HuggingFace)
├── downloader/      # Download manager (M2)
├── library/         # Local model indexing (M3)
├── storage/         # SQLite cache & settings
└── integrations/    # External tools (future)
```

### Key Technologies
- **UI**: PySide6 (Qt) with QML for declarative interfaces
- **API**: Hugging Face Hub SDK
- **Storage**: SQLite for caching, JSON for settings
- **Async**: QThread for background operations

## 🐛 Known Issues

- Rate limiting from HF API not yet handled with backoff
- Network errors show generic messages
- Cache size not configurable (fixed 6h for search, 24h for models)
- No retry mechanism for failed API calls

## 📝 Roadmap

- [x] **M0**: Project structure & skeleton UI
- [x] **M1**: Hub browsing (80% complete)
- [ ] **M2**: Download manager with queue
- [ ] **M3**: Local shelf with disk management
- [ ] **M4**: Settings & polish
- [ ] **M5**: Windows packaging
- [ ] **M6**: Documentation & v1.0 release

See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for detailed milestone breakdown.

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Setup
```bash
git clone https://github.com/YOUR_USERNAME/ModelShelf.git
cd ModelShelf
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## 💬 Support

Having issues?
1. Check [DEVELOPMENT.md](DEVELOPMENT.md) for troubleshooting
2. Review existing [Issues](https://github.com/dmytro-macuser/ModelShelf/issues)
3. Open a new issue with details

## 📜 Licence

MIT Licence - see [LICENSE](LICENSE) for details.

---

**Made with ❤️ for the LLM community**  
*Small app. Big brains.*
