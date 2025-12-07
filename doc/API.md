# Nano PDF API Reference

This document describes how to use Nano PDF programmatically in your Python code.

## Installation

```bash
pip install nano-pdf
```

## Quick Start

```python
from nano_pdf.ppt_converter import convert_pdf_to_pptx

# Simple conversion
output_path = convert_pdf_to_pptx("presentation.pdf")
print(f"Converted to: {output_path}")
```

---

## PDF to PowerPoint Conversion

### Basic Conversion

```python
from nano_pdf.ppt_converter import convert_pdf_to_pptx

# Convert all pages
convert_pdf_to_pptx("input.pdf", "output.pptx")

# Convert specific pages
convert_pdf_to_pptx("input.pdf", "output.pptx", pages=[1, 3, 5])
```

### With Options

```python
from nano_pdf.ppt_converter import (
    PDFToPPTConverter,
    ConversionOptions
)

# Configure options
options = ConversionOptions(
    extract_charts=True,      # Use AI to extract chart data
    extract_tables=True,      # Extract tables as editable
    preserve_fonts=True,      # Match original fonts
    use_ai_extraction=True,   # Use AI for analysis
    resolution="4K",          # 4K, 2K, or 1K
    fallback_to_image=True,   # Use image if extraction fails
    parallel_processing=True, # Process pages in parallel
    max_workers=5             # Parallel worker count
)

# Create converter
converter = PDFToPPTConverter(options)

# Convert with progress callback
def on_progress(current, total, message):
    print(f"[{current}/{total}] {message}")

converter.convert(
    pdf_path="input.pdf",
    output_path="output.pptx",
    pages=[1, 2, 3],
    progress_callback=on_progress
)
```

### AI-Powered Conversion

```python
from nano_pdf.ppt_converter import convert_pdf_to_pptx_with_ai

# Full AI-powered conversion (best for charts)
convert_pdf_to_pptx_with_ai(
    pdf_path="financial_report.pdf",
    output_path="report.pptx",
    extract_charts=True,
    resolution="4K"
)
```

---

## ConversionOptions

All available options for PDF to PPT conversion:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `extract_charts` | bool | True | Extract charts as editable with data |
| `extract_tables` | bool | True | Extract tables as editable |
| `preserve_fonts` | bool | True | Attempt to match original fonts |
| `use_ai_extraction` | bool | True | Use AI for element detection |
| `resolution` | str | "4K" | Image resolution: "4K", "2K", "1K" |
| `fallback_to_image` | bool | True | Fall back to image on failure |
| `parallel_processing` | bool | True | Process pages in parallel |
| `max_workers` | int | 5 | Maximum parallel workers (1-10) |

---

## AI Utilities

### Chart Detection

```python
from nano_pdf.ai_utils import analyze_page_for_charts
from nano_pdf.pdf_utils import render_page_as_image

# Render a page
page_image = render_page_as_image("document.pdf", page_number=1)

# Analyze for charts
result = analyze_page_for_charts(page_image)

if result["has_charts"]:
    for chart in result["charts"]:
        print(f"Chart type: {chart['type']}")
        print(f"Title: {chart.get('title', 'Untitled')}")
        print(f"Categories: {chart['categories']}")
        for series in chart["series"]:
            print(f"  Series '{series['name']}': {series['values']}")
```

### Layout Analysis

```python
from nano_pdf.ai_utils import analyze_page_layout

# Analyze page layout
layout = analyze_page_layout(page_image)

for element in layout["elements"]:
    print(f"Type: {element['type']}")
    print(f"Position: {element['bounding_box']}")
    if element['type'] == 'text':
        print(f"Content: {element.get('content', '')}")
```

### Table Extraction

```python
from nano_pdf.ai_utils import extract_table_data

# Extract tables
result = extract_table_data(page_image)

for table in result["tables"]:
    print(f"Table: {len(table['rows'])} rows")
    for row in table["rows"]:
        print(row)
```

### Comprehensive Extraction

```python
from nano_pdf.ai_utils import extract_slide_content_comprehensive

# Get all content from a slide
content = extract_slide_content_comprehensive(page_image)

# Access different element types
print(f"Text elements: {len(content.get('text_elements', []))}")
print(f"Charts: {len(content.get('charts', []))}")
print(f"Tables: {len(content.get('tables', []))}")
print(f"Images: {len(content.get('images', []))}")
```

---

## PDF Utilities

### Page Count

```python
from nano_pdf.pdf_utils import get_page_count

total_pages = get_page_count("document.pdf")
print(f"PDF has {total_pages} pages")
```

### Render Page to Image

```python
from nano_pdf.pdf_utils import render_page_as_image

# Get PIL Image of a page
image = render_page_as_image("document.pdf", page_number=1)
image.save("page1.png")
```

### Extract Text

```python
from nano_pdf.pdf_utils import extract_full_text

# Get text with page markers
text = extract_full_text("document.pdf")
print(text)
# Output: <document_context><page-1>...</page-1>...</document_context>
```

---

## PowerPoint Utilities

### Create Presentation Programmatically

