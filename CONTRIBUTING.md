# Contributing to ModelShelf

Thank you for your interest in contributing to ModelShelf! 🙂

## Development Setup

### Prerequisites
- Python 3.11 or higher
- Git
- Windows 10/11 (for testing native features)

### Getting Started

1. Fork and clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/ModelShelf.git
cd ModelShelf
```

2. Create a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python main.py
```

## Project Structure

```
ModelShelf/
├── ui/              # QML interface files
├── app/             # Application startup & config
├── domain/          # Core business logic
├── sources/         # Hub adapters
├── downloader/      # Download management
├── library/         # Local model indexing
├── storage/         # Database & settings
├── integrations/    # External tool integrations
├── main.py          # Entry point
└── requirements.txt
```

## Coding Guidelines

### General
- Use UK English spelling (organise, licence, favourite)
- Follow PEP 8 style guidelines
- Add docstrings to all public functions and classes
- Keep functions small and focused

### Python
- Type hints are encouraged
- Use pathlib for file operations
- Prefer composition over inheritance

### QML
- Component names use PascalCase
- Property names use camelCase
- Keep components small and reusable

## Commit Messages

Follow this format:
```
[Milestone]: Brief description

Detailed explanation if needed.
```

Examples:
- `M0: Add navigation sidebar component`
- `M1: Implement model search with pagination`
- `M2: Fix download resume on app restart`

## Milestones

See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for the full roadmap. Current milestone:

- **M0**: Repo + skeleton (✅ In Progress)
- M1: Hub browsing
- M2: Download manager
- M3: Shelf
- M4: Settings + polish
- M5: Packaging
- M6: Docs + first release

## Testing

(Coming soon)

## Pull Requests

1. Create a feature branch from `main`
2. Make your changes
3. Test thoroughly
4. Submit a pull request with a clear description
5. Reference any related issues

## Questions?

Open an issue with the "question" label, and we'll be happy to help!

## Licence

By contributing, you agree that your contributions will be licensed under the MIT Licence.
