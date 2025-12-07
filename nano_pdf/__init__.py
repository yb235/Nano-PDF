"""
Nano PDF - Edit PDFs and convert to PowerPoint using AI

Main modules:
- main: CLI interface
- pdf_utils: PDF manipulation utilities
- ai_utils: Gemini AI integration
- ppt_utils: PowerPoint creation utilities
- ppt_converter: PDF to PowerPoint conversion
"""

__version__ = "0.3.0"

# Convenient imports for programmatic usage
from nano_pdf.ppt_utils import (
    SlideContent,
    SlideLayout,
    TextBox,
    TextStyle,
    TextRun,
    Paragraph,
    ChartElement,
    ChartData,
    ChartType,
    ChartSeries,
    ImageElement,
    ShapeElement,
    TableElement,
    TableCell,
    create_presentation,
    save_presentation,
)

from nano_pdf.ppt_converter import (
    PDFToPPTConverter,
    ConversionOptions,
    convert_pdf_to_pptx,
    convert_pdf_to_pptx_with_ai,
)

__all__ = [
    # Version
    "__version__",
    # Slide content
    "SlideContent",
    "SlideLayout",
    "TextBox",
    "TextStyle",
    "TextRun",
    "Paragraph",
    "ChartElement",
    "ChartData",
    "ChartType",
    "ChartSeries",
    "ImageElement",
    "ShapeElement",
    "TableElement",
    "TableCell",
    # PPT creation
    "create_presentation",
    "save_presentation",
    # Conversion
    "PDFToPPTConverter",
    "ConversionOptions",
    "convert_pdf_to_pptx",
    "convert_pdf_to_pptx_with_ai",
]
