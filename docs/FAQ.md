# Frequently Asked Questions

Common questions about Nano PDF.

## Table of Contents

- [General Questions](#general-questions)
- [Installation and Setup](#installation-and-setup)
- [Usage Questions](#usage-questions)
- [API and Costs](#api-and-costs)
- [Quality and Limitations](#quality-and-limitations)
- [Security and Privacy](#security-and-privacy)
- [Troubleshooting](#troubleshooting)

## General Questions

### What is Nano PDF?

Nano PDF is a command-line tool that lets you edit PDF files using natural language instructions. Instead of manually editing PDFs, you describe what you want in plain English (e.g., "Change the title to 'Q4 Report'"), and AI automatically makes the changes.

### How does it work?

1. You provide a PDF file and describe what you want to change
2. Nano PDF converts the page(s) to images
3. The images and your instructions are sent to Google's Gemini 3 Pro Image AI model
4. The AI generates edited versions of the pages
5. Text layers are restored using OCR (Optical Character Recognition)
6. The edited pages are stitched back into your PDF

### What can I use it for?

- Fixing typos and errors in presentations
- Updating dates, numbers, and text
- Changing colors and visual elements
- Modifying charts and graphs
- Adding new slides to decks
- Rebranding documents
- Localizing content

### What are the limitations?

- Cannot edit encrypted/password-protected PDFs
- OCR may not perfectly capture stylized fonts
- AI-generated results may vary slightly each time
- Requires internet connection (uses cloud API)
- Requires a paid Google Gemini API key
- Best for slide-style PDFs (presentations, reports)
- Not ideal for complex vector graphics or forms

### Is it free?

The tool itself is free and open-source. However:
- You need a **paid** Google Gemini API key (free tier doesn't support image generation)
- API usage costs vary based on resolution and number of pages
- Typical cost: A few cents per page at 4K resolution
- See [Google's pricing](https://ai.google.dev/pricing) for details

### Do I need to know how to code?

No! Nano PDF is designed for non-programmers. You just need to:
- Know how to open a terminal/command prompt
- Type commands following examples
- Have basic computer skills

## Installation and Setup

### What do I need to install?

1. **Python 3.10 or newer**
2. **System dependencies**:
   - Poppler (for PDF processing)
   - Tesseract (for OCR)
3. **Nano PDF** itself (via pip)
4. **Google Gemini API key** (requires billing enabled)

See the [Installation Guide](INSTALLATION.md) for detailed instructions.

### Which operating systems are supported?

- macOS (10.14+)
- Linux (Ubuntu, Debian, Fedora, RHEL, etc.)
- Windows (10/11)

### How do I get a Google Gemini API key?

1. Visit [Google AI Studio](https://aistudio.google.com/api-keys)
2. Sign in with your Google account
3. Create an API key
4. **Enable billing** on your Google Cloud project (required!)
5. Set the key as an environment variable: `export GEMINI_API_KEY="your_key"`

### Why do I need a paid API key?

Gemini 3 Pro Image (the model used by Nano PDF) supports image generation, which is only available on paid tiers. Free API keys cannot generate images.

### Can I use a different AI model?

Currently, only Gemini 3 Pro Image is supported. Other models may be added in the future.

## Usage Questions

### How do I edit a single page?

```bash
nano-pdf edit myfile.pdf 1 "Change the title to 'New Title'"
```

Replace:
- `myfile.pdf` with your PDF filename
- `1` with the page number
- `"Change..."` with your instruction

### How do I edit multiple pages at once?

```bash
nano-pdf edit myfile.pdf \
  1 "Change on page 1" \
  2 "Change on page 2" \
  3 "Change on page 3"
```

Pages are processed in parallel for speed.

### How do I add a new page?

```bash
nano-pdf add myfile.pdf 0 "Create a title slide with 'Welcome'"
```

- `0` adds at the beginning
- `5` adds after page 5
- etc.

### What makes a good prompt?

**Good prompts are:**
- **Specific**: "Change title to 'Q4 2025'" not "Update title"
- **Clear**: "Make background blue (#0066CC)" not "Make it prettier"
- **Concise**: 1-2 sentences usually sufficient
- **Descriptive**: Include details about what you want

**Examples:**
- ✅ "Change the date from 'Jan 2024' to 'Jan 2025'"
- ✅ "Update the bar chart to show: Q1: 100, Q2: 150, Q3: 200"
- ❌ "Fix the slide" (too vague)
- ❌ "Make it better" (no guidance)

### Can I undo changes?

Your original PDF is never modified. Nano PDF creates a new file (default: `edited_<filename>.pdf`). You can always go back to the original.

### How long does it take?

- **Single page**: 5-15 seconds typically
- **Multiple pages**: Processed in parallel (10 at a time)
- **Factors**: Resolution, API response time, internet speed
- **Tip**: Use `--resolution "2K"` for faster processing

### Can I process multiple PDFs at once?

Not directly in a single command, but you can:
1. Run separate commands for each PDF
2. Write a shell script to batch process
3. See [Examples](EXAMPLES.md) for automation scripts

### What's the maximum number of pages I can edit?

There's no hard limit, but consider:
- Processing happens 10 pages at a time (parallel)
- Large batches may take longer
- API costs scale with page count
- Consider splitting very large jobs (50+ pages)

## API and Costs

### How much does it cost?

Costs depend on:
- **Resolution**: 4K costs more than 2K or 1K
- **Number of pages**: Each page is an API call
- **Context size**: Including full PDF text increases cost slightly

**Rough estimates** (check [Google's pricing](https://ai.google.dev/pricing) for current rates):
- 4K image: ~$0.05-0.10 per page
- 2K image: ~$0.02-0.05 per page
- 1K image: ~$0.01-0.02 per page

**Tips to reduce costs:**
- Use 2K or 1K while testing
- Switch to 4K only for final output
- Batch related edits together
- Disable Google Search if not needed

### Does Google Search cost extra?

Google Search integration is included in the standard API cost. However, disabling it (`--disable-google-search`) may slightly reduce processing time.

### What happens if I hit a rate limit?

- You'll see an error message about rate limiting
- Wait a few minutes and try again
- Consider reducing parallel processing (edit fewer pages at once)
- Check your API quota in Google Cloud Console

### Can I monitor my API usage?

Yes! Visit the [Google Cloud Console](https://console.cloud.google.com):
1. Go to your project
2. Navigate to "APIs & Services" → "Dashboard"
3. Select "Generative Language API"
4. View usage metrics and costs

### Is there a free trial?

Google Cloud offers free credits for new users (typically $300 for 90 days), which can be used for Gemini API calls. Check [Google Cloud Free Tier](https://cloud.google.com/free) for details.

## Quality and Limitations

### Why doesn't the output look exactly like I expected?

AI-generated results can vary because:
- The model interprets prompts creatively
- Different runs may produce slightly different results
- Complex instructions may be interpreted differently

**Solutions:**
- Be more specific in your prompts
- Use style references: `--style-refs "1,2"`
- Include context: `--use-context`
- Try rephrasing your prompt
- Iterate with 1K resolution until you get it right

### Can I select/search text in edited pages?

Yes! Nano PDF uses OCR (Tesseract) to restore searchable text layers. However:
- OCR accuracy depends on font clarity and size
- Stylized or decorative fonts may not OCR perfectly
- Very small text may be missed
- Use `--resolution "4K"` for best OCR results

### Why is text selection incorrect?

OCR isn't perfect. Common issues:
- Stylized fonts are harder to recognize
- Small text may be misread
- Complex layouts can confuse OCR
- Text may not align perfectly with position

For critical documents requiring perfect text layers, manual touch-up may be needed.

### Can Nano PDF edit scanned PDFs?

Yes! Scanned PDFs are just images, which is exactly what Gemini works with. However:
- Low-quality scans may produce poor results
- Very old or degraded documents may be challenging
- OCR accuracy depends on scan quality

### Will colors match exactly?

Colors should be close but may not be pixel-perfect due to:
- AI interpretation
- Color space conversions (RGB vs CMYK)
- Image compression

For precise color matching, specify hex codes: `"Use color #FF5733"`

### Can it edit vector graphics?

Nano PDF works with rasterized images (pixels), not vector graphics. Complex vector artwork may lose quality when edited. Best for:
- Text-heavy slides
- Simple charts and graphs
- Photos and raster images
- Layout changes

Not ideal for:
- Complex illustrations
- Detailed logos requiring precision
- Technical drawings

## Security and Privacy

### Is my data sent to Google?

Yes. When you use Nano PDF:
- PDF pages are rendered as images locally
- Images are sent to Google's Gemini API for processing
- Optional: Full PDF text can be sent as context
- Generated images are returned

**Your data is:**
- Transmitted over HTTPS (encrypted)
- Subject to Google's data policies
- Not stored locally by Nano PDF (only temporary files during processing)

**Important:** Don't use Nano PDF with highly confidential documents unless you've reviewed and accept Google's terms and data handling policies.

### Does Google store my PDFs?

According to Google's policies:
- Prompts and data may be used to improve services (check current terms)
- Enterprise API tiers may offer different data handling
- Review [Google's AI Data Usage Policy](https://cloud.google.com/terms/service-terms)

For sensitive documents, consider enterprise agreements or alternative solutions.

### Can I use Nano PDF offline?

No. Nano PDF requires internet connection to:
- Connect to Gemini API
- Send/receive image data
- Optional: Google Search integration

All AI processing happens in the cloud.

### Is my API key secure?

**Best practices:**
- Store in environment variables, never in code
- Don't commit keys to version control
- Use `.env` file for local development (add to `.gitignore`)
- Rotate keys regularly
- Set up usage alerts in Google Cloud Console

### What happens to temporary files?

Temporary PDF files are:
- Created during processing in `/tmp`
- Automatically deleted when processing completes
- Cleaned up even if errors occur
- Not stored permanently

### Can others see my edits?

- Edits happen on your local machine
- Only images sent to/from Google's API
- Output PDF saved locally
- No sharing unless you share the file yourself

## Troubleshooting

### "Command not found" error?

- Nano PDF isn't installed or not in PATH
- See [Installation Guide](INSTALLATION.md)
- Try: `python3 -m nano_pdf.main version`

### "API key not found" error?

- Environment variable not set
- Set with: `export GEMINI_API_KEY="your_key"`
- See [Installation Guide](INSTALLATION.md) for permanent setup

### "Missing system dependencies" error?

- Poppler or Tesseract not installed
- See [Installation Guide](INSTALLATION.md) for your OS
- Verify with: `pdftotext -v` and `tesseract --version`

### Processing is very slow?

- Use lower resolution: `--resolution "2K"`
- Check internet connection
- Reduce number of pages processed at once
- Disable Google Search: `--disable-google-search`

### Output quality is poor?

- Use higher resolution: `--resolution "4K"`
- Use style references: `--style-refs "1,2"`
- Be more specific in prompts
- Check source PDF quality

For more troubleshooting, see the [Troubleshooting Guide](TROUBLESHOOTING.md).

## Getting Help

### Where can I get more help?

1. **Documentation:**
   - [User Guide](USER_GUIDE.md) - Complete tutorial
   - [Troubleshooting](TROUBLESHOOTING.md) - Common issues
   - [Examples](EXAMPLES.md) - Real-world use cases
   - [API Reference](API_REFERENCE.md) - Command reference

2. **Community:**
   - [GitHub Issues](https://github.com/gavrielc/Nano-PDF/issues) - Bug reports
   - [GitHub Discussions](https://github.com/gavrielc/Nano-PDF/discussions) - Questions
   - Stack Overflow - Tag: `nano-pdf`

3. **Contributing:**
   - [Contributing Guide](../CONTRIBUTING.md) - How to help
   - [Code of Conduct](../CODE_OF_CONDUCT.md) - Community guidelines

### How can I contribute?

Contributions are welcome! You can:
- Report bugs or request features
- Improve documentation
- Submit code improvements
- Share examples and use cases
- Help other users

See [Contributing Guide](../CONTRIBUTING.md) for details.

### Is commercial use allowed?

Yes! Nano PDF is licensed under MIT License, which permits commercial use. However:
- Google's API has its own terms of service
- API costs apply for commercial usage
- Review Google's enterprise offerings for commercial use at scale

## Still Have Questions?

- Check the [full documentation](README.md)
- Search [existing issues](https://github.com/gavrielc/Nano-PDF/issues)
- Open a [new issue](https://github.com/gavrielc/Nano-PDF/issues/new)
- Start a [discussion](https://github.com/gavrielc/Nano-PDF/discussions)
