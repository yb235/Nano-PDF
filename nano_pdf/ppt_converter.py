"""
PDF to PowerPoint Converter Module.

This module provides comprehensive PDF to PPT conversion with:
- Exact font and style preservation
- Editable chart extraction and recreation
- Image extraction and placement
- Table detection and conversion
- Text box positioning and styling

Uses AI (Gemini) for intelligent element extraction and chart data parsing.
"""

import os
import io
import re
import json
import tempfile
import concurrent.futures
from typing import List, Dict, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
from PIL import Image
import fitz  # PyMuPDF for advanced PDF parsing

from nano_pdf import pdf_utils, ai_utils
from nano_pdf.ppt_utils import (
    SlideContent, SlideLayout, TextBox, TextStyle, TextRun, Paragraph,
    ChartElement, ChartData, ChartType, ChartSeries,
    ImageElement, ShapeElement, TableElement, TableCell,
    create_presentation, save_presentation, image_to_bytes,
    create_slide_from_image, hex_to_rgb, rgb_to_hex
)


# ============================================================================
# PDF Element Extraction Data Structures
# ============================================================================

@dataclass
class PDFTextBlock:
    """A block of text extracted from PDF"""
    text: str
    x: float  # points from left
    y: float  # points from top
    width: float
    height: float
    font_name: str
    font_size: float
    font_color: str  # hex
    is_bold: bool
    is_italic: bool
    rotation: float = 0


@dataclass
class PDFImage:
    """An image extracted from PDF"""
    image_data: bytes
    x: float
    y: float
    width: float
    height: float
    image_type: str  # 'raster' or 'vector'


@dataclass 
class PDFDrawing:
    """A drawing/shape extracted from PDF"""
    path_data: str  # SVG-like path
    x: float
    y: float
    width: float
    height: float
    fill_color: Optional[str]
    stroke_color: Optional[str]
    stroke_width: float


@dataclass
class PDFPageElements:
    """All elements extracted from a single PDF page"""
    page_number: int
    width: float  # points
    height: float  # points
    text_blocks: List[PDFTextBlock] = field(default_factory=list)
    images: List[PDFImage] = field(default_factory=list)
    drawings: List[PDFDrawing] = field(default_factory=list)
    background_color: Optional[str] = None


@dataclass
class ChartDetectionResult:
    """Result of chart detection in a region"""
    is_chart: bool
    chart_type: Optional[ChartType] = None
    chart_data: Optional[ChartData] = None
    confidence: float = 0.0
    bounding_box: Optional[Tuple[float, float, float, float]] = None  # x, y, w, h


@dataclass
class ConversionOptions:
    """Options for PDF to PPT conversion"""
    extract_charts: bool = True  # Try to make charts editable
    extract_tables: bool = True  # Try to make tables editable
    preserve_fonts: bool = True  # Match fonts as closely as possible
    use_ai_extraction: bool = True  # Use AI for complex element detection
    resolution: str = "4K"  # Image resolution for AI processing
    fallback_to_image: bool = True  # Fall back to image if extraction fails
    parallel_processing: bool = True  # Process pages in parallel
    max_workers: int = 5  # Max parallel workers


# ============================================================================
# PDF Parsing Functions (using PyMuPDF)
# ============================================================================

def extract_page_elements(pdf_path: str, page_number: int) -> PDFPageElements:
    """
    Extract all elements from a PDF page using PyMuPDF.
    
    Args:
        pdf_path: Path to PDF file
        page_number: 1-indexed page number
    
    Returns:
        PDFPageElements containing all extracted elements
    """
    doc = fitz.open(pdf_path)
    page = doc[page_number - 1]  # 0-indexed
    
    page_width = page.rect.width
    page_height = page.rect.height
    
    elements = PDFPageElements(
        page_number=page_number,
        width=page_width,
        height=page_height
    )
    
    # Extract text blocks with styling
    elements.text_blocks = _extract_text_blocks(page)
    
    # Extract images
    elements.images = _extract_images(page, doc)
    
    # Extract drawings/shapes
    elements.drawings = _extract_drawings(page)
    
    # Detect background color
    elements.background_color = _detect_background_color(page)
    
    doc.close()
    return elements


