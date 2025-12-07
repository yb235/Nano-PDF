<p align="center">
  <img src="https://raw.githubusercontent.com/gavrielc/Nano-PDF/main/assets/Nano%20PDF.png" alt="Nano PDF Logo" width="300"/>
</p>

# Nano PDF Editor

[![PyPI version](https://badge.fury.io/py/nano-pdf.svg)](https://badge.fury.io/py/nano-pdf)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A CLI tool to edit PDF slides using natural language prompts and **convert PDFs to editable PowerPoint presentations**, powered by Google's **Gemini 3 Pro Image** ("Nano Banana") model.

## Features

*   **Natural Language Editing**: "Update the graph to include data from 2025", "Change the chart to a bar graph".
*   **Add New Slides**: Generate entirely new slides that match your deck's visual style.
*   **PDF to PowerPoint Conversion**: Convert PDFs to PPTX with editable charts, tables, and text.
*   **AI-Powered Chart Extraction**: Charts are extracted with their actual data, making them fully editable in PowerPoint.
*   **Non-Destructive**: Preserves the searchable text layer of your PDF using OCR re-hydration.
*   **Multi-page & Parallel**: Edit multiple pages or convert entire decks with concurrent processing.

## Example

### Edit a PDF

```bash
nano-pdf edit linkedin-deck.pdf 1 "Change the tagline in the logo to 'Cringe posts from work colleagues' and update the date"
```

| Before | After |
|--------|-------|
| ![Before](https://raw.githubusercontent.com/gavrielc/Nano-PDF/main/assets/linkedin-before.png) | ![After](https://raw.githubusercontent.com/gavrielc/Nano-PDF/main/assets/linkedin-after.png) |

*[Original deck](https://www.peterfisk.com/wp-content/uploads/2025/10/LinkedIn-Pitch-Deck.-2004.-Series-B-1.pdf) from LinkedIn's 2004 Series B pitch | [Edited deck](https://github.com/gavrielc/Nano-PDF/raw/main/assets/edited_LinkedIn-Pitch-Deck.-2004.-Series-B-1.pdf)*

**Text remains selectable** - OCR re-hydration preserves the text layer:

![Text selection demo](https://raw.githubusercontent.com/gavrielc/Nano-PDF/main/assets/text-selection-demo.png)

### Convert PDF to PowerPoint

```bash
# Convert entire PDF to editable PowerPoint
nano-pdf toppt presentation.pdf

# Convert specific pages with AI chart extraction
nano-pdf toppt report.pdf --pages "1,3,5-10" --extract-charts

# Quick conversion without AI (faster)
nano-pdf toppt slides.pdf --no-use-ai
```

The converter extracts:
- **Editable text** with preserved fonts and styling
- **Editable charts** with actual data values (bar, line, pie, etc.)
- **Editable tables** with cell formatting
- **Images** in their original positions
- **Shapes** with colors and borders

## How It Works

### PDF Editing

Nano PDF uses Gemini 3 Pro Image (aka Nano Banana) and PDF manipulation to enable quick edits of PDFs with natural language editing:

1. **Page Rendering**: Converts target PDF pages to images using Poppler
2. **Style References**: Optionally includes style reference pages with generation request to understand visual style (fonts, colors, layout)
3. **AI Generation**: Sends images + prompts to Gemini 3 Pro Image, which generates edited versions
4. **OCR Re-hydration**: Uses Tesseract to restore searchable text layer to generated images
5. **PDF Stitching**: Replaces original pages with AI-edited versions while preserving document structure

The tool processes multiple pages in parallel for speed, with configurable resolution (4K/2K/1K) to balance quality vs. cost.

### PDF to PowerPoint Conversion

The PDF to PPT converter uses a multi-stage intelligent extraction pipeline:

1. **PDF Parsing**: Uses PyMuPDF to extract raw elements (text blocks, images, vector drawings)
2. **Element Analysis**: Groups related elements and detects chart/table regions
3. **AI Extraction**: Uses Gemini to analyze page images and extract:
   - Chart data (type, categories, series with actual numerical values)
   - Table structure and content
   - Text hierarchy and styling
4. **PowerPoint Generation**: Creates native PowerPoint elements using python-pptx:
   - Text boxes with matched fonts and colors
   - Native charts with extracted data (fully editable!)
   - Tables with proper formatting
   - Images and shapes
5. **Fallback**: Complex graphics that can't be parsed are preserved as images

See [doc/ARCHITECTURE.md](doc/ARCHITECTURE.md) for detailed technical documentation.

## Installation

### Using pip

```bash
pip install nano-pdf
```

### Using uvx

```bash
uvx nano-pdf edit my_deck.pdf 2 "Your edit here"
```

## Configuration

You need a **paid** Google Gemini API key with billing enabled. Free tier keys do not support image generation.

1. Get an API key from [Google AI Studio](https://aistudio.google.com/api-keys)
2. Enable billing on your Google Cloud project
3. Set your API key as an environment variable:
```bash
export GEMINI_API_KEY="your_api_key_here"
```

**Note:** This tool uses Gemini 3 Pro Image which requires a paid API tier. See [pricing](https://ai.google.dev/pricing) for details.

## Usage

### Basic Edit
Edit a single page (e.g., Page 2):

```bash
nano-pdf edit my_deck.pdf 2 "Change the title to 'Q3 Results'"
```

### Multi-page Edit
Edit multiple pages in one go:

```bash
nano-pdf edit my_deck.pdf \
  1 "Update date to Oct 2025" \
  5 "Add company logo" \
  10 "Fix typo in footer"
```

### Add New Slides
Insert a new AI-generated slide into your deck:

```bash
# Add a title slide at the beginning
nano-pdf add my_deck.pdf 0 "Title slide with 'Q3 2025 Review'"

# Add a slide after page 5
nano-pdf add my_deck.pdf 5 "Summary slide with key takeaways as bullet points"
```

The new slide will automatically match the visual style of your existing slides and uses document context by default for better relevance.

### Convert PDF to PowerPoint

Convert a PDF presentation to an editable PowerPoint file:

```bash
# Basic conversion (all pages)
nano-pdf toppt presentation.pdf

# Convert to specific output file
nano-pdf toppt report.pdf -o my_presentation.pptx

# Convert specific pages
nano-pdf toppt deck.pdf --pages "1,3,5-10"

# Full conversion with all AI features
nano-pdf toppt slides.pdf \
  --extract-charts \
  --extract-tables \
  --resolution 4K

# Fast conversion without AI (basic extraction)
nano-pdf toppt quick.pdf --no-use-ai
```

#### toppt Options

| Option | Default | Description |
|--------|---------|-------------|
| `--output, -o` | `<filename>.pptx` | Output file path |
| `--pages, -p` | All pages | Pages to convert (e.g., "1,3,5-10") |
| `--extract-charts/--no-extract-charts` | Enabled | Extract charts as editable with data |
| `--extract-tables/--no-extract-tables` | Enabled | Extract tables as editable |
| `--preserve-fonts/--no-preserve-fonts` | Enabled | Match original fonts |
| `--use-ai/--no-use-ai` | Enabled | Use AI for element extraction |
| `--resolution, -r` | 4K | AI analysis resolution (4K/2K/1K) |
| `--fallback-to-image/--no-fallback-to-image` | Enabled | Use image if extraction fails |
| `--parallel/--no-parallel` | Enabled | Process pages in parallel |
| `--max-workers` | 5 | Maximum parallel workers (1-10) |

### Analyze a Page

Preview what elements will be extracted:

```bash
# Analyze first page
nano-pdf analyze presentation.pdf

# Analyze specific page
nano-pdf analyze report.pdf --page 5

# Save analysis to JSON
nano-pdf analyze deck.pdf -o analysis.json
```

### Edit Options
*   `--use-context` / `--no-use-context`: Include the full text of the PDF as context for the model. Disabled by default for `edit`, **enabled by default for `add`**. Use `--no-use-context` to disable.
*   `--style-refs "1,5"`: Manually specify which pages to use as style references.
*   `--output "new.pdf"`: Specify the output filename.
*   `--resolution "4K"`: Image resolution - "4K" (default), "2K", or "1K". Higher quality = slower processing.
*   `--disable-google-search`: Prevents the model from using Google Search to find information before generating (enabled by default).

## Examples

### PDF Editing Examples

#### Fixing Presentation Errors
```bash
# Fix typos across multiple slides
nano-pdf edit pitch_deck.pdf \
  3 "Fix the typo 'recieve' to 'receive'" \
  7 "Change 'Q4 2024' to 'Q1 2025'"
```

#### Visual Design Changes
```bash
# Update branding and colors
nano-pdf edit slides.pdf 1 "Make the header background blue and text white" \
  --style-refs "2,3" --output branded_slides.pdf
```

#### Content Updates
```bash
# Update financial data
nano-pdf edit report.pdf 12 "Update the revenue chart to show Q3 at $2.5M instead of $2.1M"
```

### PDF to PowerPoint Examples

#### Convert a Financial Report
```bash
# Convert with chart extraction for editable charts
nano-pdf toppt quarterly_report.pdf \
  --extract-charts \
  --output editable_report.pptx
```

#### Convert Selected Slides
```bash
# Only convert key slides
nano-pdf toppt full_deck.pdf \
  --pages "1,5,10-15,20" \
  -o key_slides.pptx
```

#### Fast Batch Conversion
```bash
# Quick conversion without AI (faster, less accurate)
for f in *.pdf; do
  nano-pdf toppt "$f" --no-use-ai
done
```

## Requirements

*   Python 3.10+
*   `poppler` (for PDF rendering)
*   `tesseract` (for OCR)

### System Dependencies

#### macOS
```bash
brew install poppler tesseract
```

#### Windows
```bash
choco install poppler tesseract
```

**Note:** After installation, you may need to restart your terminal or add the installation directory to your PATH.

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get install poppler-utils tesseract-ocr
```

## Troubleshooting

### "Missing system dependencies" error
Make sure you've installed poppler and tesseract for your platform. After installation, restart your terminal to refresh PATH. Run `which pdftotext` and `which tesseract` to verify they're accessible.

### "GEMINI_API_KEY not found" error
Set your API key as an environment variable:
```bash
export GEMINI_API_KEY="your_key_here"
```

### "Gemini API Error: PAID API key required" error
Gemini 3 Pro Image requires a paid API tier. Visit [Google AI Studio](https://aistudio.google.com/api-keys) to enable billing on your project.

### Generated images don't match the style
Try using `--style-refs` to specify reference pages that have the desired visual style. The model will analyze these pages to better match fonts, colors, and layout.

### Text layer is missing or incorrect after editing
The tool uses Tesseract OCR to restore searchable text. For best results, ensure your generated images are high resolution (`--resolution "4K"`). Note that OCR may not be perfect for stylized fonts or small text.

### Pages are processing slowly
- Use `--resolution "2K"` or `--resolution "1K"` for faster processing

### Chart data not extracted correctly
The AI-powered chart extraction works best with:
- Clear, well-labeled charts
- Standard chart types (bar, column, line, pie)
- Visible axis labels and data values

For complex or stylized charts, they may be preserved as images instead.

## Running from Source

```bash
git clone https://github.com/gavrielc/Nano-PDF.git
cd Nano-PDF

# Install dependencies
uv sync    # or: pip install -e .

# Set up your API key
cp .env.example .env
# Edit .env with your GEMINI_API_KEY

# Run the tool
uv run nano-pdf edit my_deck.pdf 2 "Your edit here"
uv run nano-pdf toppt my_deck.pdf -o converted.pptx
```

## Documentation

- [Architecture Documentation](doc/ARCHITECTURE.md) - Technical details and design decisions
- [API Reference](doc/API.md) - Programmatic usage
- [Contributing Guide](CONTRIBUTING.md) - How to contribute

## License
MIT
