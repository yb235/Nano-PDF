"""
Comprehensive PDF to PPT converter using Gemini 3 Pro Image to analyze
and convert PDF pages to PowerPoint slides with exact font, style, and
interactive chart preservation.
"""
import os
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
from PIL import Image
import json
import re
from nano_pdf import pdf_utils, ai_utils, ppt_utils
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
import io


def analyze_pdf_page_structure(page_image: Image.Image, page_number: int,
                              full_text_context: str = "",
                              resolution: str = "4K") -> Dict[str, Any]:
    """
    Use Gemini 3 Pro Image to analyze a PDF page and extract its structure,
    including text elements, fonts, styles, colors, charts, and layout.
    """
    client = ai_utils.get_client()
    
    # Create a comprehensive prompt for structure analysis
    analysis_prompt = f"""
You are an expert at analyzing presentation slides and extracting their complete structure for perfect recreation.

Analyze this PDF slide page (Page {page_number}) and extract ALL elements with EXACT formatting details.

CRITICAL: Your goal is to enable PERFECT recreation of this slide in PowerPoint with:
- Exact font names, sizes, and styles
- Precise colors (hex codes)
- Accurate positioning and sizing
- Interactive charts with extracted data
- All visual elements preserved

Return a JSON object with this structure:
{{
  "background": {{
    "color": "#hexcolor" or null,
    "has_image": true/false
  }},
  "elements": [
    {{
      "type": "text|image|chart|shape|table",
      "content": "text content if type is text",
      "left": 0.5,  // position in inches from left (0-10)
      "top": 0.5,   // position in inches from top (0-7.5)
      "width": 9.0, // width in inches
      "height": 1.0, // height in inches
      "font": {{
        "font_family": "exact font name (e.g., 'Arial', 'Calibri', 'Times New Roman')",
        "font_size": 24,
        "color": "#000000",
        "bold": false,
        "italic": false,
        "underline": false
      }},
      "alignment": "left|center|right|justify",
      "crop": {{"x1": 0.0, "y1": 0.0, "x2": 1.0, "y2": 1.0}}  // for images, relative coordinates
    }},
    // For charts:
    {{
      "type": "chart",
      "chart_type": "bar|column|line|pie|area|scatter",
      "left": 1.0,
      "top": 2.0,
      "width": 8.0,
      "height": 4.0,
      "data": {{
        "categories": ["Q1", "Q2", "Q3", "Q4"],
        "series": [
          {{"name": "Revenue", "values": [100, 120, 140, 160]}},
          {{"name": "Profit", "values": [20, 30, 40, 50]}}
        ]
      }},
      "title": "Chart Title",
      "has_legend": true,
      "axis_labels": {{"x": "Quarter", "y": "Amount ($)"}}
    }},
    // For tables:
    {{
      "type": "table",
      "left": 1.0,
      "top": 1.0,
      "width": 8.0,
      "height": 4.0,
      "rows": 3,
      "columns": 4,
      "data": [
        ["Header1", "Header2", "Header3", "Header4"],
        ["Row1Col1", "Row1Col2", "Row1Col3", "Row1Col4"],
        ["Row2Col1", "Row2Col2", "Row2Col3", "Row2Col4"]
      ],
      "header_style": {{"bold": true, "background": "#f0f0f0"}},
      "cell_styles": [[{{"font": {{...}}}}, ...], ...]
    }}
  ],
  "layout": "title|blank|two_content|title_and_content",
  "slide_dimensions": {{"width": 10.0, "height": 7.5}}
}}

CRITICAL REQUIREMENTS:
1. Extract EXACT font names (e.g., "Arial", "Calibri", "Times New Roman", "Helvetica") - be precise!
2. Extract EXACT font sizes in points (e.g., 12, 18, 24, 36, 48)
3. Extract EXACT colors as hex codes (e.g., "#000000" for black, "#FF0000" for red)
4. Identify ALL charts and extract their COMPLETE data to make them interactive
5. For charts: Read ALL axis labels, legends, data points, and series names
6. For charts: Extract numerical values accurately from the visualization
7. Measure positions in inches (0.0 to 10.0 for width, 0.0 to 7.5 for height)
8. Measure sizes in inches relative to slide dimensions
9. For images: Provide crop coordinates (0.0 to 1.0) to extract image regions
10. Maintain text alignment (left, center, right, justify)
11. Preserve ALL formatting: bold, italic, underline
12. Identify background colors or images
13. Extract table data with all rows and columns
14. Identify shapes and their properties (fill color, line color, type)

IMPORTANT FOR CHARTS:
- Read the chart type carefully (bar, column, line, pie, area, scatter)
- Extract ALL series data with exact values
- Extract category labels from axes
- Extract series names from legends
- Note axis labels and titles

IMPORTANT FOR TEXT:
- Extract complete text content
- Note font family, size, color, and style
- Preserve line breaks and spacing
- Note text alignment

Return ONLY valid JSON, no additional text or markdown formatting.
"""
    
    if full_text_context:
        analysis_prompt += f"\n\nDOCUMENT CONTEXT:\n{full_text_context}\n"
    
    # Build config for detailed analysis
    from google.genai import types
    config = types.GenerateContentConfig(
        response_modalities=['TEXT'],
        temperature=0.1,  # Lower temperature for more accurate extraction
    )
    
    try:
        response = client.models.generate_content(
            model='gemini-3-pro-image-preview',
            contents=[analysis_prompt, page_image],
            config=config
        )
        
        response_text = ""
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.text:
                    response_text += part.text
        
        # Parse JSON from response
        structure = parse_structure_response(response_text)
        return structure
        
    except Exception as e:
        print(f"Error analyzing page structure: {e}")
        # Return fallback structure
        return {
            "background": None,
            "elements": [],
            "layout": "blank",
            "slide_dimensions": {"width": 10.0, "height": 7.5}
        }