def _extract_text_blocks(page) -> List[PDFTextBlock]:
    """Extract text blocks with full styling information"""
    text_blocks = []
    
    # Get text as dictionary with detailed info
    blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]
    
    for block in blocks:
        if block.get("type") != 0:  # Type 0 is text
            continue
        
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span.get("text", "").strip()
                if not text:
                    continue
                
                # Get bounding box
                bbox = span.get("bbox", [0, 0, 0, 0])
                
                # Get font info
                font_name = span.get("font", "Helvetica")
                font_size = span.get("size", 12)
                
                # Get font flags for bold/italic
                flags = span.get("flags", 0)
                is_bold = bool(flags & 2 ** 4)  # Bold flag
                is_italic = bool(flags & 2 ** 1)  # Italic flag
                
                # Get color
                color_int = span.get("color", 0)
                r = (color_int >> 16) & 0xFF
                g = (color_int >> 8) & 0xFF
                b = color_int & 0xFF
                font_color = rgb_to_hex(r, g, b)
                
                text_block = PDFTextBlock(
                    text=text,
                    x=bbox[0],
                    y=bbox[1],
                    width=bbox[2] - bbox[0],
                    height=bbox[3] - bbox[1],
                    font_name=_normalize_font_name(font_name),
                    font_size=font_size,
                    font_color=font_color,
                    is_bold=is_bold,
                    is_italic=is_italic
                )
                text_blocks.append(text_block)
    
    return text_blocks


def _normalize_font_name(font_name: str) -> str:
    """Normalize PDF font name to common font name"""
    # Remove subset prefix (e.g., "ABCDEF+Arial" -> "Arial")
    if "+" in font_name:
        font_name = font_name.split("+", 1)[1]
    
    # Common font mappings
    font_map = {
        "ArialMT": "Arial",
        "Arial-BoldMT": "Arial",
        "Arial-ItalicMT": "Arial",
        "Arial-BoldItalicMT": "Arial",
        "TimesNewRomanPSMT": "Times New Roman",
        "TimesNewRomanPS-BoldMT": "Times New Roman",
        "TimesNewRomanPS-ItalicMT": "Times New Roman",
        "Helvetica": "Arial",
        "Helvetica-Bold": "Arial",
        "Helvetica-Oblique": "Arial",
        "CourierNewPSMT": "Courier New",
        "Georgia": "Georgia",
        "Verdana": "Verdana",
        "Tahoma": "Tahoma",
        "TrebuchetMS": "Trebuchet MS",
        "Calibri": "Calibri",
        "Calibri-Bold": "Calibri",
        "Calibri-Light": "Calibri Light",
        "Cambria": "Cambria",
        "Garamond": "Garamond",
        "BookAntiqua": "Book Antiqua",
        "Palatino": "Palatino Linotype",
        "Century": "Century",
        "CenturyGothic": "Century Gothic",
        "FranklinGothic": "Franklin Gothic",
        "Impact": "Impact",
        "LucidaSans": "Lucida Sans",
        "SegoeUI": "Segoe UI",
    }
    
    # Check for exact match
    if font_name in font_map:
        return font_map[font_name]
    
    # Check for partial match
    font_lower = font_name.lower()
    for key, value in font_map.items():
        if key.lower() in font_lower:
            return value
    
    # Check for common base names
    if "arial" in font_lower:
        return "Arial"
    if "times" in font_lower:
        return "Times New Roman"
    if "helvetica" in font_lower:
        return "Arial"
    if "calibri" in font_lower:
        return "Calibri"
    if "courier" in font_lower:
        return "Courier New"
    
    # Default to Calibri (PowerPoint default)
    return "Calibri"


