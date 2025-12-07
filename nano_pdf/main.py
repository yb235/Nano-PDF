import typer
from typing import List, Optional
from pathlib import Path
from nano_pdf import pdf_utils, ai_utils
from nano_pdf.ppt_converter import (
    PDFToPPTConverter,
    ConversionOptions,
    convert_pdf_to_pptx,
    convert_pdf_to_pptx_with_ai
)
import concurrent.futures
import tempfile

app = typer.Typer(
    name="nano-pdf",
    help="Nano PDF Editor - Edit PDFs and convert to PowerPoint using AI (Gemini)",
    add_completion=False
)

@app.command()
def edit(
    pdf_path: str = typer.Argument(..., help="Path to the PDF file"),
    edits: List[str] = typer.Argument(..., help="Pairs of 'PageNumber Prompt' (e.g. 1 'Fix typo' 2 'Make blue')"),
    style_refs: Optional[str] = typer.Option(None, help="Comma-separated list of extra reference page numbers (e.g. '5,6')"),
    use_context: bool = typer.Option(False, help="Include full PDF text as context (can confuse the model)"),
    output: Optional[str] = typer.Option(None, help="Output path for the edited PDF. Defaults to 'edited_<filename>'"),
    resolution: str = typer.Option("4K", help="Image resolution: '4K', '2K', '1K' (higher = better quality but slower)"),
    disable_google_search: bool = typer.Option(False, help="Disable Google Search (enabled by default)")
):
    """
    Edit a PDF page using Nano Banana (Gemini 3 Pro Image).
    Usage: python -m src.main edit deck.pdf 1 "prompt A" 2 "prompt B"
    """
    # Check system dependencies first
    try:
        pdf_utils.check_system_dependencies()
    except RuntimeError as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(code=1)

    input_path = Path(pdf_path)
    if not input_path.exists():
        typer.echo(f"Error: File {pdf_path} not found.")
        raise typer.Exit(code=1)

    if not output:
        output = f"edited_{input_path.name}"
    
    # Parse Edits
    if len(edits) % 2 != 0:
        typer.echo("Error: Edits must be pairs of 'PageNumber Prompt'.")
        raise typer.Exit(code=1)

    # Merge duplicate page edits into a single prompt
    edits_by_page = {}
    for i in range(0, len(edits), 2):
        try:
            p_num = int(edits[i])
            prompt = edits[i+1]
            if p_num in edits_by_page:
                # Merge prompts with separator
                edits_by_page[p_num] += f"\n\nALSO: {prompt}"
            else:
                edits_by_page[p_num] = prompt
        except ValueError:
            typer.echo(f"Error: Invalid page number '{edits[i]}'")
            raise typer.Exit(code=1)

    parsed_edits = list(edits_by_page.items())

    # Validate page numbers are within range
    total_pages = pdf_utils.get_page_count(str(input_path))
    invalid_pages = [p for p, _ in parsed_edits if p < 1 or p > total_pages]
    if invalid_pages:
        typer.echo(f"Error: Invalid page number(s) {invalid_pages}. PDF has {total_pages} pages.")
        raise typer.Exit(code=1)

    typer.echo(f"Processing {pdf_path} with {len(parsed_edits)} edits...")
    
    # 1. Extract Full Text Context (Once)
    full_text = ""
    if use_context:
        typer.echo("Extracting text context...")
        full_text = pdf_utils.extract_full_text(str(input_path))
        if not full_text:
            typer.echo("Warning: Could not extract text from PDF. Context will be limited.")
    else:
        typer.echo("Skipping text context (use --use-context to enable)...")
    
    # 2. Prepare Visual Context (Style Anchors)
    typer.echo("Rendering reference images...")
    style_images = []
    
    # Add user-defined style refs
    if style_refs:
        for ref_page in style_refs.split(','):
            try:
                p_num = int(ref_page.strip())
                style_images.append(pdf_utils.render_page_as_image(str(input_path), p_num))
            except ValueError:
                typer.echo(f"Warning: Invalid style ref '{ref_page}'")
            except Exception as e:
                typer.echo(f"Warning: Could not render Page {ref_page}: {e}")

    # 3. Process Each Edit (Parallel)
    replacements = {} # page_num -> temp_pdf_path
    temp_files = []

    def process_single_page(page_num: int, prompt_text: str):
        typer.echo(f"Starting Page {page_num}...")
        try:
            target_image = pdf_utils.render_page_as_image(str(input_path), page_num)
            
            # Generate
            generated_image, response_text = ai_utils.generate_edited_slide(
                target_image=target_image,
                style_reference_images=style_images,
                full_text_context=full_text,
                user_prompt=prompt_text,
                resolution=resolution,
                enable_search=not disable_google_search
            )

            # Print model's text response if any
            if response_text:
                typer.echo(f"Model response for page {page_num}: {response_text}")

            # Re-hydrate
            temp_pdf_file = tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False)
            temp_pdf = temp_pdf_file.name
            temp_pdf_file.close()
            pdf_utils.rehydrate_image_to_pdf(generated_image, temp_pdf)
            
            typer.echo(f"Finished Page {page_num}")
            return (page_num, temp_pdf)
        except Exception as e:
            typer.echo(f"Error processing Page {page_num}: {e}")
            return None

    typer.echo(f"Processing {len(parsed_edits)} pages in parallel...")

    completed_count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_single_page, p, prompt) for p, prompt in parsed_edits]

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                p_num, temp_pdf = result
                replacements[p_num] = temp_pdf
                temp_files.append(temp_pdf)
            completed_count += 1
            typer.echo(f"Progress: {completed_count}/{len(parsed_edits)} pages completed")

    if not replacements:
        typer.echo("No pages were successfully processed.")
        raise typer.Exit(code=1)

    # 4. Batch Stitch
    typer.echo(f"\nStitching {len(replacements)} pages into final PDF...")
    try:
        pdf_utils.batch_replace_pages(str(input_path), replacements, output)
    except Exception as e:
        typer.echo(f"Error stitching PDF: {e}")
        raise typer.Exit(code=1)
    finally:
        # Cleanup
        for f in temp_files:
            if Path(f).exists():
                Path(f).unlink()

    typer.echo(f"Done! Saved to {output}")

