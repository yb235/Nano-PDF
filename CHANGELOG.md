# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-12-07

### Added
- `nano-pdf convert` command for high-fidelity PDF → PPTX conversion.
- PyMuPDF-powered text/image extraction to keep fonts, positions, and artwork editable.
- Nano Banana chart reconstruction that rebuilds bar/line/pie charts as live PowerPoint charts.
- Background strategy controls (`average_color`, `image`, `none`) plus debug thumbnail overlays.

### Changed
- Bumped project version to `0.3.0` and added `python-pptx` / `PyMuPDF` runtime dependencies.
- README now documents the converter workflow and troubleshooting tips.

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