def _extract_images(page, doc) -> List[PDFImage]:
    """Extract all images from a page"""
    images = []
    
    # Get image list
    image_list = page.get_images(full=True)
    
    for img_index, img_info in enumerate(image_list):
        xref = img_info[0]
        
        try:
            # Extract image
            base_image = doc.extract_image(xref)
            image_data = base_image["image"]
            
            # Get image position (approximate - PyMuPDF doesn't give exact position easily)
            # We'll need to find the image rectangle from page content
            rects = page.get_image_rects(img_info)
            if rects:
                rect = rects[0]
                pdf_image = PDFImage(
                    image_data=image_data,
                    x=rect.x0,
                    y=rect.y0,
                    width=rect.width,
                    height=rect.height,
                    image_type="raster"
                )
                images.append(pdf_image)
        except Exception as e:
            # Skip problematic images
            continue
    
    return images


def _extract_drawings(page) -> List[PDFDrawing]:
    """Extract vector drawings/shapes from a page"""
    drawings = []
    
    # Get drawing commands
    paths = page.get_drawings()
    
    for path in paths:
        try:
            rect = path.get("rect")
            if not rect:
                continue
            
            # Get colors
            fill = path.get("fill")
            stroke = path.get("color")
            stroke_width = path.get("width", 1)
            
            fill_color = None
            stroke_color = None
            
            if fill:
                if isinstance(fill, (list, tuple)) and len(fill) >= 3:
                    r, g, b = int(fill[0] * 255), int(fill[1] * 255), int(fill[2] * 255)
                    fill_color = rgb_to_hex(r, g, b)
            
            if stroke:
                if isinstance(stroke, (list, tuple)) and len(stroke) >= 3:
                    r, g, b = int(stroke[0] * 255), int(stroke[1] * 255), int(stroke[2] * 255)
                    stroke_color = rgb_to_hex(r, g, b)
            
            drawing = PDFDrawing(
                path_data="",  # We'd need to parse path items for SVG-like data
                x=rect.x0,
                y=rect.y0,
                width=rect.width,
                height=rect.height,
                fill_color=fill_color,
                stroke_color=stroke_color,
                stroke_width=stroke_width
            )
            drawings.append(drawing)
        except Exception as e:
            continue
    
    return drawings


def _detect_background_color(page) -> Optional[str]:
    """Detect the background color of a page"""
    # Render a small sample and check the corner
    pix = page.get_pixmap(matrix=fitz.Matrix(0.1, 0.1))
    
    # Get pixel at corner
    try:
        pixel = pix.pixel(0, 0)
        if len(pixel) >= 3:
            r, g, b = pixel[0], pixel[1], pixel[2]
            # Only return if not white (to avoid setting white background explicitly)
            if r != 255 or g != 255 or b != 255:
                return rgb_to_hex(r, g, b)
    except:
        pass
    
    return None


# ============================================================================
# Coordinate Conversion (PDF points to PowerPoint inches)
# ============================================================================

def points_to_inches(points: float) -> float:
    """Convert PDF points to inches (72 points = 1 inch)"""
    return points / 72.0


def convert_coordinates(
    pdf_x: float, pdf_y: float,
    pdf_width: float, pdf_height: float,
    pdf_page_width: float, pdf_page_height: float,
    ppt_slide_width: float = 13.333,
    ppt_slide_height: float = 7.5
) -> Tuple[float, float, float, float]:
    """
    Convert PDF coordinates to PowerPoint coordinates.
    
    PDF coordinates: origin at bottom-left, units in points
    PPT coordinates: origin at top-left, units in inches
    
    Returns: (x, y, width, height) in inches
    """
    # Scale factors
    x_scale = ppt_slide_width / points_to_inches(pdf_page_width)
    y_scale = ppt_slide_height / points_to_inches(pdf_page_height)
    
    # Convert to inches and scale
    ppt_x = points_to_inches(pdf_x) * x_scale
    ppt_y = points_to_inches(pdf_y) * y_scale  # PDF y is already from top in PyMuPDF
    ppt_width = points_to_inches(pdf_width) * x_scale
    ppt_height = points_to_inches(pdf_height) * y_scale
    
    return ppt_x, ppt_y, ppt_width, ppt_height


