# PDF to PowerPoint Converter Feature

## Overview

The `convert` command transforms PDF presentations into editable PowerPoint files with **exact** font, style, and layout preservation. Charts and graphs are recreated as **editable** PowerPoint charts that you can modify directly.

## Features

### 🎯 Exact Style Preservation
- **Fonts**: Exact font families, sizes, weights, and styles
- **Colors**: Precise RGB color matching
- **Layout**: Pixel-perfect positioning and sizing
- **Text Formatting**: Alignment, line spacing, bullet points

### 📊 Editable Charts & Graphs
- Charts are detected and recreated as native PowerPoint charts
- **Fully editable** - modify data, change chart types, adjust styling
- Supports: Bar, Column, Line, Pie, Area, Scatter, Doughnut, Radar charts
- Preserves chart titles, axis labels, legends, and gridlines

### 🖼️ Complete Element Extraction
- Text elements with exact styling
- Images and logos (with positioning)
- Shapes (rectangles, circles, arrows, lines)
- Background colors and gradients

### 🤖 AI-Powered Analysis
- Uses Gemini AI to analyze PDF structure
- Extracts complete chart data automatically
- Identifies fonts, colors, and layout with high precision
- Falls back to OCR if AI analysis fails

## Usage

### Basic Conversion

```bash
nano-pdf convert deck.pdf
```

This creates `deck.pptx` in the same directory.

### Specify Output File

```bash
nano-pdf convert deck.pdf --output my_presentation.pptx
```

### Options

- `--use-ai` / `--no-use-ai`: Enable/disable AI analysis (default: enabled)
- `--use-context` / `--no-use-context`: Include PDF text as context (default: enabled)
- `--resolution`: Image resolution for analysis ("high", "medium", "low")

### Examples

```bash
# Convert with AI analysis (recommended)
nano-pdf convert quarterly_report.pdf --output q4_report.pptx

# Convert without AI (OCR only, faster but less accurate)
nano-pdf convert simple_deck.pdf --no-use-ai

# High-quality conversion with full context
nano-pdf convert complex_presentation.pdf --output output.pptx --use-context --resolution high
```

## How It Works

1. **Page Rendering**: Each PDF page is rendered as a high-resolution image
2. **AI Analysis**: Gemini AI analyzes the page structure:
   - Extracts text with fonts, sizes, colors, positions
   - Identifies charts and extracts their data
   - Detects images, shapes, and layout elements
   - Analyzes color schemes and styling
3. **PowerPoint Creation**: 
   - Text elements are recreated with exact fonts and styling
   - Charts are built as editable PowerPoint charts with extracted data
   - Images and shapes are positioned accurately
   - Background colors are applied
4. **Output**: A fully editable PowerPoint file with preserved styling

## Chart Data Extraction

The converter intelligently extracts chart data:
- Reads axis labels and values
- Extracts data series and categories
- Preserves chart colors and styling
- Maintains legends and gridlines

Charts in the output PPTX are **fully editable** - you can:
- Modify data values
- Change chart types
- Adjust colors and styling
- Add/remove series
- Customize axes and labels

## Requirements

- Python 3.10+
- `python-pptx` library (automatically installed)
- Gemini API key with billing enabled (for AI analysis)
- System dependencies: `poppler` and `tesseract` (for PDF rendering and OCR)

## Tips for Best Results

1. **High-Quality PDFs**: Better source quality = better conversion
2. **Clear Charts**: Charts with clear labels and readable values convert best
3. **Standard Fonts**: Common fonts (Arial, Times New Roman, Calibri) map better
4. **Use AI Analysis**: Keep `--use-ai` enabled for best accuracy
5. **Review Output**: Always review the converted PPTX and adjust as needed

## Limitations

- Complex vector graphics may be simplified
- Some custom fonts may be mapped to similar standard fonts
- Very complex layouts may require manual adjustment
- Image extraction from PDFs is currently limited (placeholders are created)

## Future Enhancements

- Direct image extraction from PDF
- Better font matching and embedding
- Support for animations and transitions
- Enhanced shape detection and recreation
- Multi-column text layout support
