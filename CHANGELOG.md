# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2024-12-07

### Added
- **PDF to PowerPoint Conversion**: Complete PDF to PPTX converter with AI-powered features
- **Editable Chart Extraction**: AI-powered chart detection and data extraction for editable PowerPoint charts
- **Advanced PDF Analysis**: Deep structure extraction including text, images, shapes, and layouts
- **Font Preservation**: Exact font matching with intelligent fallback to similar fonts
- **Color Preservation**: RGB color matching for backgrounds, text, and shapes
- **AI Chart Analysis**: Uses Gemini Vision to extract chart data, categories, and series
- **Layout Preservation**: Maintains exact positioning and sizing of all elements
- **Multi-format Chart Support**: Bar, column, line, pie, scatter, and area charts
- New dependencies: python-pptx, pdfplumber, pdfminer.six, opencv-python, matplotlib, camelot-py, tabula-py

### Commands
- `nano-pdf convert` - Convert PDF to PowerPoint with AI enhancement
- `--use-ai-enhancement` - Enable/disable AI-powered analysis (default: enabled)
- `--extract-charts` - Enable/disable chart extraction and recreation (default: enabled)
- `--output` - Specify output PowerPoint filename

### Documentation
- Comprehensive PDF to PowerPoint conversion guide (PDF_TO_PPT_GUIDE.md)
- Updated README with conversion examples and best practices
- Chart conversion workflow documentation
- Troubleshooting guide for common conversion issues

### Features
- Text extraction with font, size, color, and style preservation
- Image extraction and embedding in PowerPoint
- Shape/vector graphics conversion
- Background color detection and application
- AI-powered chart region detection
- Chart type classification (bar, line, pie, etc.)
- Data extraction from chart images using Gemini Vision
- Native PowerPoint chart recreation with Excel data sheets
- Multi-page parallel processing support
- Progress tracking during conversion
- Sample PDF generator for testing

### Technical Improvements
- Modular converter architecture (PDFAnalyzer, ChartDetector, PowerPointBuilder)
- Sophisticated text grouping algorithms
- Font name normalization and mapping
- Color space conversion utilities
- Chart region detection using image analysis
- AI-powered structure analysis
- Efficient PDF parsing with pdfplumber and PyMuPDF

## [0.2.1] - 2024-XX-XX

### Added
- `nano-pdf add` command for creating new slides
- Default style reference to first page when not specified
- Document context enabled by default for new slides
- Google Search integration (enabled by default)

### Changed
- Improved prompt handling for slide generation
- Better error messages for API issues
- Enhanced style matching for new slides

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

[0.1.0]: https://github.com/gavrielc/Nano-PDF/releases/tag/v0.1.0