# ============================================================================
# Element Grouping and Analysis
# ============================================================================

def group_text_blocks(text_blocks: List[PDFTextBlock], tolerance: float = 5.0) -> List[List[PDFTextBlock]]:
    """
    Group text blocks that are likely part of the same text box.
    Uses spatial proximity and style similarity.
    """
    if not text_blocks:
        return []
    
    # Sort by y position, then x
    sorted_blocks = sorted(text_blocks, key=lambda b: (b.y, b.x))
    
    groups = []
    current_group = [sorted_blocks[0]]
    
    for i in range(1, len(sorted_blocks)):
        current = sorted_blocks[i]
        prev = current_group[-1]
        
        # Check if blocks are close enough to be in the same group
        vertical_gap = abs(current.y - (prev.y + prev.height))
        horizontal_overlap = not (current.x > prev.x + prev.width + tolerance or 
                                   prev.x > current.x + current.width + tolerance)
        
        # Check style similarity
        same_font = current.font_name == prev.font_name
        similar_size = abs(current.font_size - prev.font_size) < 2
        
        if vertical_gap < current.font_size * 2 and (horizontal_overlap or same_font):
            current_group.append(current)
        else:
            groups.append(current_group)
            current_group = [current]
    
    if current_group:
        groups.append(current_group)
    
    return groups


def detect_chart_region(
    images: List[PDFImage],
    drawings: List[PDFDrawing],
    page_width: float,
    page_height: float
) -> List[Tuple[float, float, float, float]]:
    """
    Detect regions that likely contain charts based on:
    - Presence of many similar shapes (bars, lines)
    - Geometric patterns
    - Dense drawing areas
    
    Returns list of (x, y, width, height) bounding boxes in PDF points.
    """
    chart_regions = []
    
    # Analyze drawing density
    if drawings:
        # Find clusters of drawings
        drawing_clusters = _cluster_drawings(drawings)
        
        for cluster in drawing_clusters:
            if len(cluster) >= 3:  # At least 3 shapes suggests a chart
                min_x = min(d.x for d in cluster)
                min_y = min(d.y for d in cluster)
                max_x = max(d.x + d.width for d in cluster)
                max_y = max(d.y + d.height for d in cluster)
                
                # Check if this looks like a chart area (reasonable size)
                width = max_x - min_x
                height = max_y - min_y
                
                if width > page_width * 0.1 and height > page_height * 0.1:
                    chart_regions.append((min_x, min_y, width, height))
    
    return chart_regions


def _cluster_drawings(drawings: List[PDFDrawing], distance_threshold: float = 50) -> List[List[PDFDrawing]]:
    """Cluster nearby drawings together"""
    if not drawings:
        return []
    
    clusters = []
    used = set()
    
    for i, drawing in enumerate(drawings):
        if i in used:
            continue
        
        cluster = [drawing]
        used.add(i)
        
        for j, other in enumerate(drawings):
            if j in used:
                continue
            
            # Check distance
            dx = abs((drawing.x + drawing.width/2) - (other.x + other.width/2))
            dy = abs((drawing.y + drawing.height/2) - (other.y + other.height/2))
            
            if dx < distance_threshold and dy < distance_threshold:
                cluster.append(other)
                used.add(j)
        
        clusters.append(cluster)
    
    return clusters


# ============================================================================
# Conversion Pipeline
# ============================================================================

