# Nano PDF User Guide for Beginners

Welcome to Nano PDF! This comprehensive guide will help you get started with editing PDF files using natural language, even if you've never used a command-line tool before.

## Table of Contents

- [What is Nano PDF?](#what-is-nano-pdf)
- [Before You Start](#before-you-start)
- [Installation](#installation)
- [Your First Edit](#your-first-edit)
- [Basic Commands](#basic-commands)
- [Advanced Features](#advanced-features)
- [Tips and Best Practices](#tips-and-best-practices)
- [Common Questions](#common-questions)

## What is Nano PDF?

Nano PDF is a tool that lets you edit PDF files by simply describing what you want to change in plain English. Instead of using complex PDF editing software, you can say things like:

- "Change the title to 'Q4 Report'"
- "Update the graph to show data from 2025"
- "Add the company logo in the top right corner"

The tool uses artificial intelligence (specifically Google's Gemini 3 Pro Image model) to understand your instructions and make the changes automatically.

### What Can It Do?

✅ **Edit existing PDF pages**
- Fix typos and errors
- Update text, numbers, and dates
- Change colors and visual elements
- Modify charts and graphs
- Adjust layouts

✅ **Add new pages**
- Create title slides
- Generate summary pages
- Add agenda slides
- Insert new content that matches your deck's style

✅ **Preserve quality**
- Keeps text searchable and selectable
- Maintains document structure
- Processes multiple pages at once

### What It Cannot Do

❌ Fill out forms (use a form filler instead)
❌ Remove password protection (use PyPDF2 or similar)
❌ Convert to other formats (use dedicated converters)
❌ Edit complex vector graphics (use Illustrator or Inkscape)

## Before You Start

### What You Need

1. **A computer** running macOS, Windows, or Linux
2. **Python 3.10 or newer** installed
3. **A Google Gemini API key** (with billing enabled)
4. **System dependencies**: Poppler and Tesseract (we'll install these)
5. **A PDF file** you want to edit

### Understanding the Terminal/Command Line

Nano PDF is a **command-line tool**, which means you'll type commands in a terminal window rather than clicking buttons in a graphical interface.

**Don't worry!** It's easier than it sounds:

- **macOS**: Open "Terminal" (find it in Applications → Utilities)
- **Windows**: Open "Command Prompt" or "PowerShell" (search for it in Start menu)
- **Linux**: Open your terminal emulator (usually Ctrl+Alt+T)

When you see instructions like this:
```bash
nano-pdf edit myfile.pdf 1 "Change the title"
```

You should:
1. Type the command exactly as shown
2. Press Enter/Return
3. Wait for the command to finish

## Installation

Follow the [detailed installation guide](INSTALLATION.md) for your operating system, or use this quick start:

### Quick Install (macOS)

```bash
# Install system dependencies
brew install poppler tesseract

# Install Nano PDF
pip install nano-pdf

# Set up your API key (get it from https://aistudio.google.com/api-keys)
export GEMINI_API_KEY="your_api_key_here"
```

### Quick Install (Linux)

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install poppler-utils tesseract-ocr

# Install Nano PDF
pip install nano-pdf

# Set up your API key
export GEMINI_API_KEY="your_api_key_here"
```

### Quick Install (Windows)

```bash
# Install system dependencies (requires Chocolatey)
choco install poppler tesseract

# Install Nano PDF
pip install nano-pdf

# Set up your API key
set GEMINI_API_KEY=your_api_key_here
```

### Getting Your API Key

1. Visit [Google AI Studio](https://aistudio.google.com/api-keys)
2. Sign in with your Google account
3. Click "Create API Key"
4. **Important**: Enable billing on your Google Cloud project
   - Nano PDF requires a paid API tier
   - See [pricing information](https://ai.google.dev/pricing)
5. Copy your API key and set it as an environment variable

## Your First Edit

Let's edit a PDF file step by step!

### Step 1: Prepare Your PDF

1. Find a PDF file you want to edit (e.g., `presentation.pdf`)
2. Note which page you want to change (pages are numbered starting from 1)
3. Decide what you want to change

### Step 2: Run Your First Command

Let's say you want to change the title on page 1 to "2025 Q4 Report":

```bash
nano-pdf edit presentation.pdf 1 "Change the title to '2025 Q4 Report'"
```

**What this means:**
- `nano-pdf edit` - The command to edit a PDF
- `presentation.pdf` - Your PDF file (can be a full path)
- `1` - The page number to edit (first page)
- `"Change the title to '2025 Q4 Report'"` - Your instruction in quotes

### Step 3: Wait for Processing

You'll see output like:
```
Processing presentation.pdf with 1 edits...
Skipping text context (use --use-context to enable)...
Rendering reference images...
Processing 1 pages in parallel...
Starting Page 1...
Finished Page 1
Progress: 1/1 pages completed

Stitching 1 pages into final PDF...
Done! Saved to edited_presentation.pdf
```

### Step 4: Check Your Result

Open `edited_presentation.pdf` to see your changes! The file will be in the same folder as your original PDF.

## Basic Commands

### Editing a Single Page

**Format:**
```bash
nano-pdf edit <PDF_FILE> <PAGE_NUMBER> "<INSTRUCTION>"
```

**Examples:**

Fix a typo on page 3:
```bash
nano-pdf edit report.pdf 3 "Fix the typo: change 'recieve' to 'receive'"
```

Update a date on page 1:
```bash
nano-pdf edit slides.pdf 1 "Change the date from 2024 to 2025"
```

Change colors on page 5:
```bash
nano-pdf edit deck.pdf 5 "Make the background blue and the text white"
```

### Editing Multiple Pages

You can edit several pages in one command:

**Format:**
```bash
nano-pdf edit <PDF_FILE> <PAGE1> "<INSTRUCTION1>" <PAGE2> "<INSTRUCTION2>"
```

**Example:**
```bash
nano-pdf edit report.pdf \
  1 "Update the title to 'Annual Report 2025'" \
  3 "Change the chart color to blue" \
  7 "Fix the typo in the footer"
```

**Note**: The `\` at the end of lines means "continue on next line". You can also write it on one line without the `\`.

### Adding New Pages

**Format:**
```bash
nano-pdf add <PDF_FILE> <POSITION> "<INSTRUCTION>"
```

Where `<POSITION>` is:
- `0` to add at the beginning
- `1` to add after page 1
- `5` to add after page 5
- etc.

**Examples:**

Add a title slide at the beginning:
```bash
nano-pdf add presentation.pdf 0 "Create a title slide with 'Q4 2025 Review' and the company logo"
```

Add a summary slide after page 5:
```bash
nano-pdf add deck.pdf 5 "Create a summary slide with bullet points of key takeaways"
```

## Advanced Features

### Using Style References

Style references help the AI match the visual style of your existing slides.

```bash
nano-pdf edit presentation.pdf 10 "Add a thank you message" \
  --style-refs "1,2,3"
```

This tells the AI to look at pages 1, 2, and 3 to understand your document's fonts, colors, and layout.

**When to use:**
- Your document has a specific visual theme
- You want consistent styling across edits
- You're adding new pages that should match existing ones

### Using Document Context

Document context includes the full text of your PDF, helping the AI understand your content better.

```bash
nano-pdf edit report.pdf 5 "Update the summary section" \
  --use-context
```

**When to use:**
- Editing content that references other parts of the document
- Adding pages that need to be consistent with document content
- Working with specialized or technical documents

**Note**: Context is:
- **Disabled by default** for `edit` (can confuse the model)
- **Enabled by default** for `add` (helps create relevant content)

### Choosing Resolution

Higher resolution = better quality but slower and more expensive.

```bash
nano-pdf edit slides.pdf 1 "Update graph" --resolution "2K"
```

**Options:**
- `4K` (default) - Best quality, use for final versions
- `2K` - Good quality, faster, cheaper (good for iterations)
- `1K` - Quick drafts, testing

**Cost implications:**
- 4K images cost more per API call
- Use 2K or 1K while refining your prompts
- Switch to 4K for final output

### Disabling Google Search

By default, Gemini can use Google Search to find current information. You can disable this:

```bash
nano-pdf edit report.pdf 5 "Update market data" \
  --disable-google-search
```

**When to disable:**
- You want the AI to only use your document's context
- You're working with internal/confidential information
- You want faster processing

### Specifying Output Filename

By default, output is saved as `edited_<original_name>.pdf`. You can customize this:

```bash
nano-pdf edit slides.pdf 1 "Update title" \
  --output "final_presentation.pdf"
```

## Tips and Best Practices

### Writing Good Prompts

✅ **Do:**
- Be specific: "Change the title to 'Q4 Report'" vs. "Update the title"
- Use quotes: "Change the date to 'December 2025'"
- Break complex edits into separate pages
- Describe what you want, not how to do it

❌ **Don't:**
- Be vague: "Make it better"
- Use extremely long instructions (keep under 200 words)
- Expect pixel-perfect precision for small details
- Ask for impossible edits (e.g., "remove the background" from a flat image)

### Example Good Prompts

**For text changes:**
```bash
"Change the header text from 'Draft' to 'Final Version' and update the date to January 15, 2025"
```

**For visual changes:**
```bash
"Change the pie chart colors to blue, green, and orange, and increase the size by 50%"
```

**For layout changes:**
```bash
"Move the company logo from the bottom left to the top right corner and make it smaller"
```

**For new slides:**
```bash
"Create an agenda slide with three bullet points: Introduction, Main Content, and Conclusion"
```

### Saving Time and Money

1. **Test with low resolution first:**
   ```bash
   nano-pdf edit test.pdf 1 "Try my edit" --resolution "1K"
   ```
   Once it works, re-run with 4K for final quality.

2. **Batch related edits:**
   Instead of running 3 separate commands, do:
   ```bash
   nano-pdf edit doc.pdf 1 "Edit A" 2 "Edit B" 3 "Edit C"
   ```

3. **Use style references wisely:**
   Specify 1-3 reference pages rather than letting the system auto-detect.

4. **Preview before processing:**
   Open your PDF and note the exact page numbers before running commands.

### Troubleshooting Common Issues

**"File not found" error:**
- Check the file path is correct
- Use quotes if path has spaces: `"my file.pdf"`
- Try using the full path: `/Users/name/Documents/file.pdf`

**"Invalid page number" error:**
- Remember pages start at 1, not 0
- Check the PDF actually has that many pages
- Open the PDF to verify page numbers

**"GEMINI_API_KEY not found" error:**
- You need to set your API key in every new terminal session
- Or add it to your shell profile (.bashrc, .zshrc, etc.)
- See [Installation Guide](INSTALLATION.md) for permanent setup

**"Generated image doesn't look right":**
- Try adding style references: `--style-refs "1,2"`
- Make your prompt more specific
- Use context for content-aware edits: `--use-context`
- Try regenerating with a slightly different prompt

**"Text layer is missing or incorrect":**
- This is normal for stylized fonts or small text
- OCR isn't perfect, but usually captures most text
- Use 4K resolution for best OCR results
- Consider manual text touch-up for critical documents

**Processing is very slow:**
- Use lower resolution: `--resolution "2K"`
- Don't edit too many pages at once (split into batches)
- Check your internet connection (API calls require network)

## Common Questions

**Q: Can I undo changes?**  
A: The original PDF is never modified. You can always go back to it. Keep your original file safe!

**Q: Is my data sent to Google?**  
A: Yes, rendered page images are sent to Gemini API for processing. Don't use this tool with highly confidential documents unless you've reviewed Google's data policies.

**Q: Can I use this without an internet connection?**  
A: No, Nano PDF requires internet to connect to the Gemini API.

**Q: How much does it cost?**  
A: It depends on usage. Check [Google's pricing page](https://ai.google.dev/pricing). Generally, a few cents per page at 4K resolution.

**Q: Can I edit scanned PDFs?**  
A: Yes! Scanned PDFs are just images, which is what Gemini works with. However, the AI may struggle with very low-quality scans.

**Q: Will it work with password-protected PDFs?**  
A: No, you'll need to remove the password first using another tool.

**Q: Can I batch process many PDFs?**  
A: Currently, you need to run separate commands for each PDF. You could write a shell script to automate this.

**Q: What languages are supported?**  
A: You can write prompts in English. Gemini can also understand and generate content in many other languages. OCR (text layer) works best with English but supports many languages.

## Next Steps

Now that you understand the basics:

1. **Practice**: Try editing some test PDFs to get comfortable
2. **Explore**: Experiment with different prompts and options
3. **Read more**: Check out [Examples](EXAMPLES.md) for real-world use cases
4. **Get help**: See [Troubleshooting](TROUBLESHOOTING.md) if you run into issues
5. **Share**: Help others by contributing examples or documentation!

### More Resources

- [CLI Reference](API_REFERENCE.md) - Complete command documentation
- [Examples](EXAMPLES.md) - Real-world use cases
- [FAQ](FAQ.md) - Frequently asked questions
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues and solutions

Happy editing! 🎉
