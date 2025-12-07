# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-12-07

### Added
- **PDF to PowerPoint Conversion** (`nano-pdf toppt`) - Convert PDFs to editable PPTX files
  - Extracts text with font, size, color, and positioning preserved
  - **AI-powered chart extraction** - Charts are converted to native, editable PowerPoint charts with actual data
  - Table extraction as editable PowerPoint tables
  - Image extraction with position preservation
  - Shape detection and conversion
  - Parallel processing for fast conversion
  - Fallback to image for complex elements

- **Page Analysis** (`nano-pdf analyze`) - Preview what elements will be extracted
  - Detect charts, tables, text blocks, images, and shapes
  - View chart data before conversion
  - Export analysis to JSON

- **New AI Functions**
  - `analyze_page_for_charts()` - Detect and extract chart data using Gemini
  - `analyze_page_layout()` - Identify all page elements
  - `extract_table_data()` - Extract table structure and content
  - `enhance_slide_extraction()` - Correct OCR and add styling info
  - `extract_slide_content_comprehensive()` - Full page extraction

- **Programmatic API**
  - `PDFToPPTConverter` class for custom conversion workflows
  - `ConversionOptions` dataclass for configuration
  - `convert_pdf_to_pptx()` convenience function
  - `convert_pdf_to_pptx_with_ai()` for AI-powered conversion
  - Rich data structures for slide content (`SlideContent`, `ChartData`, etc.)

### New Dependencies
- `python-pptx>=0.6.21` - PowerPoint file creation
- `PyMuPDF>=1.23.0` - Advanced PDF parsing

### Documentation
- Architecture documentation (`doc/ARCHITECTURE.md`)
- API reference (`doc/API.md`)
- Updated README with toppt examples and options

## [0.2.1] - 2025-XX-XX

### Added
- `nano-pdf add` command for adding new AI-generated slides
- `--disable-google-search` option
- Better handling of Google Search in prompts

## [0.1.0] - 2025-01-XX

### Added
- Initial release of Nano PDF
- Natural language PDF editing using Gemini 3 Pro Image
- Multi-page parallel processing (up to 10 concurrent pages)
- OCR re-hydration to preserve searchable text layer
- Style reference support for consistent visual editing
- Configurable resolution (4K, 2K, 1K)
- Optional full-document context mode
- Cross-platform support (macOS, Linux, Windows)
- System dependency checking with helpful error messages
- Automatic page range validation
- Duplicate page edit handling (merges prompts)
- Temporary file cleanup
- Progress tracking during batch operations
- Comprehensive error messages for API issues

### Features
- `nano-pdf edit` command for editing PDF pages
- `nano-pdf version` command for version information
- `--style-refs` option for visual style consistency
- `--use-context` option for document-wide context
- `--output` option for custom output filename
- `--resolution` option for quality/cost balance

### Documentation
- Complete README with installation, usage, and examples
- System dependency installation guide for macOS, Windows, Linux
- Troubleshooting section
- API key setup instructions
- Contributing guidelines
- Code of Conduct

### Infrastructure
- PyPI package configuration
- GitHub repository setup
- MIT License

[0.3.0]: https://github.com/gavrielc/Nano-PDF/releases/tag/v0.3.0
[0.2.1]: https://github.com/gavrielc/Nano-PDF/releases/tag/v0.2.1
[0.1.0]: https://github.com/gavrielc/Nano-PDF/releases/tag/v0.1.0
