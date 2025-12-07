"""
PowerPoint utilities for converting PDF pages to PPT slides with preserved formatting,
fonts, styles, and interactive charts.
"""
import os
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path
from PIL import Image
import io
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
import json
import re


def create_presentation() -> Presentation:
    """Creates a new PowerPoint presentation."""
    return Presentation()


def inches_to_emu(value: float) -> int:
    """Convert inches to EMU (English Metric Units) for PowerPoint."""
    return int(value * 914400)


def hex_to_rgb(hex_color: str) -> Optional[RGBColor]:
    """Convert hex color to RGBColor."""
    try:
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return RGBColor(r, g, b)
    except:
        pass
    return None


def parse_font_info(font_info: Dict) -> Dict[str, Any]:
    """Parse font information from AI response."""
    font_name = font_info.get('font_family', 'Calibri')
    font_size = font_info.get('font_size', 18)
    font_color = font_info.get('color', '#000000')
    is_bold = font_info.get('bold', False)
    is_italic = font_info.get('italic', False)
    is_underline = font_info.get('underline', False)
    
    rgb_color = hex_to_rgb(font_color)
    if not rgb_color:
        rgb_color = RGBColor(0, 0, 0)
    
    return {
        'name': font_name,
        'size': Pt(font_size),
        'color': rgb_color,
        'bold': is_bold,
        'italic': is_italic,
        'underline': is_underline
    }


def add_image_to_slide(slide, image: Image.Image, left: float, top: float, 
                       width: float, height: float):
    """Add an image to a slide at specified position and size."""
    img_stream = io.BytesIO()
    image.save(img_stream, format='PNG')
    img_stream.seek(0)
    
    slide.shapes.add_picture(
        img_stream,
        Inches(left),
        Inches(top),
        width=Inches(width),
        height=Inches(height)
    )


def add_text_box(slide, text: str, left: float, top: float, width: float, 
                 height: float, font_info: Dict[str, Any], alignment: str = 'left',
                 multi_paragraph: bool = False):
    """Add a text box to a slide with specified formatting.
    
    If multi_paragraph is True, split text by newlines into separate paragraphs.
    """
    textbox = slide.shapes.add_textbox(
        Inches(left),
        Inches(top),
        Inches(width),
        Inches(height)
    )
    
    text_frame = textbox.text_frame
    text_frame.word_wrap = True
    text_frame.vertical_anchor = MSO_ANCHOR.TOP
    text_frame.margin_left = Inches(0.1)
    text_frame.margin_right = Inches(0.1)
    text_frame.margin_top = Inches(0.05)
    text_frame.margin_bottom = Inches(0.05)
    
    # Set alignment
    align_map = {
        'left': PP_ALIGN.LEFT,
        'center': PP_ALIGN.CENTER,
        'right': PP_ALIGN.RIGHT,
        'justify': PP_ALIGN.JUSTIFY
    }
    alignment_enum = align_map.get(alignment.lower(), PP_ALIGN.LEFT)
    
    # Clear default paragraph
    text_frame.clear()
    
    # Handle multi-paragraph text
    if multi_paragraph and '\n' in text:
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if i > 0:
                p = text_frame.add_paragraph()
            else:
                p = text_frame.paragraphs[0]
            
            p.text = line
            p.alignment = alignment_enum
            
            # Apply formatting to the run
            if p.runs:
                run = p.runs[0]
            else:
                run = p.add_run()
            
            run.font.name = font_info['name']
            run.font.size = font_info['size']
            run.font.color.rgb = font_info['color']
            run.font.bold = font_info['bold']
            run.font.italic = font_info['italic']
            run.font.underline = font_info['underline']
    else:
        # Single paragraph
        p = text_frame.paragraphs[0]
        p.text = text
        p.alignment = alignment_enum
        
        # Apply formatting
        if p.runs:
            run = p.runs[0]
        else:
            run = p.add_run()
        
        run.font.name = font_info['name']
        run.font.size = font_info['size']
        run.font.color.rgb = font_info['color']
        run.font.bold = font_info['bold']
        run.font.italic = font_info['italic']
        run.font.underline = font_info['underline']
    
    return textbox


