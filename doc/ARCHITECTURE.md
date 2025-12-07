# Nano PDF Architecture

This document provides a comprehensive overview of the Nano PDF architecture, focusing on the PDF to PowerPoint conversion system.

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Module Structure](#module-structure)
4. [PDF to PPT Conversion Pipeline](#pdf-to-ppt-conversion-pipeline)
5. [AI Integration](#ai-integration)
6. [Data Structures](#data-structures)
7. [Conversion Strategies](#conversion-strategies)
8. [Extension Points](#extension-points)

---

## Overview

Nano PDF is a CLI tool that provides two main capabilities:

1. **PDF Editing**: Edit PDF slides using natural language prompts powered by Gemini 3 Pro Image
2. **PDF to PowerPoint Conversion**: Convert PDFs to editable PPTX files with intelligent element extraction

The system is designed with the following principles:

- **AI-First**: Leverage AI for intelligent understanding and extraction
- **Graceful Degradation**: Fall back to simpler methods when AI fails
- **Preservation**: Maintain visual fidelity as much as possible
- **Editability**: Prioritize creating editable elements over static images

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLI Interface                               │
│                              (main.py)                                   │
│                                                                          │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│   │    edit     │  │    add      │  │   toppt     │  │   analyze   │   │
│   └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           Core Modules                                   │
│                                                                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │   pdf_utils.py   │  │   ai_utils.py    │  │ ppt_converter.py │      │
│  │                  │  │                  │  │                  │      │
│  │ - PDF reading    │  │ - Gemini client  │  │ - Conversion     │      │
│  │ - Page rendering │  │ - Image gen      │  │   orchestration  │      │
│  │ - Text extract   │  │ - Chart detect   │  │ - Element        │      │
│  │ - OCR hydration  │  │ - Layout analyze │  │   extraction     │      │
│  │ - PDF stitching  │  │ - Table extract  │  │ - Coordinate     │      │
│  └──────────────────┘  └──────────────────┘  │   mapping        │      │
│                                              └──────────────────┘      │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                        ppt_utils.py                               │   │
│  │                                                                   │   │
│  │  - Slide content data structures (TextBox, Chart, Table, etc.)   │   │
│  │  - PowerPoint creation with python-pptx                          │   │
│  │  - Chart rendering (native Excel-backed charts)                   │   │
│  │  - Shape and styling utilities                                    │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        External Dependencies                             │
│                                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │  PyMuPDF    │  │ python-pptx │  │   Gemini    │  │  Tesseract  │   │
│  │  (fitz)     │  │             │  │   API       │  │   OCR       │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
│                                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                     │
│  │  pdf2image  │  │   Poppler   │  │   Pillow    │                     │
│  └─────────────┘  └─────────────┘  └─────────────┘                     │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Module Structure

### main.py
The CLI entry point using Typer. Provides commands:
- `edit`: Edit PDF pages with AI
- `add`: Add new AI-generated slides
- `toppt`: Convert PDF to PowerPoint
- `analyze`: Analyze page elements
- `version`: Show version info

### pdf_utils.py
PDF manipulation utilities:
- `get_page_count()`: Get PDF page count
- `extract_full_text()`: Extract text with layout preservation
- `render_page_as_image()`: Render page to PIL Image
- `rehydrate_image_to_pdf()`: Add OCR text layer to image
- `batch_replace_pages()`: Replace multiple pages
- `insert_page()`: Insert new page

### ai_utils.py
Gemini AI integration:
- `generate_edited_slide()`: Edit slide with AI image generation
- `generate_new_slide()`: Generate new slide from prompt
- `analyze_page_for_charts()`: Detect and extract chart data
- `analyze_page_layout()`: Identify all page elements
- `extract_table_data()`: Extract table structure and content
- `enhance_slide_extraction()`: Correct OCR and add styling
- `extract_slide_content_comprehensive()`: Full page extraction

### ppt_converter.py
PDF to PPT conversion engine:
- `PDFToPPTConverter`: Main converter class
- `ConversionOptions`: Configuration dataclass
- Element extraction from PDF
- Coordinate transformation (PDF → PPT)
- Page processing pipeline

### ppt_utils.py
PowerPoint creation utilities:
- Data structures: `SlideContent`, `TextBox`, `ChartElement`, `TableElement`, etc.
- `create_presentation()`: Create PPTX from slide content
- Helper functions for creating charts, text, shapes

---

## PDF to PPT Conversion Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     PDF to PowerPoint Pipeline                           │
└─────────────────────────────────────────────────────────────────────────┘

     ┌──────────┐
     │  Input   │
     │   PDF    │
     └────┬─────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Stage 1: PDF PARSING (PyMuPDF)                                          │
│                                                                          │
│ For each page:                                                           │
│   ├── Extract text blocks with font info (name, size, color, bold/ital) │
│   ├── Extract embedded images with positions                            │
│   ├── Extract vector drawings/shapes                                    │
│   └── Detect background color                                           │
│                                                                          │
│ Output: PDFPageElements (raw PDF content)                               │
└─────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Stage 2: PAGE RENDERING                                                  │
│                                                                          │
│ Render page as high-resolution image for AI analysis                    │
│   ├── pdf2image / Poppler for accurate rendering                        │
│   └── Resolution: 4K (3840px), 2K (1920px), or 1K (1024px)             │
│                                                                          │
│ Output: PIL Image                                                        │
└─────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Stage 3: AI ANALYSIS (Gemini)                                           │
│                                                                          │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │ Chart Detection & Extraction                                        │ │
│ │                                                                     │ │
│ │ AI analyzes image to:                                               │ │
│ │   ├── Detect chart type (bar, column, line, pie, scatter, etc.)   │ │
│ │   ├── Extract categories/labels                                    │ │
│ │   ├── Extract data series with ACTUAL values                      │ │
│ │   ├── Identify colors, axis titles, legend position               │ │
│ │   └── Determine bounding box position                              │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │ Layout Analysis (Optional)                                          │ │
│ │                                                                     │ │
│ │   ├── Identify element types (text, image, chart, table, shape)   │ │
│ │   ├── Determine element positions and sizes                       │ │
│ │   └── Detect hierarchy (title, subtitle, body, bullet)            │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│ Output: Chart data, element positions, enhanced text                    │
└─────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Stage 4: ELEMENT PROCESSING                                             │
│                                                                          │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │ Text Block Grouping                                                 │ │
│ │                                                                     │ │
│ │ Group related text blocks into logical text boxes:                 │ │
│ │   ├── Spatial proximity analysis                                   │ │
│ │   ├── Style similarity (font, size, color)                        │ │
│ │   └── Vertical/horizontal alignment                                │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │ Coordinate Transformation                                           │ │
│ │                                                                     │ │
│ │ Convert PDF coordinates to PowerPoint:                             │ │
│ │   ├── PDF: points (72 dpi), origin at bottom-left                 │ │
│ │   ├── PPT: inches, origin at top-left                             │ │
│ │   └── Scale to maintain aspect ratio                               │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │ Font Normalization                                                  │ │
│ │                                                                     │ │
│ │ Map PDF font names to common PowerPoint fonts:                     │ │
│ │   ├── "ArialMT" → "Arial"                                         │ │
│ │   ├── "Helvetica" → "Arial"                                       │ │
│ │   ├── "TimesNewRomanPSMT" → "Times New Roman"                     │ │
│ │   └── Unknown fonts → "Calibri" (default)                         │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│ Output: SlideContent (structured slide representation)                  │
└─────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Stage 5: POWERPOINT GENERATION (python-pptx)                            │
│                                                                          │
│ Create native PowerPoint elements:                                       │
│                                                                          │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │ Text Boxes                                                          │ │
│ │   ├── Set position and size                                        │ │
│ │   ├── Apply font styling (name, size, bold, italic, color)        │ │
│ │   ├── Set paragraph alignment                                      │ │
│ │   └── Handle multi-paragraph content                               │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │ Charts (Native Excel-backed)                                        │ │
│ │                                                                     │ │
│ │   ├── Create CategoryChartData with extracted values              │ │
│ │   ├── Add series with names and data points                       │ │
│ │   ├── Apply colors to series                                       │ │
│ │   ├── Configure axis titles and labels                             │ │
│ │   └── Position legend                                              │ │
│ │                                                                     │ │
│ │ Result: Fully editable chart with real data!                       │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │ Tables                                                              │ │
│ │   ├── Create table with correct rows/columns                       │ │
│ │   ├── Fill cell contents                                           │ │
│ │   ├── Apply cell styling (background, font, alignment)            │ │
│ │   └── Handle header rows                                           │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │ Images & Shapes                                                     │ │
│ │   ├── Add images at correct positions                              │ │
│ │   ├── Create auto shapes (rectangles, ovals, arrows)              │ │
│ │   └── Apply fill and border colors                                 │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│ Output: PowerPoint Presentation object                                  │
└─────────────────────────────────────────────────────────────────────────┘
          │
          ▼
     ┌──────────┐
     │  Output  │
     │  .pptx   │
     └──────────┘
```

---

## AI Integration

### Gemini Models Used

| Task | Model | Purpose |
|------|-------|---------|
| Image Generation | `gemini-3-pro-image-preview` | Generate/edit slide images |
| Chart Analysis | `gemini-2.5-flash-preview-05-20` | Extract chart data and layout |
| Layout Analysis | `gemini-2.5-flash-preview-05-20` | Identify page elements |
| Table Extraction | `gemini-2.5-flash-preview-05-20` | Extract table structure |

### AI Prompting Strategy

For chart extraction, we use structured prompts that:

1. **Specify exact output format** (JSON schema)
2. **Request actual values** (not placeholders)
3. **Include validation hints** (check axis scales)
4. **Handle edge cases** (no charts, partial data)

Example prompt structure:
```
Analyze this image... extract:
1. Chart type
2. Categories/labels
3. Data series with ACTUAL values
...
Return as JSON: { "charts": [...] }
```

### Error Handling

The AI integration includes:
- API error classification (quota, auth, general)
- Graceful fallback to image-based slides
- JSON parsing with multiple regex patterns
- Timeout handling for long operations

---

## Data Structures

### Slide Content Model

```
SlideContent
├── layout: SlideLayout
│   ├── width: float (inches)
│   ├── height: float (inches)
│   ├── background_color: Optional[str]
│   └── background_image: Optional[bytes]
│
├── text_boxes: List[TextBox]
│   └── TextBox
│       ├── paragraphs: List[Paragraph]
│       │   └── Paragraph
│       │       ├── runs: List[TextRun]
│       │       │   └── TextRun
│       │       │       ├── text: str
│       │       │       └── style: TextStyle
│       │       ├── alignment: str
│       │       └── bullet: bool
│       ├── x, y, width, height: float
│       └── background_color, border_color, etc.
│
├── charts: List[ChartElement]
│   └── ChartElement
│       ├── data: ChartData
│       │   ├── chart_type: ChartType (enum)
│       │   ├── title: Optional[str]
│       │   ├── categories: List[str]
│       │   ├── series: List[ChartSeries]
│       │   │   └── ChartSeries
│       │   │       ├── name: str
│       │   │       ├── values: List[float]
│       │   │       └── color: Optional[str]
│       │   ├── x_axis_title, y_axis_title
│       │   └── legend settings
│       └── x, y, width, height: float
│
├── images: List[ImageElement]
│   └── ImageElement
│       ├── image_data: bytes
│       ├── x, y, width, height: float
│       └── alt_text, rotation, crop settings
│
├── shapes: List[ShapeElement]
│   └── ShapeElement
│       ├── shape_type: str
│       ├── x, y, width, height: float
│       ├── fill_color, border_color
│       └── text: Optional[str]
│
├── tables: List[TableElement]
│   └── TableElement
│       ├── rows: List[List[TableCell]]
│       ├── x, y, width, height: float
│       └── header settings, colors
│
└── notes: str
```

### Chart Types Supported

```python
class ChartType(Enum):
    BAR = "bar"
    COLUMN = "column"
    LINE = "line"
    PIE = "pie"
    DONUT = "donut"
    AREA = "area"
    SCATTER = "scatter"
    BUBBLE = "bubble"
    STACKED_BAR = "stacked_bar"
    STACKED_COLUMN = "stacked_column"
    CLUSTERED_BAR = "clustered_bar"
    CLUSTERED_COLUMN = "clustered_column"
    WATERFALL = "waterfall"
    COMBO = "combo"
```

---

## Conversion Strategies

### Strategy 1: Full AI Extraction (Default)

Best for: Slides with charts, tables, or complex layouts

```
PDF → Render Image → AI Analysis → Native Elements → PPTX
```

Pros:
- Creates fully editable charts with data
- Understands visual context
- Can extract from complex graphics

Cons:
- Slower (API calls)
- Requires paid API key
- May misinterpret unusual designs

### Strategy 2: PDF Parsing Only

Best for: Text-heavy documents, fast conversion

```
PDF → PyMuPDF Extraction → Native Elements → PPTX
```

Pros:
- Fast (no API calls)
- Accurate for text
- Works offline

Cons:
- Charts become images
- Complex layouts may break
- Less accurate positioning

### Strategy 3: Hybrid (Recommended)

Best for: Most presentations

```
PDF → PyMuPDF + AI (for charts) → Native Elements + Image Fallback → PPTX
```

Pros:
- Best balance of speed and quality
- Charts are editable
- Complex graphics preserved as images

Cons:
- Still requires API for charts
- Slightly slower than PDF-only

### Strategy 4: Image Fallback

Best for: Complex designs, exact preservation

```
PDF → Render Image → Image on Slide → PPTX
```

Pros:
- Perfect visual fidelity
- Works with any content
- No extraction errors

Cons:
- Not editable
- Larger file sizes
- No searchable text

---

## Extension Points

### Adding New Chart Types

1. Add type to `ChartType` enum in `ppt_utils.py`
2. Add mapping in `_get_chart_type()` function
3. Update AI prompt in `analyze_page_for_charts()`
4. Handle special data structure if needed

### Adding New Shape Types

1. Add mapping in `_get_auto_shape_type()` in `ppt_utils.py`
2. Shape types are mapped to `MSO_AUTO_SHAPE_TYPE` constants

### Custom Element Extractors

Implement a custom extractor:

```python
def extract_custom_element(page_image: Image.Image) -> List[CustomElement]:
    # Use AI or rule-based extraction
    # Return list of custom element data
    pass
```

### Adding New Output Formats

The `SlideContent` data model is format-agnostic. To add a new output format:

1. Create a new generator module (e.g., `keynote_utils.py`)
2. Implement `create_presentation(slides_content: List[SlideContent])`
3. Map the abstract elements to format-specific constructs

---

## Performance Considerations

### Parallel Processing

Pages are processed in parallel with configurable worker count:

```python
options = ConversionOptions(
    parallel_processing=True,
    max_workers=5  # Adjust based on API rate limits
)
```

### Memory Management

- Images are processed one at a time
- Temporary files are cleaned up after use
- Large PDFs should be processed in batches

### API Rate Limits

- Chart extraction uses Gemini Flash (faster, cheaper)
- Image generation uses Gemini Pro Image
- Consider adding delays for large conversions

---

## Security Considerations

- API keys should be stored in environment variables
- Temporary files are created securely
- No data is persisted beyond the conversion
- User content is sent to Google's Gemini API

---

## Future Enhancements

Planned improvements:

1. **Smart Templates**: Detect and apply PowerPoint templates
2. **Animation Preservation**: Detect animated elements
3. **Master Slides**: Create proper slide masters
4. **Batch API**: Use Gemini batch API for large conversions
5. **Local LLM**: Support for local models (Ollama, etc.)
6. **More Formats**: Export to Google Slides, Keynote

---

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development setup and guidelines.
