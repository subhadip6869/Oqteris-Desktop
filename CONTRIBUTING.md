# Contributing to Oqteris

Thank you for your interest in contributing to Oqteris!

## Code of Conduct

Please maintain a respectful, welcoming, and inclusive atmosphere when participating in discussions, reporting issues, or submitting code.

## Development Setup

1. **Prerequisites**:
   - Python 3.13 or newer
   - Git
   - Tesseract OCR (optional, for OCR testing)
   - Visual C++ Build Tools (Windows) or standard C/C++ compiler toolchain (Linux/macOS)

2. **Clone the Repository**:
   ```bash
   git clone https://github.com/subhadip6869/Oqteris-Desktop.git
   cd Oqteris-Desktop
   ```

3. **Virtual Environment & Dependencies**:
   ```bash
   python -m venv .venv
   # Windows:
   .\.venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate

   pip install -r requirements.txt
   ```

4. **Running the Application**:
   ```bash
   python -m oqteris
   ```

5. **Running Tests**:
   ```bash
   pytest tests/
   ```

## Architectural Guidelines

- **Separation of Concerns**: Do not place PDF manipulation or disk I/O logic in QML. Use QObject controllers in Python and expose properties/signals to QML.
- **Thread Safety**: Never interact with UI or QML elements from background worker threads. Use Qt signals/slots or thread pools.
- **Digital Signatures**: Never execute destructive modifications on digitally signed PDFs without warning and presenting safe incremental update alternatives.
- **Licensing**: Keep third-party license obligations transparent. Do not incorporate GPL/AGPL-incompatible modules into core runtime code without documenting compliance.

## Pull Request Guidelines

1. Create a feature branch from `main`: `git checkout -b feature/my-feature`.
2. Format and lint code with `ruff check .` and ensure type annotations are valid.
3. Write comprehensive unit and integration tests under `tests/`.
4. Ensure all tests pass with `pytest`.
5. Submit a descriptive Pull Request referencing any related issues.