def create_chart_from_data(slide, chart_data: Dict, left: float, top: float,
                          width: float, height: float) -> Optional[Any]:
    """Create an interactive chart on a slide from chart data."""
    try:
        chart_type_map = {
            'bar': XL_CHART_TYPE.COLUMN_CLUSTERED,
            'column': XL_CHART_TYPE.COLUMN_CLUSTERED,
            'line': XL_CHART_TYPE.LINE,
            'pie': XL_CHART_TYPE.PIE,
            'area': XL_CHART_TYPE.AREA,
            'scatter': XL_CHART_TYPE.XY_SCATTER,
            'bubble': XL_CHART_TYPE.BUBBLE,
            'doughnut': XL_CHART_TYPE.DOUGHNUT,
            'radar': XL_CHART_TYPE.RADAR
        }
        
        # Check both 'type' and 'chart_type' keys
        chart_type_str = chart_data.get('chart_type') or chart_data.get('type', 'column')
        chart_type_str = chart_type_str.lower()
        chart_type = chart_type_map.get(chart_type_str, XL_CHART_TYPE.COLUMN_CLUSTERED)
        
        # Create chart data
        chart_data_obj = CategoryChartData()
        
        # Set categories
        categories = chart_data.get('categories', [])
        if not categories:
            # Generate default categories if none provided
            series_list = chart_data.get('series', [])
            if series_list and len(series_list) > 0:
                first_series = series_list[0]
                values = first_series.get('values', [])
                categories = [f"Category {i+1}" for i in range(len(values))]
        
        chart_data_obj.categories = categories
        
        # Add series
        series_list = chart_data.get('series', [])
        if not series_list:
            # If no series, create a default one
            series_list = [{"name": "Data", "values": [0] * len(categories)}]
        
        for series in series_list:
            series_name = series.get('name', 'Series')
            values = series.get('values', [])
            
            # Ensure values match categories length
            if len(values) != len(categories):
                if len(values) < len(categories):
                    values = values + [0] * (len(categories) - len(values))
                else:
                    values = values[:len(categories)]
            
            chart_data_obj.add_series(series_name, values)
        
        # Add chart to slide
        chart_shape = slide.shapes.add_chart(
            chart_type,
            Inches(left),
            Inches(top),
            Inches(width),
            Inches(height),
            chart_data_obj
        )
        
        # Set chart title if provided
        if chart_data.get('title'):
            chart = chart_shape.chart
            chart.has_title = True
            chart.chart_title.text_frame.text = chart_data['title']
        
        # Configure axes labels if provided
        if chart_type in [XL_CHART_TYPE.COLUMN_CLUSTERED, XL_CHART_TYPE.LINE, XL_CHART_TYPE.AREA]:
            chart = chart_shape.chart
            if chart_data.get('x_axis_label'):
                try:
                    chart.category_axis.axis_title.text_frame.text = chart_data['x_axis_label']
                except:
                    pass
            if chart_data.get('y_axis_label'):
                try:
                    chart.value_axis.axis_title.text_frame.text = chart_data['y_axis_label']
                except:
                    pass
        
        # Configure legend
        chart = chart_shape.chart
        chart.has_legend = chart_data.get('has_legend', True)
        if chart.has_legend and chart_data.get('legend_position'):
            # Note: python-pptx has limited legend position control
            pass
        
        return chart_shape
    except Exception as e:
        print(f"Error creating chart: {e}")
        import traceback
        print(traceback.format_exc())
        return None


def add_shape_to_slide(slide, shape_type: str, left: float, top: float,
                      width: float, height: float, fill_color: Optional[str] = None,
                      line_color: Optional[str] = None):
    """Add a shape to a slide."""
    shape_map = {
        'rectangle': MSO_SHAPE.RECTANGLE,
        'rounded_rectangle': MSO_SHAPE.ROUNDED_RECTANGLE,
        'ellipse': MSO_SHAPE.OVAL,
        'line': MSO_SHAPE.LINE,
        'arrow': MSO_SHAPE.RIGHT_ARROW
    }
    
    shape_enum = shape_map.get(shape_type.lower(), MSO_SHAPE.RECTANGLE)
    
    shape = slide.shapes.add_shape(
        shape_enum,
        Inches(left),
        Inches(top),
        Inches(width),
        Inches(height)
    )
    
    if fill_color:
        rgb = hex_to_rgb(fill_color)
        if rgb:
            fill = shape.fill
            fill.solid()
            fill.fore_color.rgb = rgb
    
    if line_color:
        rgb = hex_to_rgb(line_color)
        if rgb:
            line = shape.line
            line.color.rgb = rgb
    
    return shape