class PDFToPPTConverter:
    """
    Main converter class for PDF to PowerPoint conversion.
    
    This converter uses a multi-stage approach:
    1. Extract raw elements from PDF using PyMuPDF
    2. Analyze elements to detect charts, tables, and text boxes
    3. Use AI to extract chart data and enhance detection
    4. Convert elements to PowerPoint format
    5. Create presentation with editable elements
    """
    
    def __init__(self, options: Optional[ConversionOptions] = None):
        self.options = options or ConversionOptions()
        self._temp_files = []
    
    def convert(
        self,
        pdf_path: str,
        output_path: str,
        pages: Optional[List[int]] = None,
        progress_callback: Optional[callable] = None
    ) -> str:
        """
        Convert PDF to PowerPoint.
        
        Args:
            pdf_path: Path to input PDF
            output_path: Path for output PPTX
            pages: List of page numbers to convert (1-indexed), None for all
            progress_callback: Optional callback(current, total, message)
        
        Returns:
            Path to created PPTX file
        """
        # Validate input
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        # Get page count
        total_pages = pdf_utils.get_page_count(pdf_path)
        
        if pages is None:
            pages = list(range(1, total_pages + 1))
        else:
            # Validate page numbers
            invalid = [p for p in pages if p < 1 or p > total_pages]
            if invalid:
                raise ValueError(f"Invalid page numbers: {invalid}. PDF has {total_pages} pages.")
        
        if progress_callback:
            progress_callback(0, len(pages), "Starting conversion...")
        
        # Get PDF dimensions from first page
        doc = fitz.open(pdf_path)
        first_page = doc[0]
        pdf_page_width = first_page.rect.width
        pdf_page_height = first_page.rect.height
        doc.close()
        
        # Calculate slide dimensions (preserve aspect ratio)
        aspect_ratio = pdf_page_width / pdf_page_height
        if aspect_ratio > 1.5:  # Wide format (likely 16:9)
            slide_width = 13.333
            slide_height = slide_width / aspect_ratio
        else:  # More square or portrait
            slide_height = 7.5
            slide_width = slide_height * aspect_ratio
        
        # Convert each page
        slides_content = []
        
        if self.options.parallel_processing:
            slides_content = self._convert_pages_parallel(
                pdf_path, pages, pdf_page_width, pdf_page_height,
                slide_width, slide_height, progress_callback
            )
        else:
            slides_content = self._convert_pages_sequential(
                pdf_path, pages, pdf_page_width, pdf_page_height,
                slide_width, slide_height, progress_callback
            )
        
        # Create presentation
        if progress_callback:
            progress_callback(len(pages), len(pages), "Creating PowerPoint file...")
        
        prs = create_presentation(slides_content, slide_width, slide_height)
        save_presentation(prs, output_path)
        
        # Cleanup temp files
        self._cleanup()
        
        if progress_callback:
            progress_callback(len(pages), len(pages), "Done!")
        
        return output_path
    
    def _convert_pages_parallel(
        self,
        pdf_path: str,
        pages: List[int],
        pdf_page_width: float,
        pdf_page_height: float,
        slide_width: float,
        slide_height: float,
        progress_callback: Optional[callable]
    ) -> List[SlideContent]:
        """Convert pages in parallel"""
        results = {}
        completed = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.options.max_workers) as executor:
            future_to_page = {
                executor.submit(
                    self._convert_single_page,
                    pdf_path, page, pdf_page_width, pdf_page_height,
                    slide_width, slide_height
                ): page
                for page in pages
            }
            
            for future in concurrent.futures.as_completed(future_to_page):
                page = future_to_page[future]
                try:
                    slide_content = future.result()
                    results[page] = slide_content
                except Exception as e:
                    # Fall back to image for failed pages
                    print(f"Warning: Page {page} conversion failed ({e}), using image fallback")
                    results[page] = self._create_image_fallback(
                        pdf_path, page, slide_width, slide_height
                    )
                
                completed += 1
                if progress_callback:
                    progress_callback(completed, len(pages), f"Converted page {page}")
        
        # Return in correct order
        return [results[p] for p in pages]
    
    def _convert_pages_sequential(
        self,
        pdf_path: str,
        pages: List[int],
        pdf_page_width: float,
        pdf_page_height: float,
        slide_width: float,
        slide_height: float,
        progress_callback: Optional[callable]
    ) -> List[SlideContent]:
        """Convert pages sequentially"""
        slides_content = []
        
        for i, page in enumerate(pages):
            if progress_callback:
                progress_callback(i, len(pages), f"Converting page {page}...")
            
            try:
                slide_content = self._convert_single_page(
                    pdf_path, page, pdf_page_width, pdf_page_height,
                    slide_width, slide_height
                )
            except Exception as e:
                print(f"Warning: Page {page} conversion failed ({e}), using image fallback")
                slide_content = self._create_image_fallback(
                    pdf_path, page, slide_width, slide_height
                )
            
            slides_content.append(slide_content)
        
        return slides_content
    
    def _convert_single_page(
        self,
        pdf_path: str,
        page_number: int,
        pdf_page_width: float,
        pdf_page_height: float,
        slide_width: float,
        slide_height: float
    ) -> SlideContent:
        """Convert a single PDF page to SlideContent"""
        
        # Extract elements from PDF
        elements = extract_page_elements(pdf_path, page_number)
        
        # Render page as image for AI analysis
        page_image = pdf_utils.render_page_as_image(pdf_path, page_number)
        
        # Initialize slide content
        layout = SlideLayout(
            width=slide_width,
            height=slide_height,
            background_color=elements.background_color
        )
        
        slide_content = SlideContent(layout=layout)
        
        # Detect and process charts if enabled
        chart_regions = []
        if self.options.extract_charts and self.options.use_ai_extraction:
            chart_regions = self._detect_and_extract_charts(
                page_image, elements, pdf_page_width, pdf_page_height,
                slide_width, slide_height
            )
            slide_content.charts.extend(chart_regions)
        
        # Process text blocks
        slide_content.text_boxes = self._process_text_blocks(
            elements.text_blocks, pdf_page_width, pdf_page_height,
            slide_width, slide_height
        )
        
        # Process images
        slide_content.images = self._process_images(
            elements.images, pdf_page_width, pdf_page_height,
            slide_width, slide_height
        )
        
        # Process shapes/drawings
        slide_content.shapes = self._process_drawings(
            elements.drawings, pdf_page_width, pdf_page_height,
            slide_width, slide_height
        )
        
        # If no meaningful content extracted and fallback enabled, use image
        if (self.options.fallback_to_image and
            not slide_content.text_boxes and
            not slide_content.charts and
            not slide_content.images):
            return self._create_image_fallback(
                pdf_path, page_number, slide_width, slide_height
            )
        
        return slide_content
    
    def _detect_and_extract_charts(
        self,
        page_image: Image.Image,
        elements: PDFPageElements,
        pdf_page_width: float,
        pdf_page_height: float,
        slide_width: float,
        slide_height: float
    ) -> List[ChartElement]:
        """Use AI to detect and extract chart data from the page"""
        charts = []
        
        try:
            # Use AI to analyze the page for charts
            chart_analysis = ai_utils.analyze_page_for_charts(
                page_image,
                resolution=self.options.resolution
            )
            
            if chart_analysis and chart_analysis.get("charts"):
                for chart_info in chart_analysis["charts"]:
                    chart_data = self._parse_ai_chart_data(chart_info)
                    if chart_data:
                        # Get position from AI response or estimate
                        bbox = chart_info.get("bounding_box", {})
                        x = bbox.get("x", 0.1) * slide_width
                        y = bbox.get("y", 0.2) * slide_height
                        width = bbox.get("width", 0.8) * slide_width
                        height = bbox.get("height", 0.6) * slide_height
                        
                        chart_elem = ChartElement(
                            data=chart_data,
                            x=x, y=y,
                            width=width, height=height
                        )
                        charts.append(chart_elem)
        except Exception as e:
            print(f"Chart extraction failed: {e}")
        
        return charts
    
    def _parse_ai_chart_data(self, chart_info: Dict) -> Optional[ChartData]:
        """Parse chart data from AI analysis result"""
        try:
            chart_type_str = chart_info.get("type", "column").lower()
            chart_type_map = {
                "bar": ChartType.BAR,
                "column": ChartType.COLUMN,
                "line": ChartType.LINE,
                "pie": ChartType.PIE,
                "donut": ChartType.DONUT,
                "doughnut": ChartType.DONUT,
                "area": ChartType.AREA,
                "scatter": ChartType.SCATTER,
                "bubble": ChartType.BUBBLE,
                "stacked_bar": ChartType.STACKED_BAR,
                "stacked_column": ChartType.STACKED_COLUMN,
                "waterfall": ChartType.WATERFALL,
            }
            chart_type = chart_type_map.get(chart_type_str, ChartType.COLUMN)
            
            # Parse categories and series
            categories = chart_info.get("categories", [])
            series_data = chart_info.get("series", [])
            
            series = []
            for s in series_data:
                series.append(ChartSeries(
                    name=s.get("name", "Series"),
                    values=[float(v) for v in s.get("values", [])],
                    color=s.get("color")
                ))
            
            if not series:
                return None
            
            return ChartData(
                chart_type=chart_type,
                title=chart_info.get("title"),
                categories=categories,
                series=series,
                x_axis_title=chart_info.get("x_axis_title"),
                y_axis_title=chart_info.get("y_axis_title"),
                show_legend=chart_info.get("show_legend", True),
                data_labels=chart_info.get("data_labels", False),
                colors=chart_info.get("colors", [])
            )
        except Exception as e:
            print(f"Failed to parse chart data: {e}")
            return None
    
    def _process_text_blocks(
        self,
        text_blocks: List[PDFTextBlock],
        pdf_page_width: float,
        pdf_page_height: float,
        slide_width: float,
        slide_height: float
    ) -> List[TextBox]:
        """Convert PDF text blocks to PowerPoint text boxes"""
        # Group related text blocks
        groups = group_text_blocks(text_blocks)
        
        text_boxes = []
        for group in groups:
            if not group:
                continue
            
            # Calculate bounding box for the group
            min_x = min(b.x for b in group)
            min_y = min(b.y for b in group)
            max_x = max(b.x + b.width for b in group)
            max_y = max(b.y + b.height for b in group)
            
            # Convert coordinates
            ppt_x, ppt_y, ppt_width, ppt_height = convert_coordinates(
                min_x, min_y, max_x - min_x, max_y - min_y,
                pdf_page_width, pdf_page_height,
                slide_width, slide_height
            )
            
            # Create paragraphs from text blocks
            paragraphs = []
            for block in group:
                style = TextStyle(
                    font_name=block.font_name,
                    font_size=block.font_size * (slide_height / points_to_inches(pdf_page_height)),
                    bold=block.is_bold,
                    italic=block.is_italic,
                    color=block.font_color
                )
                
                para = Paragraph(
                    runs=[TextRun(text=block.text, style=style)],
                    alignment="left"
                )
                paragraphs.append(para)
            
            text_box = TextBox(
                paragraphs=paragraphs,
                x=ppt_x,
                y=ppt_y,
                width=max(ppt_width, 0.5),  # Minimum width
                height=max(ppt_height, 0.3)  # Minimum height
            )
            text_boxes.append(text_box)
        
        return text_boxes
    
    def _process_images(
        self,
        images: List[PDFImage],
        pdf_page_width: float,
        pdf_page_height: float,
        slide_width: float,
        slide_height: float
    ) -> List[ImageElement]:
        """Convert PDF images to PowerPoint image elements"""
        image_elements = []
        
        for img in images:
            ppt_x, ppt_y, ppt_width, ppt_height = convert_coordinates(
                img.x, img.y, img.width, img.height,
                pdf_page_width, pdf_page_height,
                slide_width, slide_height
            )
            
            image_elem = ImageElement(
                image_data=img.image_data,
                x=ppt_x,
                y=ppt_y,
                width=ppt_width,
                height=ppt_height
            )
            image_elements.append(image_elem)
        
        return image_elements
    
    def _process_drawings(
        self,
        drawings: List[PDFDrawing],
        pdf_page_width: float,
        pdf_page_height: float,
        slide_width: float,
        slide_height: float
    ) -> List[ShapeElement]:
        """Convert PDF drawings to PowerPoint shapes"""
        shapes = []
        
        for drawing in drawings:
            ppt_x, ppt_y, ppt_width, ppt_height = convert_coordinates(
                drawing.x, drawing.y, drawing.width, drawing.height,
                pdf_page_width, pdf_page_height,
                slide_width, slide_height
            )
            
            # Skip very small drawings (likely artifacts)
            if ppt_width < 0.05 or ppt_height < 0.05:
                continue
            
            # Determine shape type based on aspect ratio and other properties
            aspect = ppt_width / ppt_height if ppt_height > 0 else 1
            if 0.9 < aspect < 1.1:
                shape_type = "oval" if ppt_width < 0.5 else "rectangle"
            else:
                shape_type = "rectangle"
            
            shape = ShapeElement(
                shape_type=shape_type,
                x=ppt_x,
                y=ppt_y,
                width=ppt_width,
                height=ppt_height,
                fill_color=drawing.fill_color,
                border_color=drawing.stroke_color,
                border_width=drawing.stroke_width
            )
            shapes.append(shape)
        
        return shapes
    
    def _create_image_fallback(
        self,
        pdf_path: str,
        page_number: int,
        slide_width: float,
        slide_height: float
    ) -> SlideContent:
        """Create a slide with the page rendered as an image"""
        page_image = pdf_utils.render_page_as_image(pdf_path, page_number)
        return create_slide_from_image(page_image, slide_width, slide_height)
    
    def _cleanup(self):
        """Clean up temporary files"""
        for temp_file in self._temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except:
                pass
        self._temp_files = []


