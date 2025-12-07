from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from io import BytesIO
import math
from typing import Dict, List, Optional, Sequence, Set, Tuple

import fitz
from PIL import Image
from pptx import Presentation
from pptx.chart.data import ChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE
from pptx.enum.shapes import MSO_CONNECTOR_TYPE, MSO_SHAPE
from pptx.util import Pt

from nano_pdf import ai_utils


class GraphStrategy(str, Enum):
    IMAGE = "image"
    AUTO = "auto"
    AI = "ai"


@dataclass
class ChartBlueprint:
    chart_type: str
    categories: List[str]
    series: List[Dict[str, Sequence[float]]]
    series_colors: Optional[List[str]] = None
    title: Optional[str] = None
    notes: Optional[str] = None


class PdfToPptConverter:
    """
    Converts PDFs into PPTX decks while attempting to preserve layout, typography, and charts.
    """

    MIN_CHART_DIMENSION = 140  # points

    def __init__(
        self,
        graph_strategy: GraphStrategy = GraphStrategy.AUTO,
        ai_chart_pages: Optional[Set[int]] = None,
        ai_resolution: str = "4K",
        enable_google_search: bool = False,
    ):
        self.graph_strategy = graph_strategy
        self.ai_chart_pages = ai_chart_pages or set()
        self.ai_resolution = ai_resolution
        self.enable_google_search = enable_google_search
        self._diagnostics: List[str] = []

    def convert(self, pdf_path: str, output_pptx_path: str):
        doc = fitz.open(pdf_path)
        if doc.page_count == 0:
            raise ValueError("PDF is empty.")

        presentation = Presentation()
        first_rect = doc[0].rect
        presentation.slide_width = Pt(first_rect.width)
        presentation.slide_height = Pt(first_rect.height)

        for index, page in enumerate(doc):
            page_number = index + 1
            if page.rect != first_rect:
                self._diagnostics.append(
                    f"Page {page_number} has a different size ({page.rect.width}x{page.rect.height}). "
                    "Content will be scaled to the first page dimensions."
                )

            slide = presentation.slides.add_slide(presentation.slide_layouts[6])
            self._draw_vector_graphics(slide, page, page_number)
            page_dict = page.get_text("dict")
            self._draw_images(slide, page_dict.get("blocks", []), page_number)
            self._draw_text_blocks(slide, page_dict.get("blocks", []))

        presentation.save(output_pptx_path)

    @property
    def diagnostics(self) -> List[str]:
        return list(self._diagnostics)

    def _draw_text_blocks(self, slide, blocks: List[dict]):
        for block in blocks:
            if block.get("type") != 0:
                continue
            bbox = block.get("bbox")
            lines = block.get("lines", [])
            if not bbox or not lines:
                continue

            left, top, right, bottom = bbox
            width = max(right - left, 1)
            height = max(bottom - top, 1)

            textbox = slide.shapes.add_textbox(Pt(left), Pt(top), Pt(width), Pt(height))
            text_frame = textbox.text_frame
            text_frame.clear()
            text_frame.margin_left = 0
            text_frame.margin_right = 0
            text_frame.margin_top = 0
            text_frame.margin_bottom = 0

            for line_index, line in enumerate(lines):
                spans = line.get("spans", [])
                if not spans:
                    continue

                if line_index == 0:
                    paragraph = text_frame.paragraphs[0]
                    paragraph.text = ""
                else:
                    paragraph = text_frame.add_paragraph()

                # Default to left alignment. Vertical alignment inherits from textbox.
                for span in spans:
                    text = span.get("text", "")
                    if not text:
                        continue
                    run = paragraph.add_run()
                    run.text = text
                    font = run.font
                    font.name = span.get("font") or "Helvetica"
                    font.size = Pt(max(span.get("size") or 12, 1))

                    rgb = self._decode_span_color(span.get("color"))
                    if rgb:
                        font.color.rgb = RGBColor(*rgb)

                    font_name_lower = (span.get("font") or "").lower()
                    if any(tag in font_name_lower for tag in ("bold", "black", "heavy")):
                        font.bold = True
                    if any(tag in font_name_lower for tag in ("italic", "oblique")):
                        font.italic = True

    def _draw_images(self, slide, blocks: List[dict], page_number: int):
        for block in blocks:
            if block.get("type") != 1:
                continue
            bbox = block.get("bbox")
            raw_image = block.get("image")
            if not bbox or raw_image is None:
                continue

            try:
                image = Image.open(BytesIO(raw_image)).convert("RGBA")
            except Exception:
                self._diagnostics.append(f"Failed to decode image on page {page_number}")
                continue

            if self._should_attempt_chart(page_number, bbox, image):
                if self._try_add_chart(slide, bbox, image, page_number):
                    continue

            stream = BytesIO()
            image.save(stream, format="PNG")
            stream.seek(0)
            left, top, right, bottom = bbox
            width = max(right - left, 1)
            height = max(bottom - top, 1)
            slide.shapes.add_picture(stream, Pt(left), Pt(top), Pt(width), Pt(height))

    def _draw_vector_graphics(self, slide, page: fitz.Page, page_number: int):
        for drawing in page.get_drawings():
            fill_color = self._color_tuple_to_rgb(drawing.get("fill"))
            stroke_color = self._color_tuple_to_rgb(drawing.get("color"))
            stroke_width = drawing.get("width", 1.0)

            for item in drawing.get("items", []):
                op = item[0]
                if op == "re":
                    rect = item[1]
                    shape = slide.shapes.add_shape(
                        MSO_SHAPE.RECTANGLE,
                        Pt(rect.x0),
                        Pt(rect.y0),
                        Pt(max(rect.width, 1)),
                        Pt(max(rect.height, 1)),
                    )
                    if fill_color:
                        shape.fill.solid()
                        shape.fill.fore_color.rgb = RGBColor(*fill_color)
                    else:
                        shape.fill.background()
                    if stroke_color:
                        line = shape.line
                        line.width = Pt(max(stroke_width, 0.5))
                        line.color.rgb = RGBColor(*stroke_color)
                    continue

                if op == "l":
                    start, end = item[1], item[2]
                    connector = slide.shapes.add_connector(
                        MSO_CONNECTOR_TYPE.STRAIGHT, Pt(start.x), Pt(start.y), Pt(end.x), Pt(end.y)
                    )
                    if stroke_color:
                        connector.line.color.rgb = RGBColor(*stroke_color)
                    connector.line.width = Pt(max(stroke_width, 0.5))
                    continue

                # Other vector instructions are currently unsupported
                self._diagnostics.append(
                    f"Skipped vector op '{op}' on page {page_number}; rendered chart/image will cover it."
                )

    def _should_attempt_chart(self, page_number: int, bbox: Sequence[float], image: Image.Image) -> bool:
        if self.graph_strategy == GraphStrategy.IMAGE:
            return False
        if self.ai_chart_pages and page_number not in self.ai_chart_pages:
            # Explicit user selection overrides heuristics
            return False

        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        if width < self.MIN_CHART_DIMENSION or height < self.MIN_CHART_DIMENSION:
            return False

        # AUTO mode uses entropy to avoid targeting logos/photos
        if self.graph_strategy == GraphStrategy.AUTO:
            entropy = self._entropy(image)
            return entropy > 3.5

        return True

    def _entropy(self, image: Image.Image) -> float:
        grayscale = image.convert("L")
        histogram = grayscale.histogram()
        total = float(sum(histogram))
        if total == 0:
            return 0.0
        entropy = 0.0
        for count in histogram:
            if count == 0:
                continue
            probability = count / total
            entropy -= probability * math.log2(probability)
        return entropy

    def _try_add_chart(self, slide, bbox: Sequence[float], image: Image.Image, page_number: int) -> bool:
        try:
            raw_blueprint = ai_utils.extract_chart_blueprint(
                chart_image=image,
                resolution=self.ai_resolution,
                enable_search=self.enable_google_search,
            )
        except Exception as exc:
            self._diagnostics.append(
                f"AI chart extraction failed on page {page_number}: {exc}. Falling back to embedding the image."
            )
            return False

        if not raw_blueprint:
            return False

        blueprint = ChartBlueprint(
            chart_type=raw_blueprint.get("chart_type", "column"),
            categories=raw_blueprint.get("categories", []),
            series=raw_blueprint.get("series", []),
            series_colors=raw_blueprint.get("series_colors"),
            title=raw_blueprint.get("title"),
            notes=raw_blueprint.get("notes"),
        )

        chart_type = self._map_chart_type(blueprint.chart_type)
        if not chart_type:
            self._diagnostics.append(
                f"Unsupported chart type '{blueprint.chart_type}' on page {page_number}. Using static image instead."
            )
            return False

        if not blueprint.categories or not blueprint.series:
            self._diagnostics.append(
                f"Incomplete chart data on page {page_number}; categories or series missing."
            )
            return False

        try:
            chart_data = ChartData()
            chart_data.categories = blueprint.categories
            for series in blueprint.series:
                name = series.get("name") or "Series"
                values = [float(v) for v in series.get("values", [])]
                chart_data.add_series(name, values)

            left, top, right, bottom = bbox
            width = max(right - left, 1)
            height = max(bottom - top, 1)
            chart_shape = slide.shapes.add_chart(
                chart_type, Pt(left), Pt(top), Pt(width), Pt(height), chart_data
            )
            chart = chart_shape.chart

            if blueprint.title:
                chart.has_title = True
                chart.chart_title.text_frame.text = blueprint.title

            if blueprint.series_colors:
                for series_obj, color_hex in zip(chart.series, blueprint.series_colors):
                    rgb = self._hex_to_rgb(color_hex)
                    if rgb:
                        fill = series_obj.format.fill
                        fill.solid()
                        fill.fore_color.rgb = RGBColor(*rgb)

            return True
        except Exception as exc:
            self._diagnostics.append(
                f"Failed to build live chart on page {page_number}: {exc}. Reverting to static image."
            )
            return False

    def _map_chart_type(self, label: str) -> Optional[XL_CHART_TYPE]:
        normalized = (label or "").strip().lower()
        mapping = {
            "column": XL_CHART_TYPE.COLUMN_CLUSTERED,
            "clustered_column": XL_CHART_TYPE.COLUMN_CLUSTERED,
            "stacked_column": XL_CHART_TYPE.COLUMN_STACKED,
            "bar": XL_CHART_TYPE.BAR_CLUSTERED,
            "stacked_bar": XL_CHART_TYPE.BAR_STACKED,
            "line": XL_CHART_TYPE.LINE_MARKERS,
            "area": XL_CHART_TYPE.AREA,
            "pie": XL_CHART_TYPE.PIE,
            "donut": XL_CHART_TYPE.DOUGHNUT,
            "doughnut": XL_CHART_TYPE.DOUGHNUT,
        }
        return mapping.get(normalized)

    def _hex_to_rgb(self, value: Optional[str]) -> Optional[Tuple[int, int, int]]:
        if not value:
            return None
        hex_value = value.strip().lstrip("#")
        if len(hex_value) not in (6, 3):
            return None
        if len(hex_value) == 3:
            hex_value = "".join(ch * 2 for ch in hex_value)
        try:
            r = int(hex_value[0:2], 16)
            g = int(hex_value[2:4], 16)
            b = int(hex_value[4:6], 16)
            return (r, g, b)
        except ValueError:
            return None

    def _decode_span_color(self, value) -> Optional[Tuple[int, int, int]]:
        if value is None:
            return None
        if isinstance(value, int):
            r = (value >> 16) & 255
            g = (value >> 8) & 255
            b = value & 255
            return (r, g, b)
        if isinstance(value, (tuple, list)):
            if len(value) >= 3:
                return tuple(int(min(max(component, 0), 1) * 255) for component in value[:3])
        return None

    def _color_tuple_to_rgb(self, value) -> Optional[Tuple[int, int, int]]:
        if value is None:
            return None
        if isinstance(value, (tuple, list)):
            return tuple(int(min(max(component, 0), 1) * 255) for component in value[:3])
        return self._decode_span_color(value)