def save_presentation(prs: Presentation, output_path: str):
    """Save the presentation to a file."""
    prs.save(output_path)


def apply_slide_background(slide, background_color: Optional[str] = None,
                          background_image: Optional[Image.Image] = None):
    """Apply background color or image to a slide."""
    background = slide.background
    
    if background_image:
        # Save image temporarily and set as background
        img_stream = io.BytesIO()
        background_image.save(img_stream, format='PNG')
        img_stream.seek(0)
        
        fill = background.fill
        fill.picture()
        fill.picture().image = img_stream
    elif background_color:
        rgb = hex_to_rgb(background_color)
        if rgb:
            fill = background.fill
            fill.solid()
            fill.fore_color.rgb = rgb


def convert_ai_response_to_slide_elements(ai_response: str) -> Dict[str, Any]:
    """
    Parse AI response containing structured slide element information.
    Expected format: JSON with elements array containing text, images, charts, shapes.
    """
    try:
        # Try to extract JSON from the response
        json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return data
        else:
            # Fallback: try to parse as direct JSON
            return json.loads(ai_response)
    except json.JSONDecodeError:
        # If JSON parsing fails, return a basic structure
        return {
            'elements': [],
            'background': None,
            'layout': 'blank'
        }


def create_slide_from_elements(prs: Presentation, elements: List[Dict], 
                               page_image: Image.Image, slide_width: float = 10.0,
                               slide_height: float = 7.5):
    """Create a slide from parsed elements."""
    # Use blank layout
    blank_slide_layout = prs.slide_layouts[6]  # Blank layout
    slide = prs.slides.add_slide(blank_slide_layout)
    
    # Set slide dimensions (standard 16:9)
    prs.slide_width = inches_to_emu(slide_width)
    prs.slide_height = inches_to_emu(slide_height)
    
    # Apply background if specified
    background_info = None
    for elem in elements:
        if elem.get('type') == 'background':
            background_info = elem
            break
    
    if background_info:
        bg_color = background_info.get('color')
        apply_slide_background(slide, background_color=bg_color)
    
    # Process each element
    for elem in elements:
        elem_type = elem.get('type', '')
        
        if elem_type == 'text':
            left = elem.get('left', 0.5)
            top = elem.get('top', 0.5)
            width = elem.get('width', 9.0)
            height = elem.get('height', 1.0)
            text = elem.get('content', '')
            font_info = parse_font_info(elem.get('font', {}))
            alignment = elem.get('alignment', 'left')
            
            add_text_box(slide, text, left, top, width, height, font_info, alignment)
        
        elif elem_type == 'image':
            # For images, we'll use the extracted image region if available
            # Otherwise, use the full page image
            left = elem.get('left', 0.5)
            top = elem.get('top', 0.5)
            width = elem.get('width', 9.0)
            height = elem.get('height', 5.0)
            
            # If we have image coordinates, crop from page_image
            if 'crop' in elem:
                crop = elem['crop']
                x1, y1, x2, y2 = crop['x1'], crop['y1'], crop['x2'], crop['y2']
                img_width, img_height = page_image.size
                cropped = page_image.crop((
                    int(x1 * img_width),
                    int(y1 * img_height),
                    int(x2 * img_width),
                    int(y2 * img_height)
                ))
                add_image_to_slide(slide, cropped, left, top, width, height)
            else:
                add_image_to_slide(slide, page_image, left, top, width, height)
        
        elif elem_type == 'chart':
            left = elem.get('left', 1.0)
            top = elem.get('top', 1.0)
            width = elem.get('width', 8.0)
            height = elem.get('height', 5.0)
            chart_data = elem.get('data', {})
            
            create_chart_from_data(slide, chart_data, left, top, width, height)
        
        elif elem_type == 'shape':
            left = elem.get('left', 0.5)
            top = elem.get('top', 0.5)
            width = elem.get('width', 2.0)
            height = elem.get('height', 1.0)
            shape_type = elem.get('shape_type', 'rectangle')
            fill_color = elem.get('fill_color')
            line_color = elem.get('line_color')
            
            add_shape_to_slide(slide, shape_type, left, top, width, height,
                             fill_color, line_color)
    
    return slide