def parse_structure_response(response_text: str) -> Dict[str, Any]:
    """Parse the AI response to extract structured data."""
    try:
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        
        # Try to find JSON object directly
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        
        # Fallback: return empty structure
        return {
            "background": None,
            "elements": [],
            "layout": "blank",
            "slide_dimensions": {"width": 10.0, "height": 7.5}
        }
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        print(f"Response text: {response_text[:500]}")
        return {
            "background": None,
            "elements": [],
            "layout": "blank",
            "slide_dimensions": {"width": 10.0, "height": 7.5}
        }


def enhance_chart_data_with_ai(chart_image: Image.Image, chart_context: str = "") -> Dict[str, Any]:
    """
    Use AI to extract chart data from a chart image region.
    This makes charts 'alive' by extracting their actual data.
    """
    client = ai_utils.get_client()
    
    prompt = f"""
You are an expert at reading charts and extracting data for recreation.

Analyze this chart image and extract ALL data to recreate it as an interactive chart in PowerPoint.

Be EXTREMELY precise when reading:
- Numerical values from axes and data points
- Category labels from axes
- Series names from legends
- Chart type (bar, column, line, pie, area, scatter, bubble)
- Axis labels and titles
- Legend information

Return JSON in this format:
{{
  "type": "bar|column|line|pie|area|scatter|bubble",
  "title": "Chart Title",
  "categories": ["Category1", "Category2", "Category3", ...],
  "series": [
    {{"name": "Series1", "values": [value1, value2, value3, ...]}},
    {{"name": "Series2", "values": [value1, value2, value3, ...]}}
  ],
  "x_axis_label": "X Axis Label",
  "y_axis_label": "Y Axis Label",
  "has_legend": true,
  "legend_position": "bottom|top|left|right"
}}

Extract EXACT numerical values from the chart. Be precise with data extraction.
Read all axis labels, legends, and data points carefully.
Count data points accurately.
Read axis scales and intervals correctly.
Extract all series if multiple series are present.

{chart_context}

CRITICAL: Return ONLY valid JSON. No markdown, no code blocks, just pure JSON.
"""
    
    from google.genai import types
    config = types.GenerateContentConfig(
        response_modalities=['TEXT'],
        temperature=0.1,
    )
    
    try:
        response = client.models.generate_content(
            model='gemini-3-pro-image-preview',
            contents=[prompt, chart_image],
            config=config
        )
        
        response_text = ""
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.text:
                    response_text += part.text
        
        # Parse chart data
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            chart_data = json.loads(json_match.group())
            # Ensure it has the right structure for ppt_utils
            if 'type' in chart_data and 'chart_type' not in chart_data:
                chart_data['chart_type'] = chart_data['type']
            return chart_data
        else:
            return {}
    except Exception as e:
        print(f"Error extracting chart data: {e}")
        return {}


