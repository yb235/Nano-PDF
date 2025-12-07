# Nano PDF Architecture

This document provides a comprehensive overview of Nano PDF's architecture, design decisions, and implementation details.

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Core Components](#core-components)
- [Data Flow](#data-flow)
- [Design Decisions](#design-decisions)
- [Technology Stack](#technology-stack)
- [Performance Considerations](#performance-considerations)
- [Security Considerations](#security-considerations)

## Overview

Nano PDF is a command-line tool that enables natural language editing of PDF files using Google's Gemini 3 Pro Image (codenamed "Nano Banana") model. The tool combines computer vision AI, PDF manipulation, and OCR to provide a seamless editing experience while preserving document quality and searchability.

### Core Capabilities

1. **Natural Language Editing**: Edit PDF pages using plain English instructions
2. **New Slide Generation**: Create new slides that match the existing visual style
3. **Text Preservation**: Maintain searchable text layer through OCR re-hydration
4. **Parallel Processing**: Process multiple pages concurrently for efficiency
5. **Style Consistency**: Use reference pages to maintain visual coherence

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                           │
│                     (Typer CLI - main.py)                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ├─── edit command
                         ├─── add command
                         └─── version command
                         │
         ┌───────────────┴────────────────┐
         │                                 │
┌────────▼─────────┐            ┌────────▼──────────┐
│   PDF Utilities  │            │   AI Utilities    │
│  (pdf_utils.py)  │            │ (ai_utils.py)     │
└──────────────────┘            └───────────────────┘
         │                                 │
         │                                 │
┌────────▼─────────────────┐    ┌────────▼──────────────────────┐
│  External Dependencies    │    │    Gemini API                 │
│  - poppler (PDF→Image)    │    │  - Gemini 3 Pro Image Model  │
│  - tesseract (OCR)        │    │  - Google Search (optional)   │
│  - pypdf (PDF manipulation)│    │                               │
└──────────────────────────┘    └───────────────────────────────┘
```

## Core Components

### 1. CLI Interface (main.py)

The entry point for the application, built with Typer for excellent CLI experience.

**Key Functions:**

- `edit()`: Edits existing PDF pages with natural language prompts
- `add()`: Generates and inserts new slides into PDFs
- `version()`: Displays version information

**Features:**

- Input validation (file existence, page ranges)
- Parallel processing coordination
- Progress reporting
- Error handling and user feedback
- Temporary file management

**Architecture Pattern:** Command pattern with separate handlers for each operation

### 2. PDF Utilities (pdf_utils.py)

Handles all PDF-related operations including rendering, text extraction, and manipulation.

**Key Functions:**

```python
check_system_dependencies()  # Validates poppler and tesseract
get_page_count(pdf_path)     # Returns total pages in PDF
extract_full_text(pdf_path)  # Extracts text with layout preservation
render_page_as_image(pdf_path, page_number)  # Converts page to image
rehydrate_image_to_pdf(image, output_path)   # Image → PDF with OCR
batch_replace_pages(pdf_path, replacements, output_path)  # Multi-page replacement
insert_page(pdf_path, new_page, after_page, output_path)  # Insert new page
```

**Key Technologies:**

- **pdf2image**: Converts PDF pages to PIL Images using Poppler
- **pypdf**: Reads and writes PDF files, handles page manipulation
- **pytesseract**: Performs OCR to create searchable text layer
- **subprocess**: Calls pdftotext for efficient text extraction

**Text Extraction Strategy:**

```python
# Uses pdftotext with -layout flag for structure preservation
# Output format:
<document_context>
  <page-1>
    ... text content (max 2000 chars) ...
  </page-1>
  <page-2>
    ... text content (max 2000 chars) ...
  </page-2>
</document_context>
```

### 3. AI Utilities (ai_utils.py)

Interfaces with Google's Gemini API for image generation.

**Key Functions:**

```python
get_client()  # Creates authenticated Gemini client
generate_edited_slide(target_image, style_refs, context, prompt)
generate_new_slide(style_refs, prompt, context)
```

**API Configuration:**

```python
GenerateContentConfig(
    response_modalities=['TEXT', 'IMAGE'],  # Allow both outputs
    image_config=ImageConfig(
        image_size='4K'  # or '2K', '1K'
    ),
    tools=[{"google_search": {}}]  # Optional
)
```

**Error Handling:**

- Detects billing/quota errors and provides clear instructions
- Detects authentication errors
- Provides helpful error messages with resolution steps

**Prompt Construction:**

1. User's editing instruction
2. Target image (for edit) or style references (for add)
3. Additional style reference images
4. Optional document context (wrapped in XML-style tags)

## Data Flow

### Edit Command Flow

```
1. User Input
   ↓
2. Validate (file exists, pages in range)
   ↓
3. Extract Context (optional)
   ├─ pdftotext extracts text
   └─ Format as <document_context>
   ↓
4. Render Reference Images
   ├─ User-specified style refs
   └─ pdf2image converts pages
   ↓
5. Parallel Processing
   ├─ For each page:
   │  ├─ Render target page
   │  ├─ Call Gemini API
   │  ├─ Receive generated image
   │  ├─ OCR with Tesseract
   │  └─ Create single-page PDF
   └─ ThreadPoolExecutor (max 10 workers)
   ↓
6. Batch Stitching
   ├─ Read original PDF
   ├─ Replace edited pages
   ├─ Preserve original pages
   └─ Write output PDF
   ↓
7. Cleanup
   ├─ Delete temporary PDFs
   └─ Report success
```

### Add Command Flow

```
1. User Input (position, prompt)
   ↓
2. Validate (file exists, position valid)
   ↓
3. Extract Context (enabled by default)
   ↓
4. Render Style References
   ├─ User-specified or default to page 1
   └─ Multiple pages for better style matching
   ↓
5. Generate New Slide
   ├─ Send style refs + prompt + context
   ├─ Gemini generates new slide
   └─ Match visual style automatically
   ↓
6. OCR Re-hydration
   ├─ Tesseract extracts text
   └─ Create searchable PDF
   ↓
7. Insert into PDF
   ├─ Read original PDF
   ├─ Insert at specified position
   ├─ Scale to match dimensions
   └─ Write output PDF
```

## Design Decisions

### 1. Why Parallel Processing?

**Decision**: Use ThreadPoolExecutor with up to 10 concurrent workers

**Rationale**:
- PDF editing often involves multiple pages
- API calls to Gemini are I/O bound (network latency)
- Parallel processing dramatically reduces total execution time
- Thread pool prevents resource exhaustion

**Trade-offs**:
- Increased memory usage (multiple images in memory)
- Potential for rate limiting (mitigated by max 10 workers)
- More complex error handling

### 2. Why OCR Re-hydration?

**Decision**: Always use Tesseract to add text layer to generated images

**Rationale**:
- Gemini generates images without embedded text
- PDFs without text layers are not searchable
- Users expect to copy/paste text from edited pages
- Maintains feature parity with original PDF

**Trade-offs**:
- OCR accuracy not 100% (especially for stylized fonts)
- Additional processing time per page
- Requires system dependency (Tesseract)

**Why not embed original text?**
- Generated images may have different layout/positioning
- Text might not align with new visual elements
- OCR provides best approximation of visible text

### 3. Why Support Document Context?

**Decision**: Optional full-text context extraction

**Rationale**:
- Helps AI understand document theme and terminology
- Improves consistency across multi-page edits
- Enables content-aware generation (for 'add' command)
- Useful for specialized/technical documents

**Trade-offs**:
- Increased API payload size
- Can confuse model with too much information
- Slower processing
- Default to off for 'edit', on for 'add'

### 4. Why Style References?

**Decision**: Send reference pages to guide visual style

**Rationale**:
- Maintains visual consistency across edits
- AI can match fonts, colors, layouts
- Essential for professional documents
- Automatic extraction from document

**Implementation**:
- User can specify pages explicitly
- System uses first page as default for 'add'
- Multiple references improve style matching

### 5. Why Multiple Resolution Options?

**Decision**: Support 4K, 2K, and 1K resolution settings

**Rationale**:
- Quality vs. cost trade-off
- 4K for high-quality presentations
- 2K for draft/review iterations
- 1K for quick testing

**Cost Implications**:
- 4K images cost more per API call
- Lower resolution reduces API costs significantly
- Users can choose based on needs

### 6. Why Not Use PDF Text Overlay?

**Decision**: Use OCR instead of preserving original text layer

**Rationale**:
- Generated images have different layouts
- AI might reposition or reformat text
- Original text coordinates would be incorrect
- OCR provides best match to visible content

**Alternative Considered**: Hybrid approach (preserve + OCR)
- Too complex for marginal benefit
- Text positioning still problematic

## Technology Stack

### Core Languages & Frameworks

- **Python 3.10+**: Primary language
  - Modern type hints
  - Good ecosystem for PDF/image processing
  - Easy CLI development

- **Typer**: CLI framework
  - Excellent developer experience
  - Automatic help generation
  - Type-safe command definitions
  - Built on Click

### PDF Processing

- **Poppler** (pdftotext, pdfimages)
  - Fast, reliable PDF rendering
  - Industry standard
  - Cross-platform support

- **pdf2image**
  - Python wrapper for Poppler
  - Converts PDF pages to PIL Images
  - Handles resolution and DPI

- **pypdf**
  - Pure Python PDF library
  - Read/write PDF files
  - Page manipulation (replace, insert)
  - No external dependencies

### OCR & Computer Vision

- **Tesseract**
  - Open-source OCR engine
  - High accuracy
  - Multi-language support
  - Creates searchable PDFs

- **pytesseract**
  - Python wrapper for Tesseract
  - Easy PDF generation with text layer

- **Pillow (PIL)**
  - Image manipulation
  - Format conversion
  - Works with Gemini API

### AI & API

- **Google Gemini API** (google-genai)
  - Gemini 3 Pro Image model
  - Image generation capabilities
  - Optional Google Search integration
  - Multi-modal (text + image) input/output

- **python-dotenv**
  - Environment variable management
  - API key configuration
  - Development/production separation

## Performance Considerations

### Bottlenecks

1. **API Latency**: Gemini API calls (2-10 seconds per page)
   - **Mitigation**: Parallel processing with ThreadPoolExecutor
   - **Impact**: 10x speedup for 10-page batch

2. **PDF Rendering**: pdf2image conversion
   - **Mitigation**: Only render needed pages
   - **Optimization**: Cache style reference images

3. **OCR Processing**: Tesseract text extraction
   - **Mitigation**: Single-threaded but fast (~1 second)
   - **Optimization**: Run after API call (already parallel)

4. **File I/O**: Reading/writing PDFs
   - **Mitigation**: Use temporary files, batch writes
   - **Optimization**: Single final write operation

### Memory Usage

- **Images in Memory**: ~25MB per 4K image
- **Parallel Workers**: 10 workers × 25MB = 250MB peak
- **Mitigation**: Workers release memory after processing
- **Consideration**: Reduce workers on low-memory systems

### Cost Optimization

- **API Costs**: Based on image size and API calls
- **Strategies**:
  - Use 2K or 1K for drafts
  - Merge multiple edits per page
  - Disable Google Search when not needed
  - Cache style references

## Security Considerations

### API Key Management

- **Never hardcode keys**: Use environment variables
- **Example .env file**: Included but not committed
- **Validation**: Check for key presence before API calls
- **Error messages**: Don't log or display API keys

### File Handling

- **Input Validation**: Check file exists and is readable
- **Path Traversal**: Use Path.exists() and absolute paths
- **Temporary Files**: Use tempfile module for secure temp files
- **Cleanup**: Always delete temporary files (in finally block)

### User Data

- **Local Processing**: PDF content stays on user's machine
- **API Transmission**: Only rendered images sent to Gemini
- **Context Opt-in**: User controls what text is sent
- **No Logging**: Don't log PDF content or user prompts

### Dependencies

- **Known Vulnerabilities**: Regular dependency updates
- **Supply Chain**: Use established, maintained packages
- **System Dependencies**: Validate presence before use
- **Minimal Permissions**: Don't require elevated privileges

### Error Messages

- **Information Disclosure**: Don't expose file paths in errors
- **API Errors**: Sanitize before displaying
- **Helpful but Safe**: Guide users without revealing internals

## Extension Points

### Adding New Commands

1. Create new command function in `main.py`
2. Decorate with `@app.command()`
3. Use type hints for automatic validation
4. Follow existing error handling patterns

### Supporting New PDF Operations

1. Add function to `pdf_utils.py`
2. Use pypdf for manipulation
3. Handle edge cases (empty PDFs, permissions)
4. Add error handling

### Integrating New AI Models

1. Create new module (e.g., `claude_utils.py`)
2. Implement same interface as `ai_utils.py`
3. Add model selection parameter
4. Update configuration

### Adding Export Formats

1. Extend `pdf_utils.py` with new export function
2. Use appropriate library (e.g., reportlab, img2pdf)
3. Add CLI option for format selection
4. Document new format

## Future Considerations

### Potential Enhancements

1. **Configuration Files**: YAML/JSON for settings
2. **Batch Files**: Process multiple PDFs in sequence
3. **Templates**: Predefined styles and layouts
4. **Undo/Redo**: Track edit history
5. **Preview Mode**: Show before applying
6. **Progress Bar**: Visual feedback for long operations
7. **Logging**: Optional detailed logs
8. **Caching**: Cache API responses for same inputs
9. **Web UI**: Browser-based interface
10. **Plugin System**: Custom processing plugins

### Scalability

- **Current**: Single-machine, CLI tool
- **Future**: 
  - Web service with job queue
  - Distributed processing
  - Cloud deployment options
  - REST API

### Architecture Evolution

- **Current**: Monolithic CLI tool
- **Future**:
  - Microservices (PDF, AI, OCR services)
  - Event-driven architecture
  - Containerization (Docker)
  - Kubernetes deployment

## Conclusion

Nano PDF's architecture balances simplicity with power, providing a clean CLI interface while handling complex operations behind the scenes. The modular design separates concerns (CLI, PDF, AI) and allows for easy extension and maintenance.

Key architectural strengths:
- **Separation of Concerns**: Clear module boundaries
- **Error Handling**: Comprehensive validation and recovery
- **Performance**: Parallel processing where beneficial
- **User Experience**: Clear feedback and helpful errors
- **Extensibility**: Easy to add new features
- **Security**: Careful handling of sensitive data

The architecture is designed for a CLI tool but contains patterns that could scale to larger systems if needed.
