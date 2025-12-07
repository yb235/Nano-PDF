"""
PDF to PowerPoint Converter Module
Converts PDF slides to PowerPoint presentations with exact font, style, and layout preservation.
Makes graphs and charts editable/interactive in PowerPoint.
"""

import os
import json
import subprocess
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path
from io import BytesIO
import base64

from pdf2image import convert_from_path
from pypdf import PdfReader
from PIL import Image, ImageDraw, ImageFont
import pytesseract
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.chart import XL_CHART_TYPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_LEGEND_POSITION
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# PowerPoint standard dimensions (16:9 aspect ratio)
PPT_WIDTH = Inches(10)
PPT_HEIGHT = Inches(7.5)


def get_gemini_client():
    """Get Gemini API client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    return genai.Client(api_key=api_key)


def analyze_pdf_page_structure(
    pdf_path: str,
    page_number: int,
    full_text_context: str = ""
) -> Dict[str, Any]:
    """
    Uses Gemini AI to analyze a PDF page and extract:
    - Text content with positions, fonts, sizes, colors
    - Images and their positions
    - Charts/graphs and their data
    - Layout structure
    - Color scheme
    - Font families and styles
    """
    client = get_gemini_client()
    
    # Render page as image
    images = convert_from_path(
        pdf_path,
        first_page=page_number,
        last_page=page_number,
        dpi=300  # High resolution for better analysis
    )
    if not images:
        raise ValueError(f"Could not render page {page_number}")
    
    page_image = images[0]
    
    # Convert PIL Image to bytes for API
    img_bytes = BytesIO()
    page_image.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    # Create comprehensive analysis prompt
    prompt = f"""You are an expert PDF-to-PowerPoint converter. Analyze this PDF slide page with EXTREME PRECISION and extract ALL structural, styling, and content information in JSON format.

CRITICAL REQUIREMENTS:
- Extract EXACT font names, sizes, colors, and positions
- Identify ALL charts/graphs and extract their COMPLETE data
- Preserve layout positioning with pixel-perfect accuracy
- Detect all visual elements including logos, icons, shapes

Extract the following:

1. **Text Elements** (array): For EVERY text element on the page:
   - text: The complete text content (preserve line breaks with \\n)
   - x: Left position as percentage (0-100) of page width
   - y: Top position as percentage (0-100) of page height
   - width: Width as percentage of page width
   - height: Height as percentage of page height
   - font_family: Exact font name (e.g., "Arial", "Times New Roman", "Calibri", "Helvetica")
   - font_size: Font size in points (be precise, e.g., 12, 14, 16, 18, 24, 32, 48)
   - font_weight: "normal" or "bold"
   - font_style: "normal" or "italic"
   - color: RGB color as [R, G, B] where each value is 0-255
   - alignment: "left", "center", "right", or "justify"
   - bullet_points: true if it's a bulleted list, false otherwise
   - line_spacing: Approximate line spacing multiplier (e.g., 1.0, 1.5, 2.0)

2. **Images** (array): For EVERY image, logo, icon, or graphic:
   - type: "image"
   - x: Left position as percentage
   - y: Top position as percentage
   - width: Width as percentage
   - height: Height as percentage
   - description: Brief description (e.g., "Company logo", "Product photo", "Icon")

3. **Charts/Graphs** (array): For EVERY chart, graph, or data visualization:
   - type: "chart"
   - chart_type: One of "bar", "column", "line", "pie", "area", "scatter", "bubble", "doughnut", "radar"
   - x: Left position as percentage
   - y: Top position as percentage
   - width: Width as percentage
   - height: Height as percentage
   - title: Chart title text (if present)
   - x_axis_label: X-axis label (if present)
   - y_axis_label: Y-axis label (if present)
   - data: Complete chart data structure:
     - categories: Array of category labels (e.g., ["Q1", "Q2", "Q3", "Q4"])
     - series: Array of data series, each with:
       - name: Series name (e.g., "Revenue", "Profit")
       - values: Array of numeric values matching categories length
   - colors: Array of RGB colors [R, G, B] used in the chart (one per series)
   - has_legend: true if legend is visible, false otherwise
   - legend_position: "top", "bottom", "left", "right", or "none"
   - gridlines: true if gridlines are visible, false otherwise