@app.command()
def add(
    pdf_path: str = typer.Argument(..., help="Path to the PDF file"),
    after_page: int = typer.Argument(..., help="Insert after this page number (0 for beginning)"),
    prompt: str = typer.Argument(..., help="Description of the new slide to create"),
    style_refs: Optional[str] = typer.Option(None, help="Comma-separated list of reference page numbers for style (e.g. '1,2'). Defaults to first page."),
    use_context: bool = typer.Option(True, help="Include full PDF text as context (enabled by default for better slide generation)"),
    output: Optional[str] = typer.Option(None, help="Output path for the PDF. Defaults to 'edited_<filename>'"),
    resolution: str = typer.Option("4K", help="Image resolution: '4K', '2K', '1K' (higher = better quality but slower)"),
    disable_google_search: bool = typer.Option(False, help="Disable Google Search (enabled by default)")
):
    """
    Add a new slide to a PDF using AI generation.
    Usage: nano-pdf add deck.pdf 0 "Title slide with 'Welcome to Q3 Review'"
    """
    # Check system dependencies first
    try:
        pdf_utils.check_system_dependencies()
    except RuntimeError as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(code=1)

    input_path = Path(pdf_path)
    if not input_path.exists():
        typer.echo(f"Error: File {pdf_path} not found.")
        raise typer.Exit(code=1)

    if not output:
        output = f"edited_{input_path.name}"

    # Validate after_page
    total_pages = pdf_utils.get_page_count(str(input_path))
    if after_page < 0 or after_page > total_pages:
        typer.echo(f"Error: after_page must be between 0 and {total_pages}. Use 0 to insert at the beginning.")
        raise typer.Exit(code=1)

    typer.echo(f"Adding new slide to {pdf_path} after page {after_page}...")

    # Extract text context
    full_text = ""
    if use_context:
        typer.echo("Extracting text context...")
        full_text = pdf_utils.extract_full_text(str(input_path))
        if not full_text:
            typer.echo("Warning: Could not extract text from PDF. Context will be limited.")

    # Prepare style references
    typer.echo("Rendering style reference images...")
    style_images = []

    if style_refs:
        for ref_page in style_refs.split(','):
            try:
                p_num = int(ref_page.strip())
                if p_num < 1 or p_num > total_pages:
                    typer.echo(f"Warning: Style ref page {p_num} out of range, skipping")
                    continue
                style_images.append(pdf_utils.render_page_as_image(str(input_path), p_num))
            except ValueError:
                typer.echo(f"Warning: Invalid style ref '{ref_page}'")
            except Exception as e:
                typer.echo(f"Warning: Could not render Page {ref_page}: {e}")
    else:
        # Default to first page as style reference
        typer.echo("Using page 1 as default style reference...")
        try:
            style_images.append(pdf_utils.render_page_as_image(str(input_path), 1))
        except Exception as e:
            typer.echo(f"Warning: Could not render Page 1: {e}")

    # Generate the new slide
    typer.echo("Generating new slide with AI...")
    try:
        generated_image, response_text = ai_utils.generate_new_slide(
            style_reference_images=style_images,
            user_prompt=prompt,
            full_text_context=full_text,
            resolution=resolution,
            enable_search=not disable_google_search
        )
    except Exception as e:
        typer.echo(f"Error generating slide: {e}")
        raise typer.Exit(code=1)

    # Print model's text response if any
    if response_text:
        typer.echo(f"Model response: {response_text}")

    # Re-hydrate to PDF
    typer.echo("Converting to PDF with text layer...")
    temp_pdf_file = tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False)
    temp_pdf = temp_pdf_file.name
    temp_pdf_file.close()

    try:
        pdf_utils.rehydrate_image_to_pdf(generated_image, temp_pdf)

        # Insert into the PDF
        typer.echo("Inserting slide into PDF...")
        pdf_utils.insert_page(str(input_path), temp_pdf, after_page, output)
    except Exception as e:
        typer.echo(f"Error creating PDF: {e}")
        raise typer.Exit(code=1)
    finally:
        # Cleanup
        if Path(temp_pdf).exists():
            Path(temp_pdf).unlink()

    typer.echo(f"Done! New slide added after page {after_page}. Saved to {output}")