def convert_pdf_to_ppt(pdf_path: str, output_ppt_path: str,
                       full_text_context: str = "",
                       resolution: str = "4K",
                       enable_search: bool = False) -> str:
    """
    Convert a PDF to PowerPoint presentation with exact formatting preservation.
    
    Args:
        pdf_path: Path to input PDF
        output_ppt_path: Path to output PPTX file
        full_text_context: Full text context from PDF
        resolution: Image resolution for analysis
        enable_search: Enable Google Search for AI
    
    Returns:
        Path to created PPTX file
    """
    print(f"Converting PDF to PPT: {pdf_path}")
    
    # Get total pages
    total_pages = pdf_utils.get_page_count(pdf_path)
    print(f"Found {total_pages} pages in PDF")
    
    # Create presentation
    prs = Presentation()
    
    # Set standard 16:9 dimensions (10" x 7.5" for 16:9 aspect ratio)
    prs.slide_width = ppt_utils.inches_to_emu(10.0)
    prs.slide_height = ppt_utils.inches_to_emu(7.5)
    
    print(f"Created presentation with dimensions: {prs.slide_width/914400:.1f}\" x {prs.slide_height/914400:.1f}\"")
    
    # Process each page
    for page_num in range(1, total_pages + 1):
        print(f"\nProcessing page {page_num}/{total_pages}...")
        
        try:
            # Render page as image
            page_image = pdf_utils.render_page_as_image(pdf_path, page_num)
            print(f"  Rendered page {page_num} as image ({page_image.size[0]}x{page_image.size[1]})")
            
            # Analyze page structure with AI
            print(f"  Analyzing page structure with AI (this may take a moment)...")
            structure = analyze_pdf_page_structure(
                page_image,
                page_num,
                full_text_context,
                resolution
            )
            
            # Debug: print structure summary
            num_elements = len(structure.get('elements', []))
            print(f"  Found {num_elements} elements: ", end="")
            element_types = {}
            for elem in structure.get('elements', []):
                elem_type = elem.get('type', 'unknown')
                element_types[elem_type] = element_types.get(elem_type, 0) + 1
            print(", ".join([f"{count} {type}(s)" for type, count in element_types.items()]))
            
            # Create slide from structure
            elements = structure.get('elements', [])
            print(f"  Creating slide from {len(elements)} elements...")
            
            # If no elements extracted, use fallback: add full page as image
            if not elements:
                print(f"  Warning: No elements extracted, using full page image as fallback")
                blank_layout = prs.slide_layouts[6]
                slide = prs.slides.add_slide(blank_layout)
                ppt_utils.apply_slide_background(slide, background_color=structure.get('background', {}).get('color'))
                ppt_utils.add_image_to_slide(slide, page_image, 0, 0, 10.0, 7.5)
            else:
                slide = create_slide_from_structure(prs, structure, page_image, page_num)
            
            print(f"  ✓ Page {page_num} converted successfully")
            
        except Exception as e:
            print(f"  ✗ Error processing page {page_num}: {e}")
            import traceback
            print(f"  Traceback: {traceback.format_exc()}")
            # Create a blank slide as fallback
            blank_layout = prs.slide_layouts[6]
            slide = prs.slides.add_slide(blank_layout)
            # Add the page image as a full-slide image
            try:
                ppt_utils.add_image_to_slide(slide, page_image, 0, 0, 10.0, 7.5)
                print(f"  ✓ Added page {page_num} as fallback image")
            except Exception as fallback_error:
                print(f"  ✗ Even fallback failed: {fallback_error}")
    
    # Save presentation
    print(f"\nSaving presentation to {output_ppt_path}...")
    ppt_utils.save_presentation(prs, output_ppt_path)
    print(f"✓ Conversion complete! Saved to {output_ppt_path}")
    
    return output_ppt_path


