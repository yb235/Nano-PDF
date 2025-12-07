# Quick Start Guide: PDF to PowerPoint Conversion

## Installation

```bash
# Install Nano PDF
pip install nano-pdf

# Or install from source
git clone https://github.com/gavrielc/Nano-PDF.git
cd Nano-PDF
pip install -e .

# Install system dependencies
# macOS:
brew install poppler tesseract

# Linux (Ubuntu/Debian):
sudo apt-get install poppler-utils tesseract-ocr

# Windows:
choco install poppler tesseract
```

## Setup

```bash
# Set your Gemini API key (required for AI features)
export GEMINI_API_KEY="your_api_key_here"

# Or create .env file
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

## Basic Usage

### 1. Simple Conversion
```bash
# Convert any PDF to PowerPoint
nano-pdf convert presentation.pdf

# Output: presentation.pptx
```

### 2. With Custom Output Name
```bash
nano-pdf convert input.pdf --output my_slides.pptx
```

### 3. Fast Mode (No AI)
```bash
# Faster conversion, charts stay as images
nano-pdf convert simple.pdf --no-use-ai-enhancement --no-extract-charts
```

### 4. AI-Enhanced (Editable Charts)
```bash
# Slower but charts become editable PowerPoint objects
nano-pdf convert charts.pdf --use-ai-enhancement --extract-charts
```

## Testing the Converter

### Generate Sample PDF
```bash
# Create a test PDF
python3 create_sample_pdf.py

# This creates: sample_presentation.pdf
```

### Run Automated Tests
```bash
# Test the converter
python3 test_converter.py

# Output shows:
# ✓ All imports successful
# ✓ PDF analyzer works
# ✓ PowerPoint builder initialized  
# ✓ Full conversion successful
```

### Interactive Demos
```bash
# Run interactive demo program
python3 examples/convert_pdf_demo.py

# Menu options:
#   1. Basic Conversion
#   2. AI-Enhanced Conversion
#   3. Structure Analysis
#   4. Chart Detection
```

## Verify Results

### Open the PowerPoint
```bash
# Convert the sample
nano-pdf convert sample_presentation.pdf --output result.pptx

# Open in PowerPoint/LibreOffice and check:
# - Text is editable
# - Fonts match original
# - Charts are clickable (Edit Data to see values)
# - Images are embedded
# - Layout matches PDF
```

### Check Charts Are Editable
1. Open `result.pptx` in PowerPoint
2. Click on any chart
3. You should see "Chart Tools" ribbon appear
4. Click "Edit Data" to open Excel with chart values
5. Modify values and watch chart update!

## Command Reference

### Full Command Syntax
```bash
nano-pdf convert <PDF_FILE> [OPTIONS]
```

### Options
| Option | Description | Default |
|--------|-------------|---------|
| `--output PATH` | Output filename | `<input>.pptx` |
| `--use-ai-enhancement` | Enable AI features | `True` |
| `--no-use-ai-enhancement` | Disable AI | - |
| `--extract-charts` | Extract editable charts | `True` |
| `--no-extract-charts` | Keep charts as images | - |

### Examples

**Basic:**
```bash
nano-pdf convert deck.pdf
```

**Custom output:**
```bash
nano-pdf convert report.pdf --output Q4_Report.pptx
```

**Fast (no AI):**
```bash
nano-pdf convert simple.pdf --no-use-ai-enhancement
```

**Charts only:**
```bash
nano-pdf convert charts.pdf --extract-charts
```

## Troubleshooting

### Charts Not Editable
**Problem**: Charts appear as images

**Solution**:
```bash
# Make sure AI is enabled
nano-pdf convert file.pdf --use-ai-enhancement --extract-charts

# Check API key is set
echo $GEMINI_API_KEY

# If empty, set it:
export GEMINI_API_KEY="your_key"
```

### Missing Dependencies
**Problem**: `ModuleNotFoundError: No module named 'pptx'`

**Solution**:
```bash
# Reinstall dependencies
pip install -e .

# Or install manually
pip install python-pptx pdfplumber PyMuPDF
```

### Font Issues
**Problem**: Fonts look different

**Solution**:
- Use PDFs with standard fonts (Arial, Calibri, Times New Roman)
- Install missing fonts on your system
- Edit fonts manually in PowerPoint after conversion

### API Rate Limits
**Problem**: "Rate limit exceeded"

**Solution**:
```bash
# Disable AI to avoid API calls
nano-pdf convert file.pdf --no-use-ai-enhancement

# Or wait and try again (free tier has limits)
# Consider upgrading to paid tier
```

## Tips for Best Results

### 1. PDF Quality
- Use native PDFs (not scanned documents)
- Ensure text is selectable in PDF
- Charts should have clear labels

### 2. Conversion Settings
- **Complex charts**: Use AI enhancement
- **Simple slides**: Disable AI for speed
- **Mixed content**: Enable AI, verify output

### 3. Post-Conversion
- Review converted PowerPoint
- Verify chart data accuracy
- Adjust layout if needed
- Update colors/fonts as desired

## Advanced Usage

### Batch Conversion
```bash
# Convert all PDFs in directory
for pdf in *.pdf; do
    nano-pdf convert "$pdf" --output "ppt_${pdf%.pdf}.pptx"
done
```

### Python API
```python
from nano_pdf import ppt_converter, ai_utils

# Convert programmatically
ppt_converter.convert_pdf_to_pptx(
    pdf_path="input.pdf",
    output_path="output.pptx",
    use_ai=True,
    ai_utils_module=ai_utils,
    progress_callback=print
)
```

### Integration with Editing
```bash
# 1. Convert PDF to PPT
nano-pdf convert original.pdf --output editable.pptx

# 2. Convert PPT back to PDF (use PowerPoint/other tool)
# 3. Edit the PDF
nano-pdf edit working.pdf 1 "Update title"

# 4. Convert back to PPT
nano-pdf convert edited_working.pdf
```

## Getting Help

### Documentation
- Full guide: `PDF_TO_PPT_GUIDE.md`
- README: `README.md`
- Feature summary: `FEATURE_SUMMARY.md`

### Support
- GitHub Issues: https://github.com/gavrielc/Nano-PDF/issues
- Email: gavrielcohen89@gmail.com

### Examples
- Demo script: `examples/convert_pdf_demo.py`
- Test suite: `test_converter.py`
- Sample generator: `create_sample_pdf.py`

## Next Steps

1. **Try It Out**
   ```bash
   python3 create_sample_pdf.py
   nano-pdf convert sample_presentation.pdf
   # Open sample_presentation.pptx
   ```

2. **Read the Guide**
   - See `PDF_TO_PPT_GUIDE.md` for detailed documentation

3. **Experiment**
   - Try your own PDFs
   - Test different settings
   - Compare AI vs non-AI results

4. **Report Issues**
   - Found a bug? Report it!
   - Have suggestions? Let us know!

---

**Version**: 0.3.0  
**Last Updated**: December 2024

Happy converting! 🎉
