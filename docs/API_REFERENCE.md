# Nano PDF CLI Reference

Complete command-line interface reference for Nano PDF.

## Table of Contents

- [Overview](#overview)
- [Commands](#commands)
  - [edit](#edit-command)
  - [add](#add-command)
  - [version](#version-command)
- [Options](#options)
- [Arguments](#arguments)
- [Exit Codes](#exit-codes)
- [Environment Variables](#environment-variables)
- [Examples](#examples)

## Overview

Nano PDF provides a command-line interface for editing PDF files using natural language.

**General Syntax:**
```bash
nano-pdf <COMMAND> [OPTIONS] [ARGUMENTS]
```

**Getting Help:**
```bash
nano-pdf --help           # General help
nano-pdf edit --help      # Help for edit command
nano-pdf add --help       # Help for add command
```

## Commands

### edit Command

Edit one or more pages in a PDF using natural language prompts.

**Syntax:**
```bash
nano-pdf edit <PDF_PATH> <PAGE> <PROMPT> [<PAGE> <PROMPT> ...] [OPTIONS]
```

**Required Arguments:**
- `PDF_PATH` (string): Path to the PDF file to edit
- `PAGE` (integer): Page number to edit (1-indexed)
- `PROMPT` (string): Natural language instruction for editing

**Options:**
- `--style-refs TEXT`: Comma-separated list of page numbers to use as style references
- `--use-context / --no-use-context`: Include full PDF text as context (default: disabled)
- `--output TEXT`: Output filename (default: `edited_<filename>.pdf`)
- `--resolution TEXT`: Image resolution: "4K", "2K", or "1K" (default: "4K")
- `--disable-google-search`: Disable Google Search integration (default: enabled)

**Examples:**

Edit single page:
```bash
nano-pdf edit slides.pdf 1 "Change the title to 'Q4 2025'"
```

Edit multiple pages:
```bash
nano-pdf edit report.pdf 1 "Update date" 3 "Fix typo" 5 "Change color to blue"
```

With style references:
```bash
nano-pdf edit deck.pdf 10 "Add summary" --style-refs "1,2,3"
```

With context:
```bash
nano-pdf edit document.pdf 5 "Update section" --use-context
```

With custom output and resolution:
```bash
nano-pdf edit presentation.pdf 1 "Edit title" \
  --output "final.pdf" \
  --resolution "2K"
```

**Behavior:**
- Pages are processed in parallel (up to 10 concurrent)
- Original PDF is never modified
- If the same page is edited multiple times in one command, prompts are merged
- Generated images are re-hydrated with OCR to preserve text layer
- Progress is reported during processing

**Error Handling:**
- Validates PDF file exists
- Validates page numbers are within document range
- Validates prompts are provided for each page
- Checks for system dependencies (poppler, tesseract)
- Validates API key is set

### add Command

Generate and insert a new page into a PDF.

**Syntax:**
```bash
nano-pdf add <PDF_PATH> <AFTER_PAGE> <PROMPT> [OPTIONS]
```

**Required Arguments:**
- `PDF_PATH` (string): Path to the PDF file
- `AFTER_PAGE` (integer): Insert after this page (0 for beginning)
- `PROMPT` (string): Description of the new page to create

**Options:**
- `--style-refs TEXT`: Comma-separated list of page numbers for style matching (default: page 1)
- `--use-context / --no-use-context`: Include full PDF text as context (default: enabled)
- `--output TEXT`: Output filename (default: `edited_<filename>.pdf`)
- `--resolution TEXT`: Image resolution: "4K", "2K", or "1K" (default: "4K")
- `--disable-google-search`: Disable Google Search integration (default: enabled)

**Examples:**

Add at beginning:
```bash
nano-pdf add presentation.pdf 0 "Title slide with 'Welcome to Q4 Review'"
```

Add after specific page:
```bash
nano-pdf add deck.pdf 5 "Summary slide with key bullet points"
```

With style references:
```bash
nano-pdf add report.pdf 10 "Add conclusion slide" --style-refs "2,3,4"
```

Without context:
```bash
nano-pdf add slides.pdf 0 "Create title page" --no-use-context
```

**Behavior:**
- Context is enabled by default (helps generate relevant content)
- New page inherits dimensions from first page of document
- Style is matched to reference pages
- Searchable text layer is added via OCR

**Position Values:**
- `0`: Insert at the beginning (before page 1)
- `1`: Insert after page 1 (becomes new page 2)
- `N`: Insert after page N

### version Command

Display the version of Nano PDF.

**Syntax:**
```bash
nano-pdf version
```

**Output:**
```
Nano PDF v0.2.1
```

## Options

### --style-refs

**Type**: String (comma-separated integers)  
**Default**: None (for edit), page 1 (for add)  
**Commands**: edit, add

Specifies which pages to use as visual style references. The AI will analyze these pages to understand fonts, colors, layouts, and design elements.

**Format:**
```bash
--style-refs "1,2,3"
```

**When to use:**
- Document has consistent visual theme
- Want generated content to match existing style
- Adding new pages that should fit seamlessly
- Editing pages that should maintain design consistency

**Tips:**
- Use 1-3 representative pages
- Choose pages that best demonstrate your desired style
- Include pages with varied content (title slide, content slide, etc.)

### --use-context / --no-use-context

**Type**: Boolean flag  
**Default**: False (edit), True (add)  
**Commands**: edit, add

Controls whether the full text content of the PDF is included in the AI prompt.

**Enable context:**
```bash
--use-context
```

**Disable context:**
```bash
--no-use-context
```

**When to enable:**
- Edits reference other parts of document
- Adding content that should be consistent with document theme
- Technical documents with specific terminology
- Want AI to understand document structure

**When to disable:**
- Simple visual changes
- Large documents (to reduce API payload)
- Fast iteration/testing
- Model gets confused by too much context

**Notes:**
- Context is truncated to 2000 chars per page
- Formatted with page numbers for clarity
- May increase API costs due to larger payload

### --output

**Type**: String (filename or path)  
**Default**: `edited_<original_filename>.pdf`  
**Commands**: edit, add

Specifies the output filename for the edited PDF.

**Examples:**
```bash
--output "final_version.pdf"
--output "/path/to/output/result.pdf"
--output "../edited.pdf"
```

**Notes:**
- Can be a filename (saves in current directory)
- Can be a relative or absolute path
- Directory must exist
- Will overwrite existing files without warning

### --resolution

**Type**: String enum  
**Values**: "4K", "2K", "1K"  
**Default**: "4K"  
**Commands**: edit, add

Controls the resolution of generated images.

**Options:**

- **4K** (3072x3072 pixels)
  - Highest quality
  - Best for final versions
  - Slowest processing
  - Highest API cost
  - Best OCR accuracy

- **2K** (2048x2048 pixels)
  - Good quality
  - Balanced speed/cost
  - Suitable for most use cases
  - Good OCR accuracy

- **1K** (1024x1024 pixels)
  - Lower quality
  - Fast processing
  - Lower cost
  - Suitable for drafts/testing
  - May affect OCR accuracy

**Usage:**
```bash
--resolution "2K"
```

**Recommendations:**
- Use 1K or 2K while iterating on prompts
- Switch to 4K for final output
- Use 2K as default for most work
- Only use 4K when quality is critical

### --disable-google-search

**Type**: Boolean flag  
**Default**: False (search enabled)  
**Commands**: edit, add

Disables Google Search integration for the Gemini model.

**Usage:**
```bash
--disable-google-search
```

**When to disable:**
- Working with internal/confidential documents
- Want AI to only use provided context
- Faster processing (no search overhead)
- Predictable results

**When to leave enabled (default):**
- Updating with current information
- Need fact-checking
- General knowledge questions
- Market data or statistics

**Notes:**
- Search is enabled by default
- Disabling may improve speed slightly
- Model can still use its training data

## Arguments

### PDF_PATH

**Type**: String  
**Required**: Yes  
**Description**: Path to the PDF file

**Formats:**
```bash
"file.pdf"                    # Current directory
"./folder/file.pdf"           # Relative path
"/absolute/path/file.pdf"     # Absolute path
"~/Documents/file.pdf"        # Home directory
"path with spaces.pdf"        # Use quotes for spaces
```

**Validation:**
- File must exist
- Must be a valid PDF file
- Must be readable

### PAGE

**Type**: Integer  
**Required**: Yes (for edit command)  
**Description**: Page number (1-indexed)

**Valid values:**
- Minimum: 1 (first page)
- Maximum: Total pages in PDF

**Examples:**
```bash
1         # First page
5         # Fifth page
100       # One hundredth page
```

**Validation:**
- Must be a positive integer
- Must be within document page range
- Cannot be 0 (pages start at 1)

### AFTER_PAGE

**Type**: Integer  
**Required**: Yes (for add command)  
**Description**: Insert position (0-indexed position)

**Valid values:**
- Minimum: 0 (insert at beginning)
- Maximum: Total pages in PDF

**Examples:**
```bash
0         # Insert at beginning (before page 1)
1         # Insert after page 1 (becomes new page 2)
5         # Insert after page 5 (becomes new page 6)
```

### PROMPT

**Type**: String  
**Required**: Yes  
**Description**: Natural language instruction

**Format:**
- Must be enclosed in quotes
- Can be multi-line
- Reasonable length (under 500 words recommended)

**Good prompts:**
```bash
"Change the title to 'Q4 2025 Report'"
"Update the bar chart to show 2025 data instead of 2024"
"Fix the typo: change 'recieve' to 'receive'"
"Make the background blue and increase the font size"
```

**Bad prompts:**
```bash
"Make it better"              # Too vague
"Fix"                         # Not specific
"Change everything"           # Too broad
```

## Exit Codes

Nano PDF uses standard exit codes:

- **0**: Success
- **1**: Error occurred

**Examples:**

```bash
nano-pdf edit file.pdf 1 "Edit"
echo $?  # 0 if successful, 1 if error
```

**In scripts:**
```bash
if nano-pdf edit file.pdf 1 "Edit"; then
    echo "Success!"
else
    echo "Failed!"
fi
```

## Environment Variables

### GEMINI_API_KEY

**Required**: Yes  
**Type**: String  
**Description**: Google Gemini API key

**Setup:**

**macOS/Linux:**
```bash
export GEMINI_API_KEY="your_key_here"
```

**Windows (Command Prompt):**
```cmd
set GEMINI_API_KEY=your_key_here
```

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your_key_here"
```

**Validation:**
- Checked at runtime before API calls
- Must be a valid paid-tier API key
- Error if not set or invalid

**Security:**
- Never commit API keys to version control
- Use environment variables or secure vaults
- Don't share keys publicly

## Examples

### Basic Editing

**Edit one page:**
```bash
nano-pdf edit report.pdf 3 "Change the title to 'Updated Report'"
```

**Edit multiple pages:**
```bash
nano-pdf edit slides.pdf \
  1 "Update date to January 2025" \
  5 "Change chart colors to blue and green" \
  10 "Add company logo in top right"
```

### Adding Pages

**Add title slide:**
```bash
nano-pdf add presentation.pdf 0 "Title slide with 'Q4 Review' and company logo"
```

**Add summary slide:**
```bash
nano-pdf add deck.pdf 15 "Create summary slide with 3 key takeaways as bullet points"
```

### Advanced Options

**High-quality edit with style matching:**
```bash
nano-pdf edit report.pdf 5 "Update financial chart" \
  --style-refs "1,2,3" \
  --resolution "4K" \
  --output "final_report.pdf"
```

**Fast draft with context:**
```bash
nano-pdf edit document.pdf 10 "Revise conclusion" \
  --use-context \
  --resolution "1K"
```

**Private document (no search):**
```bash
nano-pdf add internal_deck.pdf 5 "Add confidential metrics slide" \
  --disable-google-search \
  --style-refs "1,2"
```

### Batch Processing

**Process multiple pages efficiently:**
```bash
nano-pdf edit large_document.pdf \
  1 "Fix title" \
  2 "Update date" \
  3 "Change color scheme" \
  4 "Fix typo" \
  5 "Update chart" \
  --resolution "2K"
```

### Pipeline Usage

**In shell scripts:**
```bash
#!/bin/bash

for file in *.pdf; do
    nano-pdf edit "$file" 1 "Add watermark: DRAFT" \
      --output "drafts/$file" \
      --resolution "1K"
done
```

**With error handling:**
```bash
#!/bin/bash

if ! nano-pdf edit report.pdf 1 "Update title"; then
    echo "Error: Failed to edit PDF" >&2
    exit 1
fi

echo "Successfully edited PDF"
```

### Testing and Iteration

**Quick test with low resolution:**
```bash
# Test your prompt
nano-pdf edit test.pdf 1 "Try this edit" --resolution "1K"

# If it works, run with high quality
nano-pdf edit test.pdf 1 "Try this edit" --resolution "4K"
```

## Getting Help

- Run `nano-pdf --help` for quick reference
- Run `nano-pdf <command> --help` for command-specific help
- See [User Guide](USER_GUIDE.md) for tutorials
- See [Examples](EXAMPLES.md) for real-world use cases
- See [Troubleshooting](TROUBLESHOOTING.md) for common issues
