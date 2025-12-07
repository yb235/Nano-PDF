# Development Guide

Guide for developers who want to contribute to or extend Nano PDF.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Code Style and Standards](#code-style-and-standards)
- [Testing](#testing)
- [Making Changes](#making-changes)
- [Submitting Contributions](#submitting-contributions)
- [Debugging](#debugging)
- [Extending Nano PDF](#extending-nano-pdf)

## Getting Started

### Prerequisites

- Python 3.10 or newer
- Git
- Basic understanding of Python and PDFs
- Familiarity with command-line tools

### Quick Start

```bash
# Clone the repository
git clone https://github.com/gavrielc/Nano-PDF.git
cd Nano-PDF

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install system dependencies (macOS example)
brew install poppler tesseract

# Install the package in development mode
pip install -e .

# Set up your API key
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Verify installation
nano-pdf version
```

## Development Setup

### Recommended Tools

- **IDE**: VS Code, PyCharm, or your preferred editor
- **Python packages**: Install development dependencies
- **Git**: For version control
- **Terminal**: For running commands

### Using uv (Recommended for Fast Setup)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer:

```bash
# Install uv
pip install uv

# Sync dependencies
uv sync

# Run the tool
uv run nano-pdf version

# Run Python scripts
uv run python scripts/test_script.py
```

### Manual Setup with pip

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in editable mode
pip install -e .

# Install development dependencies
pip install pytest black flake8 mypy
```

### Setting Up Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Project Structure

```
Nano-PDF/
├── nano_pdf/              # Main package
│   ├── __init__.py       # Package initialization
│   ├── main.py           # CLI entry point (Typer app)
│   ├── ai_utils.py       # Gemini API integration
│   └── pdf_utils.py      # PDF processing utilities
├── docs/                  # Documentation
│   ├── README.md         # Documentation index
│   ├── ARCHITECTURE.md   # System architecture
│   ├── USER_GUIDE.md     # User guide
│   ├── API_REFERENCE.md  # CLI reference
│   ├── INSTALLATION.md   # Installation guide
│   ├── TROUBLESHOOTING.md # Troubleshooting
│   ├── EXAMPLES.md       # Usage examples
│   ├── FAQ.md            # FAQ
│   └── DEVELOPMENT.md    # This file
├── assets/               # Images and media
├── tests/                # Test files (if any)
├── .github/              # GitHub configuration
│   └── workflows/        # CI/CD workflows
├── pyproject.toml        # Project configuration
├── README.md             # Main readme
├── CONTRIBUTING.md       # Contribution guidelines
├── CODE_OF_CONDUCT.md    # Code of conduct
├── CHANGELOG.md          # Version history
├── LICENSE               # MIT License
├── .env.example          # Example environment file
└── .gitignore           # Git ignore rules
```

### Key Modules

#### `main.py`
- CLI interface using Typer
- Command definitions: `edit`, `add`, `version`
- Input validation and error handling
- Parallel processing coordination
- Progress reporting

#### `ai_utils.py`
- Gemini API client initialization
- Image generation functions
- Prompt construction
- Error handling for API calls

#### `pdf_utils.py`
- PDF page counting
- Text extraction (using pdftotext)
- Page rendering (pdf2image)
- OCR re-hydration (Tesseract)
- Page replacement and insertion
- System dependency checking

## Code Style and Standards

### Python Style

We follow **PEP 8** with these specifics:

- **Line length**: 120 characters (Pythonic)
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings
- **Type hints**: Use for function signatures
- **Docstrings**: Use for all public functions

### Example Function

```python
def render_page_as_image(pdf_path: str, page_number: int) -> Image.Image:
    """
    Renders a specific page (1-indexed) as a PIL Image.
    
    Args:
        pdf_path: Path to the PDF file
        page_number: Page number (1-indexed)
        
    Returns:
        PIL Image of the rendered page
        
    Raises:
        ValueError: If page_number is invalid or page cannot be rendered
    """
    images = convert_from_path(
        pdf_path,
        first_page=page_number,
        last_page=page_number
    )
    if not images:
        raise ValueError(f"Could not render page {page_number}")
    return images[0]
```

### Code Formatting

Use **Black** for automatic formatting:

```bash
# Format all files
black nano_pdf/

# Check without modifying
black --check nano_pdf/
```

### Linting

Use **flake8** for linting:

```bash
# Run flake8
flake8 nano_pdf/

# Configuration in .flake8 or pyproject.toml
```

### Type Checking

Use **mypy** for type checking:

```bash
# Run mypy
mypy nano_pdf/

# Configuration in mypy.ini or pyproject.toml
```

### Import Order

Follow this import order:

1. Standard library imports
2. Third-party imports
3. Local application imports

```python
import os
import subprocess
from typing import List, Tuple
from pathlib import Path

from PIL import Image
from google import genai
import typer

from nano_pdf import pdf_utils
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=nano_pdf

# Run specific test file
pytest tests/test_pdf_utils.py

# Run specific test
pytest tests/test_pdf_utils.py::test_page_count
```

### Writing Tests

Create test files in `tests/` directory:

```python
# tests/test_pdf_utils.py
import pytest
from nano_pdf import pdf_utils

def test_get_page_count():
    """Test page counting."""
    count = pdf_utils.get_page_count("test_files/sample.pdf")
    assert count == 5

def test_invalid_pdf():
    """Test error handling for invalid PDF."""
    with pytest.raises(Exception):
        pdf_utils.get_page_count("nonexistent.pdf")
```

### Test Data

Store test PDFs in `tests/test_files/` (add to .gitignore if large).

### Integration Tests

For integration tests that use the API:

```python
import os
import pytest

@pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY not set"
)
def test_generate_slide():
    """Integration test for slide generation."""
    # Test code here
```

## Making Changes

### Workflow

1. **Create a branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes:**
   - Edit code
   - Add tests
   - Update documentation

3. **Test locally:**
   ```bash
   # Run tests
   pytest
   
   # Run linting
   flake8 nano_pdf/
   
   # Format code
   black nano_pdf/
   
   # Test CLI
   nano-pdf edit test.pdf 1 "Test edit"
   ```

4. **Commit changes:**
   ```bash
   git add .
   git commit -m "Add: Brief description of changes"
   ```

5. **Push to GitHub:**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open Pull Request** on GitHub

### Commit Message Format

Use descriptive commit messages:

```
Add: New feature or functionality
Fix: Bug fix
Update: Changes to existing functionality
Docs: Documentation updates
Test: Test additions or modifications
Refactor: Code restructuring without behavior change
```

Examples:
```
Add: Support for custom output resolution
Fix: Handle empty PDF files gracefully
Update: Improve error messages for API failures
Docs: Add examples for batch processing
```

## Submitting Contributions

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

### Pull Request Process

1. **Open PR** on GitHub
2. **Fill out template** with:
   - Description of changes
   - Why changes are needed
   - Testing performed
   - Any breaking changes

3. **Address review feedback**
4. **Wait for approval** from maintainers
5. **Merge** once approved

### Review Criteria

Reviewers will check:
- Code quality and style
- Test coverage
- Documentation completeness
- Breaking changes
- Performance implications

## Debugging

### Using Python Debugger

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use built-in breakpoint()
breakpoint()
```

### Verbose Logging

Add temporary print statements:

```python
print(f"Debug: page_number={page_number}")
print(f"Debug: replacements={replacements}")
```

Or use logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"Processing page {page_number}")
```

### Testing API Calls

Test API integration separately:

```python
# scripts/test_api.py
from nano_pdf import ai_utils
from PIL import Image

# Load test image
img = Image.open("test_image.png")

# Test generation
result, text = ai_utils.generate_edited_slide(
    target_image=img,
    style_reference_images=[],
    full_text_context="",
    user_prompt="Test prompt",
    resolution="1K"
)

print(f"Generated: {result.size}")
print(f"Text: {text}")
```

### Debugging PDF Issues

```bash
# Check PDF structure
pdfinfo file.pdf

# Extract text
pdftotext file.pdf -

# View PDF metadata
pdftk file.pdf dump_data
```

## Extending Nano PDF

### Adding New Commands

1. **Define command in `main.py`:**

```python
@app.command()
def my_command(
    pdf_path: str = typer.Argument(..., help="PDF file"),
    option: str = typer.Option("default", help="An option")
):
    """
    Description of your command.
    """
    # Implementation
    typer.echo("Running my command")
```

2. **Add supporting functions** in appropriate module

3. **Update documentation**

4. **Add tests**

### Adding New PDF Operations

Add functions to `pdf_utils.py`:

```python
def rotate_page(pdf_path: str, page_number: int, angle: int, output_path: str):
    """
    Rotate a page by specified angle.
    
    Args:
        pdf_path: Input PDF path
        page_number: Page to rotate (1-indexed)
        angle: Rotation angle (90, 180, 270)
        output_path: Output PDF path
    """
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    
    for i, page in enumerate(reader.pages):
        if i == page_number - 1:
            page.rotate(angle)
        writer.add_page(page)
    
    with open(output_path, 'wb') as f:
        writer.write(f)
```

### Supporting New AI Models

Create new module (e.g., `claude_utils.py`):

```python
def generate_with_claude(target_image, prompt):
    """
    Generate using Claude (example).
    """
    # Implementation
    pass
```

Update `main.py` to support model selection:

```python
@app.command()
def edit(
    ...,
    model: str = typer.Option("gemini", help="AI model: gemini, claude")
):
    if model == "gemini":
        result = ai_utils.generate_edited_slide(...)
    elif model == "claude":
        result = claude_utils.generate_with_claude(...)
```

### Adding Configuration Files

Support for config files (e.g., `nano-pdf.yaml`):

```python
import yaml

def load_config(config_path: str = "nano-pdf.yaml"):
    """Load configuration from YAML file."""
    if not Path(config_path).exists():
        return {}
    
    with open(config_path) as f:
        return yaml.safe_load(f)
```

### Plugin System (Future)

Design for plugin support:

```python
# plugins/watermark_plugin.py
class WatermarkPlugin:
    def process(self, image: Image.Image) -> Image.Image:
        # Add watermark
        return image

# main.py - load plugins
from plugins import WatermarkPlugin

plugins = [WatermarkPlugin()]
for plugin in plugins:
    image = plugin.process(image)
```

## Build and Release

### Building Package

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Check distribution
twine check dist/*
```

### Publishing to PyPI

```bash
# Test upload to TestPyPI
twine upload --repository testpypi dist/*

# Production upload
twine upload dist/*
```

### Version Bumping

Update version in:
- `pyproject.toml` - `version = "X.Y.Z"`
- `main.py` - `version()` function
- `CHANGELOG.md` - Add entry for new version

### Creating Releases

1. Update version numbers
2. Update CHANGELOG.md
3. Commit changes
4. Create git tag: `git tag -a vX.Y.Z -m "Version X.Y.Z"`
5. Push tag: `git push origin vX.Y.Z`
6. Create GitHub release
7. Build and upload to PyPI

## Resources

### Documentation

- [Architecture](ARCHITECTURE.md) - System design
- [User Guide](USER_GUIDE.md) - End-user documentation
- [API Reference](API_REFERENCE.md) - CLI reference
- [Contributing](../CONTRIBUTING.md) - Contribution guidelines

### External Resources

- [Typer Documentation](https://typer.tiangolo.com/)
- [pypdf Documentation](https://pypdf.readthedocs.io/)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [pdf2image Documentation](https://github.com/Belval/pdf2image)
- [Tesseract Documentation](https://github.com/tesseract-ocr/tesseract)

### Community

- [GitHub Issues](https://github.com/gavrielc/Nano-PDF/issues)
- [GitHub Discussions](https://github.com/gavrielc/Nano-PDF/discussions)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/nano-pdf)

## Questions?

Feel free to:
- Open an issue for bugs or feature requests
- Start a discussion for questions
- Submit PRs for improvements
- Contact maintainers

Happy coding! 🎉