4. **Shapes/Graphics** (array): For rectangles, circles, arrows, lines, etc.:
   - type: "shape"
   - shape_type: "rectangle", "circle", "line", "arrow", "triangle", etc.
   - x, y, width, height: Position and size as percentages
   - fill_color: RGB color [R, G, B] or null if transparent
   - line_color: RGB color [R, G, B] for border/line
   - line_width: Line width in points

5. **Background**:
   - background_color: RGB color [R, G, B] or null if white/transparent
   - background_image: true if there's a background image, false otherwise
   - background_gradient: true if gradient background, false otherwise

6. **Overall Style**:
   - primary_color: Main/dominant color used (RGB)
   - secondary_color: Secondary/accent color (RGB)
   - font_families: Array of all unique font families used
   - color_scheme: Array of all unique colors used (RGB arrays)
   - theme: "light" or "dark" if discernible

Return ONLY valid, parseable JSON in this exact format:
{{
  "text_elements": [
    {{
      "text": "Example Title",
      "x": 10.5,
      "y": 5.2,
      "width": 30.0,
      "height": 8.0,
      "font_family": "Arial",
      "font_size": 32,
      "font_weight": "bold",
      "font_style": "normal",
      "color": [0, 0, 0],
      "alignment": "center",
      "bullet_points": false,
      "line_spacing": 1.0
    }}
  ],
  "images": [
    {{
      "type": "image",
      "x": 80.0,
      "y": 5.0,
      "width": 15.0,
      "height": 10.0,
      "description": "Company logo"
    }}
  ],
  "charts": [
    {{
      "type": "chart",
      "chart_type": "column",
      "x": 10.0,
      "y": 30.0,
      "width": 80.0,
      "height": 50.0,
      "title": "Quarterly Revenue",
      "x_axis_label": "Quarter",
      "y_axis_label": "Revenue ($M)",
      "data": {{
        "categories": ["Q1", "Q2", "Q3", "Q4"],
        "series": [
          {{
            "name": "Revenue",
            "values": [10.5, 12.3, 15.2, 18.7]
          }}
        ]
      }},
      "colors": [[65, 105, 225]],
      "has_legend": true,
      "legend_position": "bottom",
      "gridlines": true
    }}
  ],
  "shapes": [],
  "background": {{
    "background_color": [255, 255, 255],
    "background_image": false,
    "background_gradient": false
  }},
  "style": {{
    "primary_color": [0, 0, 0],
    "secondary_color": [65, 105, 225],
    "font_families": ["Arial", "Calibri"],
    "color_scheme": [[0, 0, 0], [65, 105, 225], [255, 255, 255]],
    "theme": "light"
  }}
}}

