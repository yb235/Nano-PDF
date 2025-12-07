# Troubleshooting Guide

Common issues and solutions for Nano PDF.

## Table of Contents

- [Installation Issues](#installation-issues)
- [API and Authentication Issues](#api-and-authentication-issues)
- [PDF Processing Issues](#pdf-processing-issues)
- [Output Quality Issues](#output-quality-issues)
- [Performance Issues](#performance-issues)
- [System Dependency Issues](#system-dependency-issues)
- [General Errors](#general-errors)

## Installation Issues

### "nano-pdf: command not found"

**Symptoms:**
```bash
$ nano-pdf version
bash: nano-pdf: command not found
```

**Causes & Solutions:**

1. **Not installed:**
   ```bash
   pip install nano-pdf
   ```

2. **Installation directory not in PATH:**
   ```bash
   # Find where it's installed
   pip show nano-pdf
   
   # Add to PATH (add to ~/.bashrc or ~/.zshrc)
   export PATH="$HOME/.local/bin:$PATH"
   
   # Reload shell
   source ~/.bashrc
   ```

3. **Installed with different Python version:**
   ```bash
   # Use Python module syntax instead
   python3 -m nano_pdf.main version
   
   # Or reinstall with correct Python
   python3.11 -m pip install nano-pdf
   ```

### "No module named 'nano_pdf'"

**Symptoms:**
```
ModuleNotFoundError: No module named 'nano_pdf'
```

**Solutions:**

1. **Verify installation:**
   ```bash
   pip list | grep nano-pdf
   ```

2. **Reinstall:**
   ```bash
   pip uninstall nano-pdf
   pip install nano-pdf
   ```

3. **Check Python version:**
   ```bash
   python --version  # Must be 3.10+
   ```

4. **Clear cache and reinstall:**
   ```bash
   pip cache purge
   pip install --no-cache-dir nano-pdf
   ```

### "error: externally-managed-environment"

**Symptoms:**
```
error: externally-managed-environment
× This environment is externally managed
```

**Cause:** Modern Linux distributions prevent system-wide pip installations.

**Solutions:**

1. **Use pipx (recommended):**
   ```bash
   sudo apt install pipx
   pipx install nano-pdf
   ```

2. **Use virtual environment:**
   ```bash
   python3 -m venv nano-env
   source nano-env/bin/activate
   pip install nano-pdf
   ```

3. **Use --break-system-packages (not recommended):**
   ```bash
   pip install --break-system-packages nano-pdf
   ```

### Permission Denied Errors

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied
```

**Solutions:**

1. **Install to user directory:**
   ```bash
   pip install --user nano-pdf
   ```

2. **Don't use sudo with pip** (can cause issues)

3. **Use virtual environment:**
   ```bash
   python -m venv myenv
   source myenv/bin/activate
   pip install nano-pdf
   ```

## API and Authentication Issues

### "GEMINI_API_KEY not found"

**Symptoms:**
```
ValueError: GEMINI_API_KEY not found in environment variables
```

**Solutions:**

1. **Set the environment variable:**
   
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

2. **Verify it's set:**
   ```bash
   echo $GEMINI_API_KEY  # Unix
   echo %GEMINI_API_KEY%  # Windows CMD
   ```

3. **Make it permanent:**
   - Add to `~/.bashrc` or `~/.zshrc` (Unix)
   - Add to System Environment Variables (Windows)
   - Use `.env` file in project directory

### "PAID API key required" Error

**Symptoms:**
```
RuntimeError: Gemini API Error: This tool requires a PAID API key with billing enabled.
```

**Cause:** Gemini 3 Pro Image requires a paid API tier. Free tier keys don't support image generation.

**Solutions:**

1. **Enable billing:**
   - Visit [Google AI Studio](https://aistudio.google.com/api-keys)
   - Go to your Google Cloud project
   - Enable billing
   - May take a few minutes to activate

2. **Create a new API key** after enabling billing

3. **Verify billing is enabled:**
   - Check Google Cloud Console
   - Verify payment method is added
   - Check project billing status

4. **Wait and retry:**
   - Billing activation can take 5-15 minutes
   - Try again after waiting

### "Invalid API key" Error

**Symptoms:**
```
RuntimeError: Gemini API Error: Invalid API key.
```

**Solutions:**

1. **Check for typos:**
   - Verify the entire key is copied
   - No extra spaces or quotes
   - Check for line breaks

2. **Generate a new key:**
   - Old keys may have been revoked
   - Visit [Google AI Studio](https://aistudio.google.com/api-keys)
   - Create a new API key

3. **Check project permissions:**
   - Ensure API key has proper permissions
   - Verify Gemini API is enabled for your project

### Rate Limiting / Quota Errors

**Symptoms:**
```
Error: Rate limit exceeded
Error: Quota exceeded
```

**Solutions:**

1. **Reduce parallel processing:**
   - Edit fewer pages at once
   - Split large batches into smaller ones

2. **Use lower resolution:**
   ```bash
   --resolution "2K"  # or "1K"
   ```

3. **Wait and retry:**
   - Rate limits reset after time
   - Usually 1 minute for temporary limits

4. **Check quota limits:**
   - Visit Google Cloud Console
   - Check Gemini API quotas
   - Request quota increase if needed

5. **Upgrade API plan:**
   - Higher tiers have higher limits
   - Consider your usage patterns

## PDF Processing Issues

### "File not found" Error

**Symptoms:**
```
Error: File myfile.pdf not found.
```

**Solutions:**

1. **Check file path:**
   ```bash
   ls -la myfile.pdf  # Verify file exists
   pwd                # Check current directory
   ```

2. **Use absolute path:**
   ```bash
   nano-pdf edit /full/path/to/file.pdf 1 "Edit"
   ```

3. **Use quotes for paths with spaces:**
   ```bash
   nano-pdf edit "my file.pdf" 1 "Edit"
   ```

4. **Check file permissions:**
   ```bash
   ls -l myfile.pdf  # Should be readable
   chmod 644 myfile.pdf  # Make readable if needed
   ```

### "Invalid page number" Error

**Symptoms:**
```
Error: Invalid page number(s) [10]. PDF has 5 pages.
```

**Solutions:**

1. **Check page count:**
   ```bash
   # Open PDF and count pages
   # Or use pdfinfo
   pdfinfo myfile.pdf | grep Pages
   ```

2. **Remember pages are 1-indexed:**
   - First page is 1, not 0
   - Last page is total page count

3. **Use valid page range:**
   ```bash
   # If PDF has 5 pages, valid pages are 1-5
   nano-pdf edit file.pdf 5 "Edit last page"
   ```

### PDF is Password Protected

**Symptoms:**
```
Error: Could not read PDF
Error: PDF is encrypted
```

**Cause:** Nano PDF cannot process password-protected PDFs.

**Solutions:**

1. **Remove password first:**
   ```bash
   # Using qpdf
   qpdf --password=PASSWORD --decrypt input.pdf output.pdf
   
   # Using pikepdf (Python)
   pip install pikepdf
   python -c "import pikepdf; pdf=pikepdf.open('in.pdf', password='PASSWORD'); pdf.save('out.pdf')"
   ```

2. **Use PDF editing software:**
   - Adobe Acrobat
   - Preview (macOS)
   - PDFtk
   
3. **Then process with Nano PDF**

### Corrupted PDF Error

**Symptoms:**
```
Error: Could not process PDF
Error: Invalid PDF structure
```

**Solutions:**

1. **Try repairing PDF:**
   ```bash
   # Using qpdf
   qpdf --check input.pdf
   qpdf input.pdf --replace-input
   
   # Using pdftk
   pdftk input.pdf output repaired.pdf
   ```

2. **Re-export PDF:**
   - Open in PDF viewer
   - Export/Save As new file
   - Try processing new file

3. **Check PDF version:**
   - Very old or very new PDFs may have issues
   - Convert to standard PDF 1.7

## Output Quality Issues

### Text Layer Missing or Incorrect

**Symptoms:**
- Cannot select/copy text from edited pages
- Searchable text doesn't match visible text
- OCR results are incorrect

**Causes & Solutions:**

1. **Use higher resolution:**
   ```bash
   --resolution "4K"  # Better OCR accuracy
   ```

2. **Check Tesseract installation:**
   ```bash
   tesseract --version
   ```

3. **Install language data:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr-eng
   
   # macOS
   brew install tesseract-lang
   ```

4. **Accept OCR limitations:**
   - Stylized fonts are harder to OCR
   - Very small text may be missed
   - Complex layouts may confuse OCR
   - Manual touch-up may be needed

### Generated Image Doesn't Match Style

**Symptoms:**
- Colors don't match original
- Fonts look different
- Layout is inconsistent

**Solutions:**

1. **Use style references:**
   ```bash
   --style-refs "1,2,3"
   ```

2. **Be more specific in prompt:**
   ```bash
   "Change the title to 'New Title' but keep the exact same blue color (#0066CC) and font"
   ```

3. **Include more style examples:**
   ```bash
   --style-refs "1,2,3,4,5"
   ```

4. **Use context for consistency:**
   ```bash
   --use-context
   ```

5. **Iterate on the prompt:**
   - Try different phrasings
   - Be more descriptive about desired style
   - Reference specific design elements

### Low Quality Output

**Symptoms:**
- Blurry text
- Pixelated images
- Low resolution output

**Solutions:**

1. **Use 4K resolution:**
   ```bash
   --resolution "4K"
   ```

2. **Check source PDF quality:**
   - Input quality affects output
   - Can't improve poor source material

3. **Use higher DPI for rendering:**
   - Modify pdf2image settings in code if needed
   - Default should be sufficient for most cases

### Colors Look Wrong

**Symptoms:**
- Colors are shifted
- Brightness is off
- Color profile issues

**Solutions:**

1. **Specify exact colors in prompt:**
   ```bash
   "Change background to hex color #FF5733"
   ```

2. **Use style references:**
   ```bash
   --style-refs "1"  # Page with correct colors
   ```

3. **Check PDF color space:**
   - RGB vs CMYK differences
   - Convert to RGB if needed

4. **Monitor calibration:**
   - Colors may appear different on different screens
   - Check on multiple devices

## Performance Issues

### Processing is Very Slow

**Symptoms:**
- Taking minutes per page
- Hanging or appearing stuck

**Causes & Solutions:**

1. **Network latency:**
   - Check internet connection
   - API calls require network
   - Gemini API response time varies

2. **Use lower resolution:**
   ```bash
   --resolution "2K"  # or "1K" for fastest
   ```

3. **Reduce parallel processing:**
   - Processing too many pages at once
   - Split into smaller batches
   ```bash
   # Instead of 20 pages, do 2 batches of 10
   nano-pdf edit file.pdf 1 "edit" 2 "edit" ... 10 "edit"
   nano-pdf edit file.pdf 11 "edit" 12 "edit" ... 20 "edit"
   ```

4. **Disable Google Search:**
   ```bash
   --disable-google-search
   ```

5. **Check system resources:**
   ```bash
   top  # Check CPU/memory usage
   ```

### High Memory Usage

**Symptoms:**
- System slowdown
- Out of memory errors
- Swap usage

**Solutions:**

1. **Process fewer pages at once:**
   - Reduce batch size
   - Maximum 10 concurrent by default

2. **Use lower resolution:**
   ```bash
   --resolution "2K"  # Uses less memory
   ```

3. **Close other applications:**
   - Free up RAM
   - Especially large applications

4. **Monitor memory:**
   ```bash
   # macOS/Linux
   free -h
   
   # Or use system monitor
   ```

### Disk Space Issues

**Symptoms:**
```
Error: No space left on device
```

**Solutions:**

1. **Check disk space:**
   ```bash
   df -h
   ```

2. **Clean temporary files:**
   ```bash
   # Nano PDF cleans up automatically
   # But check /tmp for orphaned files
   ls -lh /tmp/*.pdf
   rm /tmp/*.pdf  # If safe
   ```

3. **Clean pip cache:**
   ```bash
   pip cache purge
   ```

4. **Free up space:**
   - Delete unnecessary files
   - Move files to external storage

## System Dependency Issues

### "Missing system dependencies" Error

**Symptoms:**
```
RuntimeError: Missing system dependencies: pdftotext (poppler/poppler-utils), tesseract
```

**Solutions:**

**macOS:**
```bash
brew install poppler tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install poppler-utils tesseract-ocr
```

**Linux (Fedora/RHEL):**
```bash
sudo dnf install poppler-utils tesseract
```

**Windows:**
```bash
choco install poppler tesseract
```

**After installation:**
- Restart terminal
- Verify with `pdftotext -v` and `tesseract --version`

### Poppler Not Found

**Symptoms:**
```
pdftotext: command not found
```

**Solutions:**

1. **Install poppler** (see above)

2. **Check PATH:**
   ```bash
   which pdftotext  # Should show path
   ```

3. **Add to PATH (Windows):**
   - Find installation directory
   - Add to System Environment Variables
   - Restart terminal

4. **Manual installation (Windows):**
   - Download from [poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases)
   - Extract to `C:\Program Files\poppler`
   - Add `C:\Program Files\poppler\Library\bin` to PATH

### Tesseract Not Found

**Symptoms:**
```
tesseract: command not found
TesseractNotFoundError
```

**Solutions:**

1. **Install Tesseract** (see above)

2. **Check PATH:**
   ```bash
   which tesseract  # Should show path
   ```

3. **Install language data:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr-eng
   ```

4. **Set TESSDATA_PREFIX (if needed):**
   ```bash
   export TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata
   ```

## General Errors

### Temporary Files Not Cleaned Up

**Symptoms:**
- `/tmp` full of PDF files
- Disk space running out

**Cause:** Process interrupted before cleanup.

**Solutions:**

1. **Manual cleanup:**
   ```bash
   # Check for leftover temp files
   ls /tmp/*.pdf
   
   # Remove if safe
   rm /tmp/tmp*.pdf
   ```

2. **Let Nano PDF finish:**
   - Cleanup happens at end of process
   - Don't interrupt with Ctrl+C if possible

3. **Restart if hung:**
   - If process is stuck, interrupt and clean manually

### Unicode/Character Encoding Errors

**Symptoms:**
```
UnicodeDecodeError
UnicodeEncodeError
```

**Solutions:**

1. **Use UTF-8 encoding:**
   ```bash
   export LC_ALL=en_US.UTF-8
   export LANG=en_US.UTF-8
   ```

2. **Check filename encoding:**
   - Rename files with special characters
   - Use ASCII-safe filenames

3. **Update locale:**
   ```bash
   # Ubuntu/Debian
   sudo locale-gen en_US.UTF-8
   ```

### SSL/Certificate Errors

**Symptoms:**
```
SSLError: certificate verify failed
```

**Solutions:**

1. **Update certificates:**
   ```bash
   # macOS
   /Applications/Python*/Install\ Certificates.command
   
   # Linux
   sudo apt-get install ca-certificates
   ```

2. **Update Python:**
   ```bash
   pip install --upgrade certifi
   ```

3. **Check firewall/proxy:**
   - Corporate firewalls may block API calls
   - Configure proxy if needed

### Module Import Errors

**Symptoms:**
```
ImportError: cannot import name 'X'
ModuleNotFoundError: No module named 'X'
```

**Solutions:**

1. **Update dependencies:**
   ```bash
   pip install --upgrade nano-pdf
   ```

2. **Reinstall with dependencies:**
   ```bash
   pip uninstall nano-pdf
   pip install nano-pdf
   ```

3. **Check for conflicts:**
   ```bash
   pip check
   ```

4. **Use fresh virtual environment:**
   ```bash
   python -m venv fresh-env
   source fresh-env/bin/activate
   pip install nano-pdf
   ```

## Getting More Help

If your issue isn't covered here:

1. **Check logs:**
   - Error messages contain useful information
   - Include full error message when asking for help

2. **Enable verbose output:**
   - Python's `-v` flag: `python -v -m nano_pdf.main ...`

3. **Search existing issues:**
   - [GitHub Issues](https://github.com/gavrielc/Nano-PDF/issues)
   - Someone may have had the same problem

4. **Open a new issue:**
   - Include OS, Python version, command used
   - Include complete error message
   - Describe what you expected vs what happened
   - Mention what you've already tried

5. **Ask the community:**
   - [GitHub Discussions](https://github.com/gavrielc/Nano-PDF/discussions)
   - Stack Overflow (tag: nano-pdf)

6. **Check documentation:**
   - [User Guide](USER_GUIDE.md)
   - [Installation Guide](INSTALLATION.md)
   - [API Reference](API_REFERENCE.md)