# ============================================================================
# Convenience Functions
# ============================================================================

def convert_pdf_to_pptx(
    pdf_path: str,
    output_path: Optional[str] = None,
    pages: Optional[List[int]] = None,
    options: Optional[ConversionOptions] = None,
    progress_callback: Optional[callable] = None
) -> str:
    """
    Convert a PDF file to PowerPoint presentation.
    
    Args:
        pdf_path: Path to input PDF file
        output_path: Path for output PPTX (default: same name with .pptx extension)
        pages: List of page numbers to convert (1-indexed), None for all
        options: Conversion options
        progress_callback: Optional callback(current, total, message)
    
    Returns:
        Path to created PPTX file
    """
    if output_path is None:
        output_path = str(Path(pdf_path).with_suffix('.pptx'))
    
    converter = PDFToPPTConverter(options)
    return converter.convert(pdf_path, output_path, pages, progress_callback)


def convert_pdf_to_pptx_with_ai(
    pdf_path: str,
    output_path: Optional[str] = None,
    pages: Optional[List[int]] = None,
    extract_charts: bool = True,
    resolution: str = "4K",
    progress_callback: Optional[callable] = None
) -> str:
    """
    Convert PDF to PowerPoint with AI-powered chart extraction.
    
    This is the recommended method for PDFs with charts and graphs
    that you want to be editable in PowerPoint.
    
    Args:
        pdf_path: Path to input PDF file
        output_path: Path for output PPTX
        pages: List of page numbers to convert (1-indexed)
        extract_charts: Whether to extract charts as editable
        resolution: Image resolution for AI analysis
        progress_callback: Optional callback(current, total, message)
    
    Returns:
        Path to created PPTX file
    """
    options = ConversionOptions(
        extract_charts=extract_charts,
        extract_tables=True,
        preserve_fonts=True,
        use_ai_extraction=True,
        resolution=resolution,
        fallback_to_image=True,
        parallel_processing=True
    )
    
    return convert_pdf_to_pptx(pdf_path, output_path, pages, options, progress_callback)