```python
from nano_pdf.ppt_utils import (
    SlideContent, SlideLayout, TextBox, TextStyle, TextRun, Paragraph,
    ChartElement, ChartData, ChartType, ChartSeries,
    create_presentation, save_presentation
)

# Create a title slide
title_style = TextStyle(
    font_name="Calibri",
    font_size=44,
    bold=True,
    color="#000000"
)

title_box = TextBox(
    paragraphs=[
        Paragraph(
            runs=[TextRun("My Presentation", title_style)],
            alignment="center"
        )
    ],
    x=0.5, y=3.0, width=12.333, height=1.5
)

slide1 = SlideContent(
    layout=SlideLayout(background_color="#FFFFFF"),
    text_boxes=[title_box]
)

# Create a chart slide
chart_data = ChartData(
    chart_type=ChartType.COLUMN,
    title="Sales by Quarter",
    categories=["Q1", "Q2", "Q3", "Q4"],
    series=[
        ChartSeries(name="2024", values=[100, 150, 120, 180], color="#4472C4"),
        ChartSeries(name="2023", values=[80, 120, 100, 150], color="#ED7D31"),
    ],
    show_legend=True
)

chart_elem = ChartElement(
    data=chart_data,
    x=1.0, y=1.5, width=11.333, height=5.5
)

slide2 = SlideContent(
    layout=SlideLayout(),
    charts=[chart_elem]
)

# Create and save presentation
prs = create_presentation([slide1, slide2])
save_presentation(prs, "my_presentation.pptx")
```

### Helper Functions

```python
from nano_pdf.ppt_utils import (
    create_title_slide,
    create_content_slide,
    create_chart_slide,
    create_image_slide
)

# Quick title slide
slide1 = create_title_slide(
    title="Quarterly Report",
    subtitle="Q4 2024 Financial Summary"
)

# Bullet point slide
slide2 = create_content_slide(
    title="Key Highlights",
    bullet_points=[
        "Revenue up 25% YoY",
        "New market expansion",
        "Improved margins"
    ]
)

# Chart slide
from nano_pdf.ppt_utils import ChartData, ChartType, ChartSeries

chart_data = ChartData(
    chart_type=ChartType.PIE,
    categories=["Product A", "Product B", "Product C"],
    series=[ChartSeries(name="Revenue", values=[45, 35, 20])]
)

slide3 = create_chart_slide("Revenue Distribution", chart_data)

# Create presentation
prs = create_presentation([slide1, slide2, slide3])
save_presentation(prs, "report.pptx")
```

---

## PDF Editing

### Edit Slides with AI

```python
from nano_pdf.ai_utils import generate_edited_slide
from nano_pdf.pdf_utils import render_page_as_image, rehydrate_image_to_pdf

# Render the page
page_image = render_page_as_image("deck.pdf", page_number=1)

# Edit with AI
edited_image, response = generate_edited_slide(
    target_image=page_image,
    style_reference_images=[],
    full_text_context="",
    user_prompt="Change the title to 'Updated Title'",
    resolution="4K"
)

# Save as PDF with OCR
rehydrate_image_to_pdf(edited_image, "edited_page.pdf")
```

### Generate New Slides

```python
from nano_pdf.ai_utils import generate_new_slide

# Get style reference from existing deck
style_image = render_page_as_image("deck.pdf", page_number=1)

# Generate new slide
new_slide, response = generate_new_slide(
    style_reference_images=[style_image],
    user_prompt="Create a slide showing Q4 2024 goals as bullet points",
    resolution="4K"
)

# Save
new_slide.save("new_slide.png")
```

---

## Data Structures Reference

### SlideContent

```python
@dataclass
class SlideContent:
    layout: SlideLayout = field(default_factory=SlideLayout)
    text_boxes: List[TextBox] = field(default_factory=list)
    charts: List[ChartElement] = field(default_factory=list)
    images: List[ImageElement] = field(default_factory=list)
    shapes: List[ShapeElement] = field(default_factory=list)
    tables: List[TableElement] = field(default_factory=list)
    notes: str = ""
```

### ChartData

```python
@dataclass
class ChartData:
    chart_type: ChartType
    title: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    series: List[ChartSeries] = field(default_factory=list)
    x_axis_title: Optional[str] = None
    y_axis_title: Optional[str] = None
    show_legend: bool = True
    legend_position: str = "bottom"
    data_labels: bool = False
    colors: List[str] = field(default_factory=list)
```

### TextStyle

```python
@dataclass
class TextStyle:
    font_name: str = "Calibri"
    font_size: int = 12  # points
    bold: bool = False
    italic: bool = False
    underline: bool = False
    color: str = "#000000"  # hex
    alignment: str = "left"
    vertical_alignment: str = "top"
    line_spacing: float = 1.0
    space_before: float = 0
    space_after: float = 0
```

---

## Error Handling

```python
from nano_pdf.ppt_converter import PDFToPPTConverter, ConversionOptions

try:
    converter = PDFToPPTConverter()
    converter.convert("input.pdf", "output.pptx")
except FileNotFoundError as e:
    print(f"PDF not found: {e}")
except ValueError as e:
    print(f"Invalid input: {e}")
except RuntimeError as e:
    print(f"Conversion failed: {e}")
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Google Gemini API key (required for AI features) |

Set with:
```bash
export GEMINI_API_KEY="your_api_key_here"
```

Or in Python:
```python
import os
os.environ["GEMINI_API_KEY"] = "your_api_key_here"
```

---

## Examples

See the [examples/](../examples/) directory for complete working examples:

- `basic_conversion.py` - Simple PDF to PPT conversion
- `chart_extraction.py` - AI-powered chart extraction
- `programmatic_pptx.py` - Creating presentations from code
- `batch_conversion.py` - Converting multiple files
