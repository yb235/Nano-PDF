from __future__ import annotations

import io
from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean
from typing import Callable, Iterable, List, Optional, Sequence, Tuple, Dict, Any

import fitz
from PIL import Image
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

# Type aliases
BBox = Tuple[float, float, float, float]
RGB = Tuple[int, int, int]


@dataclass
class TextSpan:
    """Represents a contiguous run of text with formatting metadata."""

    text: str
    font: Optional[str]
    size: float
    color: Optional[RGB]
    bold: bool
    italic: bool


@dataclass
class TextLine:
    spans: List[TextSpan] = field(default_factory=list)


@dataclass
class TextBlock:
    bbox: BBox
    lines: List[TextLine]
    alignment: str = "left"  # left, center, right


@dataclass
class ImageBlock:
    bbox: BBox
    image_bytes: bytes
    name: str


@dataclass
class ChartSpec:
    bbox: Dict[str, float]
    chart_type: str
    title: Optional[str]
    categories: List[str]
    series: List[Dict[str, Any]]
    x_axis_label: Optional[str] = None
    y_axis_label: Optional[str] = None


class PDFToPPTConverter:
    """
    Converts PDF pages into editable PowerPoint slides using vector/text extraction.
    """

    def __init__(
        self,
        pdf_path: str,
        background_strategy: str = "average_color",
        embed_page_thumbnail: bool = False,
        slide_width_in: float = 13.33,
        slide_height_in: float = 7.5,
    ) -> None:
        self.pdf_path = Path(pdf_path)
        self._doc = fitz.open(str(self.pdf_path))
        self.background_strategy = background_strategy.lower()
        self.embed_page_thumbnail = embed_page_thumbnail
        self.slide_width_emu = Inches(slide_width_in)
        self.slide_height_emu = Inches(slide_height_in)
        self._blank_layout_index = 6  # Blank layout in default template

    def close(self) -> None:
        if self._doc is not None:
            self._doc.close()
            self._doc = None

    def convert(
        self,
        output_path: str,
        page_numbers: Sequence[int],
        chart_extractor: Optional[Callable[[Image.Image, int], List[Dict[str, Any]]]] = None,
        console: Optional[Callable[[str], None]] = None,
    ) -> None:
        """
        Convert selected pages into a PPTX presentation.
        """
        prs = Presentation()
        prs.slide_width = self.slide_width_emu
        prs.slide_height = self.slide_height_emu

        try:
            for idx, page_number in enumerate(page_numbers, start=1):
                page = self._doc[page_number - 1]
                if console:
                    console(f"→ Building slide {idx}/{len(page_numbers)} (page {page_number})")

                page_image = self._render_page_image(page)
                text_blocks = self._extract_text_blocks(page)
                image_blocks = self._extract_image_blocks(page)
                chart_specs: List[Dict[str, Any]] = []

                if chart_extractor:
                    try:
                        chart_specs = chart_extractor(page_image, page_number) or []
                    except Exception as exc:  # pragma: no cover - defensive
                        if console:
                            console(f"  ⚠️  Chart extraction failed on page {page_number}: {exc}")
                        chart_specs = []

                slide = prs.slides.add_slide(prs.slide_layouts[self._blank_layout_index])

                self._apply_background(slide, page_image)
                self._add_static_page_thumbnail(slide, page_image)
                self._draw_images(slide, image_blocks, page)
                self._draw_charts(slide, chart_specs, page)
                self._draw_text(slide, text_blocks, page)

            prs.save(output_path)
        finally:
            self.close()

    # -------------------------------------------------------------------------
    # Extraction helpers
    # -------------------------------------------------------------------------

    def _extract_text_blocks(self, page: fitz.Page) -> List[TextBlock]:
        text_dict = page.get_text("dict")
        results: List[TextBlock] = []

        for block in text_dict.get("blocks", []):
            if block.get("type") != 0:
                continue

            bbox = tuple(block.get("bbox", (0, 0, 0, 0)))  # type: ignore[arg-type]
            lines_payload = block.get("lines", [])
            lines: List[TextLine] = []

            for line in lines_payload:
                spans_payload = line.get("spans", [])
                spans: List[TextSpan] = []

                for span in spans_payload:
                    text = span.get("text", "")
                    if not text.strip():
                        continue

                    font_name = span.get("font")
                    font_lower = (font_name or "").lower()
                    bold = any(token in font_lower for token in ("bold", "black", "heavy", "semibold"))
                    italic = any(token in font_lower for token in ("italic", "oblique"))

                    spans.append(
                        TextSpan(
                            text=text,
                            font=font_name,
                            size=float(span.get("size", 12.0)),
                            color=self._normalize_color(span.get("color")),
                            bold=bold,
                            italic=italic,
                        )
                    )

                if spans:
                    lines.append(TextLine(spans=spans))

            if lines:
                alignment = self._infer_alignment(block)
                results.append(TextBlock(bbox=bbox, lines=lines, alignment=alignment))

        results.sort(key=lambda blk: (blk.bbox[1], blk.bbox[0]))
        return results

    def _extract_image_blocks(self, page: fitz.Page) -> List[ImageBlock]:
        images: List[ImageBlock] = []
        info_by_xref = {item["xref"]: item for item in page.get_image_info(xrefs=True)}

        for item in page.get_images(full=True):
            xref = item[0]
            if xref not in info_by_xref:
                continue
            bbox = tuple(info_by_xref[xref]["bbox"])  # type: ignore[arg-type]

            pix = fitz.Pixmap(page.parent, xref)
            if pix.samples is None:
                continue

            if pix.n >= 4 and not pix.alpha:  # pragma: no cover - safety
                pix = fitz.Pixmap(fitz.csRGB, pix)
            elif pix.alpha:
                pix = fitz.Pixmap(fitz.csRGB, pix)

            images.append(
                ImageBlock(
                    bbox=bbox,
                    image_bytes=pix.tobytes("png"),
                    name=f"image_{xref}",
                )
            )

        return images

    def _render_page_image(self, page: fitz.Page, zoom: float = 2.0) -> Image.Image:
        matrix = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        mode = "RGB" if pix.n < 4 else "RGBA"
        image = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
        if image.mode != "RGB":
            image = image.convert("RGB")
        return image

    # -------------------------------------------------------------------------
    # Drawing helpers
    # -------------------------------------------------------------------------

    def _draw_text(self, slide, text_blocks: Iterable[TextBlock], page: fitz.Page) -> None:
        for block in text_blocks:
            left, top, width, height = self._scale_bbox(block.bbox, page)
            textbox = slide.shapes.add_textbox(left, top, width, height)
            text_frame = textbox.text_frame
            text_frame.word_wrap = True
            text_frame.clear()

            for line_idx, line in enumerate(block.lines):
                if line_idx == 0:
                    paragraph = text_frame.paragraphs[0]
                    paragraph.text = ""
                else:
                    paragraph = text_frame.add_paragraph()

                paragraph.alignment = self._ppt_alignment(block.alignment)

                for span in line.spans:
                    run = paragraph.add_run()
                    run.text = span.text
                    font = run.font
                    if span.font:
                        font.name = span.font
                    font.size = Pt(span.size)
                    font.bold = span.bold or None
                    font.italic = span.italic or None
                    if span.color:
                        font.color.rgb = RGBColor(*span.color)

    def _draw_images(self, slide, image_blocks: Iterable[ImageBlock], page: fitz.Page) -> None:
        for block in image_blocks:
            left, top, width, height = self._scale_bbox(block.bbox, page)
            stream = io.BytesIO(block.image_bytes)
            stream.seek(0)
            slide.shapes.add_picture(stream, left, top, width=width, height=height)

    def _draw_charts(self, slide, chart_specs: Sequence[Dict[str, Any]], page: fitz.Page) -> None:
        if not chart_specs:
            return

        for spec in chart_specs:
            bbox = spec.get("bounding_box") or spec.get("bbox")
            categories = spec.get("categories") or []
            series_payload = spec.get("series") or []

            if not bbox or not categories or not series_payload:
                continue

            chart_type = self._chart_type_enum(spec.get("chart_type", "bar"))
            left, top, width, height = self._scale_normalized_bbox(bbox)

            data = CategoryChartData()
            data.categories = categories

            for serie in series_payload:
                name = serie.get("name") or "Series"
                values = [self._coerce_float(val) for val in serie.get("values", [])]
                if len(values) < len(categories):
                    values += [values[-1] if values else 0.0] * (len(categories) - len(values))
                data.add_series(name, values)

            chart_shape = slide.shapes.add_chart(chart_type, left, top, width, height, data).chart
            chart_shape.has_legend = True
            chart_shape.legend.include_in_layout = False

            if spec.get("title"):
                chart_shape.has_title = True
                chart_shape.chart_title.text_frame.text = spec["title"]

            if spec.get("x_axis_label"):
                chart_shape.category_axis.has_title = True
                chart_shape.category_axis.axis_title.text_frame.text = spec["x_axis_label"]

            if spec.get("y_axis_label"):
                chart_shape.value_axis.has_title = True
                chart_shape.value_axis.axis_title.text_frame.text = spec["y_axis_label"]

    def _apply_background(self, slide, page_image: Image.Image) -> None:
        strategy = self.background_strategy
        if strategy == "none":
            return

        if strategy == "image":
            stream = self._pil_to_stream(page_image, format="JPEG", quality=85)
            slide.shapes.add_picture(stream, 0, 0, width=self.slide_width_emu, height=self.slide_height_emu)
            return

        avg_color = self._average_color(page_image)
        fill = slide.background.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor(*avg_color)

    def _add_static_page_thumbnail(self, slide, page_image: Image.Image) -> None:
        if not self.embed_page_thumbnail:
            return
        stream = self._pil_to_stream(page_image, format="JPEG", quality=70)
        slide.shapes.add_picture(stream, 0, 0, width=self.slide_width_emu, height=self.slide_height_emu)

    # -------------------------------------------------------------------------
    # Geometry helpers
    # -------------------------------------------------------------------------

    def _scale_bbox(self, bbox: BBox, page: fitz.Page) -> Tuple[int, int, int, int]:
        x0, y0, x1, y1 = bbox
        page_width = page.rect.width
        page_height = page.rect.height

        left = int((x0 / page_width) * self.slide_width_emu)
        top = int((y0 / page_height) * self.slide_height_emu)
        width = max(int(((x1 - x0) / page_width) * self.slide_width_emu), 1)
        height = max(int(((y1 - y0) / page_height) * self.slide_height_emu), 1)
        return left, top, width, height

    def _scale_normalized_bbox(self, bbox: Dict[str, float]) -> Tuple[int, int, int, int]:
        left = max(0.0, min(1.0, float(bbox.get("x", bbox.get("left", 0.0)))))
        top = max(0.0, min(1.0, float(bbox.get("y", bbox.get("top", 0.0)))))
        width = max(0.01, min(1.0, float(bbox.get("width", bbox.get("w", 1.0)))))
        height = max(0.01, min(1.0, float(bbox.get("height", bbox.get("h", 1.0)))))

        return (
            int(left * self.slide_width_emu),
            int(top * self.slide_height_emu),
            int(width * self.slide_width_emu),
            int(height * self.slide_height_emu),
        )

    # -------------------------------------------------------------------------
    # Utility helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def _normalize_color(color_payload: Optional[Sequence[float]]) -> Optional[RGB]:
        if not color_payload:
            return None

        if isinstance(color_payload, (int, float)):
            value = int(color_payload)
            return (
                (value >> 16) & 0xFF,
                (value >> 8) & 0xFF,
                value & 0xFF,
            )

        values = list(color_payload)[:3]
        if not values:
            return None

        if max(values) <= 1:
            scaled = tuple(int(max(0, min(1, val)) * 255) for val in values)
        else:
            scaled = tuple(int(max(0, min(255, val))) for val in values)

        while len(scaled) < 3:
            scaled += (scaled[-1],)

        return scaled[:3]

    @staticmethod
    def _ppt_alignment(alignment: str) -> PP_ALIGN:
        mapping = {
            "center": PP_ALIGN.CENTER,
            "right": PP_ALIGN.RIGHT,
            "justify": PP_ALIGN.JUSTIFY,
        }
        return mapping.get(alignment, PP_ALIGN.LEFT)

    @staticmethod
    def _infer_alignment(block: Dict[str, Any]) -> str:
        align_map = {0: "left", 1: "center", 2: "right", 3: "justify"}
        raw = block.get("alignment")
        if isinstance(raw, int):
            return align_map.get(raw, "left")
        return "left"

    @staticmethod
    def _chart_type_enum(label: str) -> XL_CHART_TYPE:
        lookup = {
            "bar": XL_CHART_TYPE.BAR_CLUSTERED,
            "column": XL_CHART_TYPE.COLUMN_CLUSTERED,
            "line": XL_CHART_TYPE.LINE_MARKERS,
            "area": XL_CHART_TYPE.AREA,
            "pie": XL_CHART_TYPE.PIE,
            "scatter": XL_CHART_TYPE.XY_SCATTER_LINES,
        }
        return lookup.get(label.lower(), XL_CHART_TYPE.COLUMN_CLUSTERED)

    @staticmethod
    def _coerce_float(value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _pil_to_stream(image: Image.Image, format: str = "PNG", quality: int = 90) -> io.BytesIO:
        buffer = io.BytesIO()
        save_kwargs: Dict[str, Any] = {"format": format}
        if format.upper() in {"JPEG", "JPG"}:
            save_kwargs["quality"] = quality
            save_kwargs["optimize"] = True
        image.save(buffer, **save_kwargs)
        buffer.seek(0)
        return buffer

    @staticmethod
    def _average_color(image: Image.Image) -> RGB:
        if image.mode != "RGB":
            image = image.convert("RGB")
        pixels = list(image.resize((32, 32)).getdata())
        if not pixels:
            return (255, 255, 255)
        r = int(mean(pixel[0] for pixel in pixels))
        g = int(mean(pixel[1] for pixel in pixels))
        b = int(mean(pixel[2] for pixel in pixels))
        return (r, g, b)


__all__ = ["PDFToPPTConverter", "ChartSpec"]