IMPORTANT:
- Be EXTREMELY precise with all measurements and colors
- Extract COMPLETE chart data - read all numbers from axes and data points
- Identify ALL visual elements, don't miss anything
- Preserve exact text content including special characters
- Use accurate font size detection based on visual appearance
{f"Document context (for reference): {full_text_context[:2000]}" if full_text_context else ""}
"""
    
    try:
        config = types.GenerateContentConfig(
            response_modalities=['TEXT'],
            temperature=0.1  # Low temperature for consistent, precise output
        )
        
        # Try gemini-2.0-flash-exp first, fallback to gemini-1.5-pro if needed
        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=[prompt, page_image],
                config=config
            )
        except Exception as e:
            # Fallback to gemini-1.5-pro if flash-exp is not available
            print(f"  Note: Falling back to gemini-1.5-pro: {e}")
            response = client.models.generate_content(
                model='gemini-1.5-pro',
                contents=[prompt, page_image],
                config=config
            )
        
        if not response.candidates or not response.candidates[0].content.parts:
            raise RuntimeError("No response from Gemini API")
        
        response_text = response.candidates[0].content.parts[0].text
        
        # Extract JSON from response (handle markdown code blocks)
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        
        # Parse JSON
        structure = json.loads(response_text)
        return structure
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Response was: {response_text[:500]}")
        # Return minimal structure if parsing fails
        return {
            "text_elements": [],
            "images": [],
            "charts": [],
            "background": {"background_color": None, "background_image": False},
            "style": {"primary_color": [0, 0, 0], "font_families": ["Arial"]}
        }
    except Exception as e:
        print(f"Error analyzing page: {e}")
        raise


def extract_text_with_ocr(page_image: Image.Image) -> List[Dict[str, Any]]:
    """
    Extract text with OCR and get bounding boxes for better positioning.
    Falls back to OCR if AI analysis fails.
    """
    try:
        # Use pytesseract to get detailed text data
        data = pytesseract.image_to_data(page_image, output_type=pytesseract.Output.DICT)
        
        text_elements = []
        width, height = page_image.size
        
        for i in range(len(data['text'])):
            text = data['text'][i].strip()
            if text and int(data['conf'][i]) > 30:  # Confidence threshold
                x = (data['left'][i] / width) * 100
                y = (data['top'][i] / height) * 100
                w = (data['width'][i] / width) * 100
                h = (data['height'][i] / height) * 100
                
                text_elements.append({
                    "text": text,
                    "x": x,
                    "y": y,
                    "width": w,
                    "height": h,
                    "font_family": "Arial",  # Default, will be refined by AI
                    "font_size": max(8, int(data['height'][i] * 0.75)),  # Approximate
                    "font_weight": "normal",
                    "font_style": "normal",
                    "color": [0, 0, 0],
                    "alignment": "left"
                })
        
        return text_elements
    except Exception as e:
        print(f"OCR extraction error: {e}")
        return []


def rgb_to_ppt_color(rgb: List[int]) -> RGBColor:
    """Convert RGB list [R, G, B] to PowerPoint RGBColor."""
    if len(rgb) >= 3:
        return RGBColor(rgb[0], rgb[1], rgb[2])
    return RGBColor(0, 0, 0)


def percent_to_inches(percent: float, dimension: str) -> float:
    """Convert percentage to inches based on PPT dimensions."""
    if dimension == "width":
        return (percent / 100.0) * PPT_WIDTH.inches
    else:
        return (percent / 100.0) * PPT_HEIGHT.inches


def get_font_family_mapping(font_name: str) -> str:
    """
    Map PDF font names to PowerPoint-compatible font names.
    PowerPoint has limited font support, so we map common fonts.
    """
    font_mapping = {
        "arial": "Arial",
        "helvetica": "Arial",
        "times": "Times New Roman",
        "times new roman": "Times New Roman",
        "times-roman": "Times New Roman",
        "courier": "Courier New",
        "courier new": "Courier New",
        "calibri": "Calibri",
        "verdana": "Verdana",
        "georgia": "Georgia",
        "palatino": "Palatino Linotype",
        "comic sans": "Comic Sans MS",
        "trebuchet": "Trebuchet MS",
        "impact": "Impact",
    }
    
    font_lower = font_name.lower().strip()
    for key, value in font_mapping.items():
        if key in font_lower:
            return value
    
    # Default to Arial if not found
    return "Arial"


def add_text_to_slide(
    slide,
    text_element: Dict[str, Any],
    slide_width: float,
    slide_height: float
):
    """Add a text element to a PowerPoint slide with exact styling."""
    text = text_element.get("text", "")
    if not text:
        return
    
    # Calculate position and size
    left = percent_to_inches(text_element.get("x", 0), "width")
    top = percent_to_inches(text_element.get("y", 0), "height")
    width = percent_to_inches(text_element.get("width", 10), "width")
    height = percent_to_inches(text_element.get("height", 5), "height")
    
    # Create text box
    textbox = slide.shapes.add_textbox(
        Inches(left),
        Inches(top),
        Inches(width),
        Inches(height)
    )
    
    text_frame = textbox.text_frame
    text_frame.word_wrap = True
    text_frame.auto_size = None
    
    # Set alignment
    alignment_map = {
        "left": PP_ALIGN.LEFT,
        "center": PP_ALIGN.CENTER,
        "right": PP_ALIGN.RIGHT,
        "justify": PP_ALIGN.JUSTIFY
    }
    alignment = alignment_map.get(
        text_element.get("alignment", "left").lower(),
        PP_ALIGN.LEFT
    )
    
    # Handle bullet points
    is_bullet = text_element.get("bullet_points", False)
    paragraphs = text.split("\n") if "\n" in text else [text]
    
    for i, para_text in enumerate(paragraphs):
        if i == 0:
            p = text_frame.paragraphs[0]
        else:
            p = text_frame.add_paragraph()
        
        p.text = para_text.strip()
        p.alignment = alignment
        
        # Set font properties
        font = p.font
        font_family = get_font_family_mapping(
            text_element.get("font_family", "Arial")
        )
        font.name = font_family
        font.size = Pt(text_element.get("font_size", 12))
        
        # Font weight
        if text_element.get("font_weight", "normal").lower() == "bold":
            font.bold = True
        
        # Font style
        if text_element.get("font_style", "normal").lower() == "italic":
            font.italic = True
        
        # Color
        color = rgb_to_ppt_color(text_element.get("color", [0, 0, 0]))
        font.color.rgb = color
        
        # Bullet points
        if is_bullet:
            p.level = 0
            p.space_after = Pt(6)
    
    # Set text frame properties
    text_frame.vertical_anchor = MSO_ANCHOR.TOP
    text_frame.margin_left = Inches(0.1)
    text_frame.margin_right = Inches(0.1)
    text_frame.margin_top = Inches(0.05)
    text_frame.margin_bottom = Inches(0.05)


def add_image_to_slide(
    slide,
    image_element: Dict[str, Any],
    pdf_path: str,
    page_number: int,
    slide_width: float,
    slide_height: float
):
    """Add an image to a PowerPoint slide."""
    left = percent_to_inches(image_element.get("x", 0), "width")
    top = percent_to_inches(image_element.get("y", 0), "height")
    width = percent_to_inches(image_element.get("width", 10), "width")
    height = percent_to_inches(image_element.get("height", 10), "height")
    
    # Try to extract image from PDF page
    # For now, we'll use a placeholder approach
    # In a full implementation, you'd extract the actual image from PDF
    
    # Create a placeholder shape
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(left),
        Inches(top),
        Inches(width),
        Inches(height)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(240, 240, 240)
    shape.line.color.rgb = RGBColor(200, 200, 200)
    
    # Add text label
    text_frame = shape.text_frame
    text_frame.text = image_element.get("description", "Image")
    p = text_frame.paragraphs[0]
    p.font.size = Pt(10)
    p.font.color.rgb = RGBColor(100, 100, 100)
    p.alignment = PP_ALIGN.CENTER


def add_shape_to_slide(
    slide,
    shape_element: Dict[str, Any],
    slide_width: float,
    slide_height: float
):
    """Add a shape (rectangle, circle, line, etc.) to a PowerPoint slide."""
    shape_type_str = shape_element.get("shape_type", "rectangle").lower()
    left = percent_to_inches(shape_element.get("x", 0), "width")
    top = percent_to_inches(shape_element.get("y", 0), "height")
    width = percent_to_inches(shape_element.get("width", 5), "width")
    height = percent_to_inches(shape_element.get("height", 5), "height")
    
    # Map shape types
    shape_type_map = {
        "rectangle": MSO_SHAPE.RECTANGLE,
        "circle": MSO_SHAPE.OVAL,
        "oval": MSO_SHAPE.OVAL,
        "line": MSO_SHAPE.LINE,
        "arrow": MSO_SHAPE.RIGHT_ARROW,
        "triangle": MSO_SHAPE.TRIANGLE,
        "rounded_rectangle": MSO_SHAPE.ROUNDED_RECTANGLE,
    }
    
    ppt_shape_type = shape_type_map.get(shape_type_str, MSO_SHAPE.RECTANGLE)
    
    try:
        shape = slide.shapes.add_shape(
            ppt_shape_type,
            Inches(left),
            Inches(top),
            Inches(width),
            Inches(height)
        )
        
        # Set fill color
        fill_color = shape_element.get("fill_color")
        if fill_color:
            shape.fill.solid()
            shape.fill.fore_color.rgb = rgb_to_ppt_color(fill_color)
        else:
            shape.fill.solid()
            shape.fill.fore_color.rgb = RGBColor(255, 255, 255)
        
        # Set line/border color
        line_color = shape_element.get("line_color")
        if line_color:
            shape.line.color.rgb = rgb_to_ppt_color(line_color)
            line_width = shape_element.get("line_width", 1)
            shape.line.width = Pt(line_width)
        else:
            shape.line.fill.background()  # No line
        
    except Exception as e:
        print(f"  Note: Could not create shape {shape_type_str}: {e}")


def create_chart_in_slide(
    slide,
    chart_element: Dict[str, Any],
    slide_width: float,
    slide_height: float
):
    """Create an editable chart in PowerPoint from chart data with full styling."""
    left = percent_to_inches(chart_element.get("x", 0), "width")
    top = percent_to_inches(chart_element.get("y", 0), "height")
    width = percent_to_inches(chart_element.get("width", 30), "width")
    height = percent_to_inches(chart_element.get("height", 20), "height")
    
    chart_data = chart_element.get("data", {})
    chart_type_str = chart_element.get("chart_type", "column").lower()
    
    # Comprehensive chart type mapping
    chart_type_map = {
        "bar": XL_CHART_TYPE.BAR_CLUSTERED,
        "column": XL_CHART_TYPE.COLUMN_CLUSTERED,
        "line": XL_CHART_TYPE.LINE,
        "pie": XL_CHART_TYPE.PIE,
        "doughnut": XL_CHART_TYPE.DOUGHNUT,
        "area": XL_CHART_TYPE.AREA,
        "scatter": XL_CHART_TYPE.XY_SCATTER,
        "bubble": XL_CHART_TYPE.BUBBLE,
        "radar": XL_CHART_TYPE.RADAR,
    }
    
    chart_type = chart_type_map.get(chart_type_str, XL_CHART_TYPE.COLUMN_CLUSTERED)
    
    # Prepare chart data
    chart_data_obj = CategoryChartData()
    
    categories = chart_data.get("categories", [])
    series_list = chart_data.get("series", [])
    
    if not categories:
        # Fallback: create categories from series length
        if series_list and len(series_list) > 0:
            first_series_values = series_list[0].get("values", [])
            categories = [f"Item {i+1}" for i in range(len(first_series_values))]
    
    chart_data_obj.categories = categories
    
    for series in series_list:
        series_name = series.get("name", "Series")
        values = series.get("values", [])
        if values:
            chart_data_obj.add_series(series_name, values)
    
    # Create chart
    try:
        chart_shape = slide.shapes.add_chart(
            chart_type,
            Inches(left),
            Inches(top),
            Inches(width),
            Inches(height),
            chart_data_obj
        )
        
        chart = chart_shape.chart
        
        # Set chart title
        title_text = chart_element.get("title", "")
        if title_text:
            chart.has_title = True
            chart.chart_title.text_frame.text = title_text
            chart.chart_title.text_frame.paragraphs[0].font.size = Pt(14)
            chart.chart_title.text_frame.paragraphs[0].font.bold = True
        
        # Set axis labels
        try:
            x_axis_label = chart_element.get("x_axis_label", "")
            y_axis_label = chart_element.get("y_axis_label", "")
            
            if x_axis_label and hasattr(chart, "category_axis"):
                chart.category_axis.has_title = True
                chart.category_axis.axis_title.text_frame.text = x_axis_label
            
            if y_axis_label and hasattr(chart, "value_axis"):
                chart.value_axis.has_title = True
                chart.value_axis.axis_title.text_frame.text = y_axis_label
        except Exception as e:
            print(f"  Note: Could not set axis labels: {e}")
        
        # Set legend
        has_legend = chart_element.get("has_legend", True)
        chart.has_legend = has_legend
        
        if has_legend:
            legend_pos_map = {
                "top": XL_LEGEND_POSITION.TOP,
                "bottom": XL_LEGEND_POSITION.BOTTOM,
                "left": XL_LEGEND_POSITION.LEFT,
                "right": XL_LEGEND_POSITION.RIGHT,
            }
            legend_pos = legend_pos_map.get(
                chart_element.get("legend_position", "bottom").lower(),
                XL_LEGEND_POSITION.BOTTOM
            )
            chart.legend.position = legend_pos
        
        # Apply colors if specified
        colors = chart_element.get("colors", [])
        if colors and hasattr(chart, "series") and chart.series:
            for i, series_obj in enumerate(chart.series):
                if i < len(colors):
                    try:
                        color = rgb_to_ppt_color(colors[i])
                        series_obj.format.fill.solid()
                        series_obj.format.fill.fore_color.rgb = color
                    except Exception as e:
                        print(f"  Note: Could not apply color to series {i}: {e}")
        
        # Set gridlines
        try:
            if chart_element.get("gridlines", False):
                if hasattr(chart, "value_axis"):
                    chart.value_axis.has_major_gridlines = True
                    chart.value_axis.major_gridlines.format.line.color.rgb = RGBColor(200, 200, 200)
        except Exception as e:
            print(f"  Note: Could not set gridlines: {e}")
        
        print(f"  ✓ Created editable {chart_type_str} chart with {len(series_list)} series")
        
    except Exception as e:
        print(f"  ⚠ Error creating chart: {e}")
        import traceback
        print(f"  Traceback: {traceback.format_exc()}")
        # Fallback: create a placeholder shape with chart info
        shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(left),
            Inches(top),
            Inches(width),
            Inches(height)
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = RGBColor(240, 240, 240)
        shape.line.color.rgb = RGBColor(150, 150, 150)
        
        text_frame = shape.text_frame
        text_frame.text = f"Chart: {chart_type_str}\n(Data extraction needed)"
        if title_text:
            text_frame.text += f"\n{title_text}"
        p = text_frame.paragraphs[0]
        p.font.size = Pt(12)
        p.alignment = PP_ALIGN.CENTER


def convert_pdf_to_ppt(
    pdf_path: str,
    output_ppt_path: str,
    use_ai_analysis: bool = True,
    use_context: bool = True,
    resolution: str = "high"
) -> str:
    """
    Convert a PDF presentation to PowerPoint format.
    
    Args:
        pdf_path: Path to input PDF file
        output_ppt_path: Path to output PowerPoint file
        use_ai_analysis: Use Gemini AI for structure analysis (recommended)
        use_context: Include full PDF text as context for AI
        resolution: Image resolution for analysis ("high", "medium", "low")
    
    Returns:
        Path to created PowerPoint file
    """
    print(f"Converting PDF to PowerPoint: {pdf_path}")
    
    # Create PowerPoint presentation
    prs = Presentation()
    prs.slide_width = Emu(int(PPT_WIDTH.inches * 914400))
    prs.slide_height = Emu(int(PPT_HEIGHT.inches * 914400))
    
    # Get PDF page count
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    
    print(f"Found {total_pages} pages in PDF")
    
    # Extract full text context if requested
    full_text = ""
    if use_context:
        print("Extracting text context...")
        try:
            result = subprocess.run(
                ['pdftotext', '-layout', pdf_path, '-'],
                capture_output=True,
                text=True,
                check=True
            )
            full_text = result.stdout[:5000]  # Limit context size
        except Exception as e:
            print(f"Warning: Could not extract text context: {e}")
    
    # Process each page
    for page_num in range(1, total_pages + 1):
        print(f"Processing page {page_num}/{total_pages}...")
        
        # Create new slide
        slide_layout = prs.slide_layouts[6]  # Blank layout
        slide = prs.slides.add_slide(slide_layout)
        
        # Set background if needed (will be set after analysis)
        
        if use_ai_analysis:
            try:
                # Analyze page structure with AI
                structure = analyze_pdf_page_structure(
                    pdf_path,
                    page_num,
                    full_text
                )
                
                # Add text elements
                for text_elem in structure.get("text_elements", []):
                    try:
                        add_text_to_slide(
                            slide,
                            text_elem,
                            PPT_WIDTH.inches,
                            PPT_HEIGHT.inches
                        )
                    except Exception as e:
                        print(f"  Warning: Could not add text element: {e}")
                
                # Add images
                for img_elem in structure.get("images", []):
                    try:
                        add_image_to_slide(
                            slide,
                            img_elem,
                            pdf_path,
                            page_num,
                            PPT_WIDTH.inches,
                            PPT_HEIGHT.inches
                        )
                    except Exception as e:
                        print(f"  Warning: Could not add image: {e}")
                
                # Add charts (make them editable!)
                for chart_elem in structure.get("charts", []):
                    try:
                        create_chart_in_slide(
                            slide,
                            chart_elem,
                            PPT_WIDTH.inches,
                            PPT_HEIGHT.inches
                        )
                    except Exception as e:
                        print(f"  Warning: Could not create chart: {e}")
                
                # Add shapes
                for shape_elem in structure.get("shapes", []):
                    try:
                        add_shape_to_slide(
                            slide,
                            shape_elem,
                            PPT_WIDTH.inches,
                            PPT_HEIGHT.inches
                        )
                    except Exception as e:
                        print(f"  Warning: Could not add shape: {e}")
                
                # Set background color
                background_info = structure.get("background", {})
                bg_color = background_info.get("background_color")
                if bg_color and bg_color != [255, 255, 255]:  # Not white
                    try:
                        background = slide.background
                        fill = background.fill
                        fill.solid()
                        fill.fore_color.rgb = rgb_to_ppt_color(bg_color)
                    except Exception as e:
                        print(f"  Note: Could not set background color: {e}")
                
            except Exception as e:
                print(f"  Error analyzing page {page_num} with AI: {e}")
                print(f"  Falling back to OCR extraction...")
                
                # Fallback: Use OCR
                images = convert_from_path(
                    pdf_path,
                    first_page=page_num,
                    last_page=page_num,
                    dpi=200
                )
                if images:
                    text_elements = extract_text_with_ocr(images[0])
                    for text_elem in text_elements:
                        try:
                            add_text_to_slide(
                                slide,
                                text_elem,
                                PPT_WIDTH.inches,
                                PPT_HEIGHT.inches
                            )
                        except Exception as e:
                            print(f"    Warning: Could not add OCR text: {e}")
        else:
            # Use OCR-only approach
            images = convert_from_path(
                pdf_path,
                first_page=page_num,
                last_page=page_num,
                dpi=200
            )
            if images:
                text_elements = extract_text_with_ocr(images[0])
                for text_elem in text_elements:
                    try:
                        add_text_to_slide(
                            slide,
                            text_elem,
                            PPT_WIDTH.inches,
                            PPT_HEIGHT.inches
                        )
                    except Exception as e:
                        print(f"  Warning: Could not add text: {e}")
    
    # Save presentation
    print(f"Saving PowerPoint to {output_ppt_path}...")
    prs.save(output_ppt_path)
    
    print(f"✓ Conversion complete! Created {output_ppt_path}")
    return output_ppt_path