@app.command()
def toppt(
    pdf_path: str = typer.Argument(..., help="Path to the PDF file to convert"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output path for the PPTX file. Defaults to '<filename>.pptx'"),
    pages: Optional[str] = typer.Option(None, "--pages", "-p", help="Comma-separated page numbers to convert (e.g. '1,2,5-10'). Defaults to all pages."),
    extract_charts: bool = typer.Option(True, "--extract-charts/--no-extract-charts", help="Extract charts as editable PowerPoint charts (uses AI)"),
    extract_tables: bool = typer.Option(True, "--extract-tables/--no-extract-tables", help="Extract tables as editable PowerPoint tables"),
    preserve_fonts: bool = typer.Option(True, "--preserve-fonts/--no-preserve-fonts", help="Attempt to match original fonts"),
    use_ai: bool = typer.Option(True, "--use-ai/--no-use-ai", help="Use AI for intelligent element extraction"),
    resolution: str = typer.Option("4K", "--resolution", "-r", help="Image resolution for AI analysis: '4K', '2K', '1K'"),
    fallback_to_image: bool = typer.Option(True, "--fallback-to-image/--no-fallback-to-image", help="Fall back to image if element extraction fails"),
    parallel: bool = typer.Option(True, "--parallel/--no-parallel", help="Process pages in parallel for speed"),
    max_workers: int = typer.Option(5, "--max-workers", help="Maximum parallel workers (1-10)")
):
    """
    Convert PDF to PowerPoint (PPTX) with editable elements.
    
    This command converts a PDF presentation to a PowerPoint file, attempting to:
    - Preserve fonts, colors, and styling exactly
    - Extract charts as editable PowerPoint charts (with data!)
    - Extract tables as editable PowerPoint tables
    - Maintain text as editable text boxes
    - Keep images in their original positions
    
    Uses Nano Banana Pro Magic (Gemini AI) for intelligent chart data extraction
    and element detection.
    
    Examples:
    
        # Convert entire PDF to PPT
        nano-pdf toppt presentation.pdf
        
        # Convert specific pages
        nano-pdf toppt report.pdf --pages "1,3,5-10"
        
        # Convert without AI (faster, basic extraction)
        nano-pdf toppt slides.pdf --no-use-ai
        
        # Convert with custom output name
        nano-pdf toppt deck.pdf -o my_presentation.pptx
        
        # High-quality conversion (slower)
        nano-pdf toppt important.pdf --resolution 4K --extract-charts
    """
    # Check system dependencies first
    try:
        pdf_utils.check_system_dependencies()
    except RuntimeError as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(code=1)

    input_path = Path(pdf_path)
    if not input_path.exists():
        typer.echo(f"Error: File {pdf_path} not found.")
        raise typer.Exit(code=1)

    # Set output path
    if not output:
        output = str(input_path.with_suffix('.pptx'))
    
    # Parse page numbers
    page_list = None
    if pages:
        page_list = _parse_page_range(pages)
        if not page_list:
            typer.echo(f"Error: Invalid page specification '{pages}'")
            raise typer.Exit(code=1)
        
        # Validate page numbers
        total_pages = pdf_utils.get_page_count(str(input_path))
        invalid = [p for p in page_list if p < 1 or p > total_pages]
        if invalid:
            typer.echo(f"Error: Invalid page numbers {invalid}. PDF has {total_pages} pages.")
            raise typer.Exit(code=1)
    
    # Validate max_workers
    max_workers = max(1, min(10, max_workers))
    
    # Create conversion options
    options = ConversionOptions(
        extract_charts=extract_charts,
        extract_tables=extract_tables,
        preserve_fonts=preserve_fonts,
        use_ai_extraction=use_ai,
        resolution=resolution,
        fallback_to_image=fallback_to_image,
        parallel_processing=parallel,
        max_workers=max_workers
    )
    
    # Progress callback
    def progress_callback(current: int, total: int, message: str):
        if total > 0:
            pct = (current / total) * 100
            typer.echo(f"[{pct:5.1f}%] {message}")
        else:
            typer.echo(message)
    
    typer.echo(f"\n{'='*60}")
    typer.echo(f"  Nano PDF to PowerPoint Converter")
    typer.echo(f"  Powered by Nano Banana Pro Magic (Gemini AI)")
    typer.echo(f"{'='*60}\n")
    
    typer.echo(f"Input:  {pdf_path}")
    typer.echo(f"Output: {output}")
    
    if page_list:
        typer.echo(f"Pages:  {len(page_list)} selected")
    else:
        total = pdf_utils.get_page_count(str(input_path))
        typer.echo(f"Pages:  All ({total} pages)")
    
    typer.echo(f"\nOptions:")
    typer.echo(f"  - Extract charts: {'Yes (AI)' if extract_charts and use_ai else 'Yes' if extract_charts else 'No'}")
    typer.echo(f"  - Extract tables: {'Yes' if extract_tables else 'No'}")
    typer.echo(f"  - Preserve fonts: {'Yes' if preserve_fonts else 'No'}")
    typer.echo(f"  - AI extraction:  {'Yes' if use_ai else 'No'}")
    typer.echo(f"  - Resolution:     {resolution}")
    typer.echo(f"  - Parallel:       {'Yes (' + str(max_workers) + ' workers)' if parallel else 'No'}")
    typer.echo(f"  - Image fallback: {'Yes' if fallback_to_image else 'No'}")
    typer.echo()
    
    try:
        converter = PDFToPPTConverter(options)
        result_path = converter.convert(
            pdf_path=str(input_path),
            output_path=output,
            pages=page_list,
            progress_callback=progress_callback
        )
        
        typer.echo(f"\n{'='*60}")
        typer.echo(f"  Conversion Complete!")
        typer.echo(f"{'='*60}")
        typer.echo(f"\nSaved to: {result_path}")
        typer.echo("\nTips:")
        typer.echo("  - Open in PowerPoint to edit charts, tables, and text")
        typer.echo("  - Charts extracted by AI contain real data - fully editable!")
        typer.echo("  - Some complex graphics may be preserved as images")
        
    except Exception as e:
        typer.echo(f"\nError during conversion: {e}")
        raise typer.Exit(code=1)


def _parse_page_range(page_spec: str) -> Optional[List[int]]:
    """
    Parse page specification string into list of page numbers.
    
    Examples:
        "1,2,3" -> [1, 2, 3]
        "1-5" -> [1, 2, 3, 4, 5]
        "1,3,5-10" -> [1, 3, 5, 6, 7, 8, 9, 10]
    """
    pages = []
    try:
        parts = page_spec.replace(" ", "").split(",")
        for part in parts:
            if "-" in part:
                start, end = part.split("-", 1)
                start = int(start)
                end = int(end)
                if start > end:
                    start, end = end, start
                pages.extend(range(start, end + 1))
            else:
                pages.append(int(part))
        
        # Remove duplicates and sort
        pages = sorted(set(pages))
        return pages if pages else None
    except (ValueError, AttributeError):
        return None


@app.command()
def analyze(
    pdf_path: str = typer.Argument(..., help="Path to the PDF file to analyze"),
    page: int = typer.Option(1, "--page", "-p", help="Page number to analyze (1-indexed)"),
    output_json: Optional[str] = typer.Option(None, "--output-json", "-o", help="Save analysis results to JSON file")
):
    """
    Analyze a PDF page to detect elements (charts, tables, text, images).
    
    This is useful for previewing what elements will be extracted during
    conversion, and for debugging extraction issues.
    
    Examples:
    
        # Analyze first page
        nano-pdf analyze presentation.pdf
        
        # Analyze specific page
        nano-pdf analyze report.pdf --page 5
        
        # Save results to JSON
        nano-pdf analyze deck.pdf -o analysis.json
    """
    import json
    
    input_path = Path(pdf_path)
    if not input_path.exists():
        typer.echo(f"Error: File {pdf_path} not found.")
        raise typer.Exit(code=1)
    
    total_pages = pdf_utils.get_page_count(str(input_path))
    if page < 1 or page > total_pages:
        typer.echo(f"Error: Page {page} is out of range. PDF has {total_pages} pages.")
        raise typer.Exit(code=1)
    
    typer.echo(f"\nAnalyzing page {page} of {pdf_path}...")
    typer.echo("Using AI to detect elements...")
    
    try:
        # Render page
        page_image = pdf_utils.render_page_as_image(str(input_path), page)
        
        # Get comprehensive analysis
        analysis = ai_utils.extract_slide_content_comprehensive(page_image)
        
        if not analysis:
            typer.echo("\nNo elements detected or analysis failed.")
            raise typer.Exit(code=1)
        
        # Display results
        typer.echo(f"\n{'='*60}")
        typer.echo(f"  Analysis Results - Page {page}")
        typer.echo(f"{'='*60}\n")
        
        # Slide properties
        if "slide_properties" in analysis:
            props = analysis["slide_properties"]
            typer.echo("SLIDE PROPERTIES:")
            typer.echo(f"  Background: {props.get('background_color', 'N/A')}")
            if props.get('theme_colors'):
                typer.echo(f"  Theme Colors: {', '.join(props['theme_colors'][:5])}")
            typer.echo()
        
        # Text elements
        if "text_elements" in analysis and analysis["text_elements"]:
            typer.echo(f"TEXT ELEMENTS ({len(analysis['text_elements'])}):")
            for i, elem in enumerate(analysis["text_elements"][:10]):  # Show first 10
                text_preview = elem.get("text", "")[:50]
                if len(elem.get("text", "")) > 50:
                    text_preview += "..."
                elem_type = elem.get("type", "text")
                typer.echo(f"  {i+1}. [{elem_type}] \"{text_preview}\"")
            if len(analysis["text_elements"]) > 10:
                typer.echo(f"  ... and {len(analysis['text_elements']) - 10} more")
            typer.echo()
        
        # Charts
        if "charts" in analysis and analysis["charts"]:
            typer.echo(f"CHARTS ({len(analysis['charts'])}):")
            for i, chart in enumerate(analysis["charts"]):
                chart_type = chart.get("type", "unknown")
                title = chart.get("title", "Untitled")
                series_count = len(chart.get("series", []))
                cat_count = len(chart.get("categories", []))
                typer.echo(f"  {i+1}. {chart_type.upper()} chart: \"{title}\"")
                typer.echo(f"     - {series_count} data series, {cat_count} categories")
                if chart.get("series"):
                    for s in chart["series"][:3]:
                        vals = s.get("values", [])[:5]
                        typer.echo(f"     - Series \"{s.get('name', 'unnamed')}\": {vals}{'...' if len(s.get('values', [])) > 5 else ''}")
            typer.echo()
        
        # Tables
        if "tables" in analysis and analysis["tables"]:
            typer.echo(f"TABLES ({len(analysis['tables'])}):")
            for i, table in enumerate(analysis["tables"]):
                rows = table.get("rows", [])
                row_count = len(rows)
                col_count = len(rows[0]) if rows else 0
                typer.echo(f"  {i+1}. Table: {row_count} rows x {col_count} columns")
            typer.echo()
        
        # Images
        if "images" in analysis and analysis["images"]:
            typer.echo(f"IMAGES ({len(analysis['images'])}):")
            for i, img in enumerate(analysis["images"]):
                desc = img.get("description", "No description")[:60]
                img_type = img.get("type", "image")
                typer.echo(f"  {i+1}. [{img_type}] {desc}")
            typer.echo()
        
        # Shapes
        if "shapes" in analysis and analysis["shapes"]:
            typer.echo(f"SHAPES ({len(analysis['shapes'])}):")
            for i, shape in enumerate(analysis["shapes"][:5]):
                shape_type = shape.get("type", "shape")
                fill = shape.get("fill_color", "none")
                typer.echo(f"  {i+1}. {shape_type} (fill: {fill})")
            if len(analysis["shapes"]) > 5:
                typer.echo(f"  ... and {len(analysis['shapes']) - 5} more")
            typer.echo()
        
        # Save to JSON if requested
        if output_json:
            with open(output_json, 'w') as f:
                json.dump(analysis, f, indent=2)
            typer.echo(f"Analysis saved to: {output_json}")
        
    except Exception as e:
        typer.echo(f"\nError during analysis: {e}")
        raise typer.Exit(code=1)


@app.command()
def version():
    """
    Show version information.
    """
    typer.echo("\n  Nano PDF Editor v0.3.0")
    typer.echo("  Powered by Gemini 3 Pro Image (Nano Banana)")
    typer.echo("\n  Features:")
    typer.echo("    - Edit PDF slides with natural language")
    typer.echo("    - Add new slides to existing decks")
    typer.echo("    - Convert PDF to PowerPoint with editable charts")
    typer.echo("    - Analyze slide content with AI")
    typer.echo("\n  https://github.com/gavrielc/Nano-PDF")
    typer.echo()


if __name__ == "__main__":
    app()