def create_slide_from_structure(prs: Presentation, structure: Dict[str, Any],
                               page_image: Image.Image, page_num: int):
    """Create a PowerPoint slide from the analyzed structure."""
    # Use blank layout for maximum control
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    
    # Apply background
    background = structure.get('background')
    if background:
        bg_color = background.get('color')
        if bg_color:
            ppt_utils.apply_slide_background(slide, background_color=bg_color)
    
    # Get slide dimensions
    slide_dims = structure.get('slide_dimensions', {'width': 10.0, 'height': 7.5})
    slide_width = slide_dims.get('width', 10.0)
    slide_height = slide_dims.get('height', 7.5)
    
    # Process each element
    elements = structure.get('elements', [])
    img_width, img_height = page_image.size
    
    for elem in elements:
        elem_type = elem.get('type', '')
        
        try:
            if elem_type == 'text':
                # Add text element
                text = elem.get('content', '')
                if not text:
                    continue
                
                left = elem.get('left', 0.5)
                top = elem.get('top', 0.5)
                width = elem.get('width', 9.0)
                height = elem.get('height', 1.0)
                font_info = ppt_utils.parse_font_info(elem.get('font', {}))
                alignment = elem.get('alignment', 'left')
                multi_paragraph = elem.get('multi_paragraph', '\n' in text)
                
                ppt_utils.add_text_box(slide, text, left, top, width, height,
                                      font_info, alignment, multi_paragraph)
            
            elif elem_type == 'image':
                # Add image element
                left = elem.get('left', 0.5)
                top = elem.get('top', 0.5)
                width = elem.get('width', 9.0)
                height = elem.get('height', 5.0)
                
                # If crop coordinates provided, extract image region
                if 'crop' in elem:
                    crop = elem['crop']
                    x1 = int(crop.get('x1', 0) * img_width)
                    y1 = int(crop.get('y1', 0) * img_height)
                    x2 = int(crop.get('x2', 1) * img_width)
                    y2 = int(crop.get('y2', 1) * img_height)
                    
                    cropped_img = page_image.crop((x1, y1, x2, y2))
                    ppt_utils.add_image_to_slide(slide, cropped_img, left, top, width, height)
                else:
                    # Use full page image
                    ppt_utils.add_image_to_slide(slide, page_image, left, top, width, height)
            
            elif elem_type == 'chart':
                # Create interactive chart
                left = elem.get('left', 1.0)
                top = elem.get('top', 1.0)
                width = elem.get('width', 8.0)
                height = elem.get('height', 4.0)
                
                chart_data = elem.get('data', {})
                if not chart_data or not chart_data.get('series'):
                    # Try to extract chart data from image region
                    if 'crop' in elem:
                        crop = elem['crop']
                        x1 = max(0, int(crop.get('x1', 0) * img_width))
                        y1 = max(0, int(crop.get('y1', 0) * img_height))
                        x2 = min(img_width, int(crop.get('x2', 1) * img_width))
                        y2 = min(img_height, int(crop.get('y2', 1) * img_height))
                        
                        if x2 > x1 and y2 > y1:
                            chart_img = page_image.crop((x1, y1, x2, y2))
                            enhanced_data = enhance_chart_data_with_ai(chart_img)
                            if enhanced_data:
                                chart_data = enhanced_data
                    else:
                        # Use full page image for chart extraction
                        enhanced_data = enhance_chart_data_with_ai(page_image)
                        if enhanced_data:
                            chart_data = enhanced_data
                
                # Create the chart if we have valid data
                if chart_data and chart_data.get('series'):
                    chart_shape = ppt_utils.create_chart_from_data(slide, chart_data, left, top, width, height)
                    if not chart_shape:
                        # Fallback: add chart as image
                        if 'crop' in elem:
                            crop = elem['crop']
                            x1 = max(0, int(crop.get('x1', 0) * img_width))
                            y1 = max(0, int(crop.get('y1', 0) * img_height))
                            x2 = min(img_width, int(crop.get('x2', 1) * img_width))
                            y2 = min(img_height, int(crop.get('y2', 1) * img_height))
                            if x2 > x1 and y2 > y1:
                                chart_img = page_image.crop((x1, y1, x2, y2))
                                ppt_utils.add_image_to_slide(slide, chart_img, left, top, width, height)
                else:
                    # Fallback: add chart region as image
                    if 'crop' in elem:
                        crop = elem['crop']
                        x1 = max(0, int(crop.get('x1', 0) * img_width))
                        y1 = max(0, int(crop.get('y1', 0) * img_height))
                        x2 = min(img_width, int(crop.get('x2', 1) * img_width))
                        y2 = min(img_height, int(crop.get('y2', 1) * img_height))
                        if x2 > x1 and y2 > y1:
                            chart_img = page_image.crop((x1, y1, x2, y2))
                            ppt_utils.add_image_to_slide(slide, chart_img, left, top, width, height)
            
            elif elem_type == 'table':
                # Create table
                left = elem.get('left', 1.0)
                top = elem.get('top', 1.0)
                width = elem.get('width', 8.0)
                height = elem.get('height', 4.0)
                
                data = elem.get('data', [])
                if not data:
                    continue
                
                # Determine dimensions from data
                rows = len(data)
                cols = max(len(row) for row in data) if data else 2
                rows = max(rows, elem.get('rows', rows))
                cols = max(cols, elem.get('columns', cols))
                
                # Ensure minimum dimensions
                rows = max(2, rows)
                cols = max(2, cols)
                
                try:
                    # Add table shape
                    table_shape = slide.shapes.add_table(rows, cols, Inches(left), Inches(top),
                                                         Inches(width), Inches(height))
                    table = table_shape.table
                    
                    # Populate table data
                    for i, row_data in enumerate(data[:rows]):
                        if not isinstance(row_data, list):
                            row_data = [str(row_data)]
                        
                        for j, cell_data in enumerate(row_data[:cols]):
                            if i < rows and j < cols:
                                cell = table.cell(i, j)
                                cell.text = str(cell_data) if cell_data is not None else ""
                                
                                # Apply header style if first row
                                if i == 0:
                                    para = cell.text_frame.paragraphs[0]
                                    run = para.runs[0] if para.runs else para.add_run()
                                    
                                    header_style = elem.get('header_style', {})
                                    run.font.bold = header_style.get('bold', True)
                                    
                                    if header_style.get('background'):
                                        rgb = ppt_utils.hex_to_rgb(header_style['background'])
                                        if rgb:
                                            cell.fill.solid()
                                            cell.fill.fore_color.rgb = rgb
                                    
                                    # Apply font from header style if provided
                                    if header_style.get('font'):
                                        font_info = ppt_utils.parse_font_info(header_style['font'])
                                        run.font.name = font_info['name']
                                        run.font.size = font_info['size']
                                        run.font.color.rgb = font_info['color']
                                
                                # Apply cell-specific styles if provided
                                cell_styles = elem.get('cell_styles', [])
                                if i < len(cell_styles) and j < len(cell_styles[i]):
                                    cell_style = cell_styles[i][j]
                                    if cell_style:
                                        para = cell.text_frame.paragraphs[0]
                                        run = para.runs[0] if para.runs else para.add_run()
                                        
                                        if cell_style.get('font'):
                                            font_info = ppt_utils.parse_font_info(cell_style['font'])
                                            run.font.name = font_info['name']
                                            run.font.size = font_info['size']
                                            run.font.color.rgb = font_info['color']
                                            run.font.bold = font_info['bold']
                                            run.font.italic = font_info['italic']
                                        
                                        if cell_style.get('background'):
                                            rgb = ppt_utils.hex_to_rgb(cell_style['background'])
                                            if rgb:
                                                cell.fill.solid()
                                                cell.fill.fore_color.rgb = rgb
                
                except Exception as table_error:
                    print(f"    Warning: Error creating table: {table_error}")
                    continue
            
            elif elem_type == 'shape':
                # Add shape
                left = elem.get('left', 0.5)
                top = elem.get('top', 0.5)
                width = elem.get('width', 2.0)
                height = elem.get('height', 1.0)
                shape_type = elem.get('shape_type', 'rectangle')
                fill_color = elem.get('fill_color')
                line_color = elem.get('line_color')
                
                ppt_utils.add_shape_to_slide(slide, shape_type, left, top, width, height,
                                            fill_color, line_color)
        
        except Exception as e:
            print(f"    Warning: Error adding element of type '{elem_type}': {e}")
            continue
    
    return slide
