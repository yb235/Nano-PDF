# Nano PDF Installation Guide

This guide provides detailed, step-by-step installation instructions for all platforms.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Platform-Specific Installation](#platform-specific-installation)
  - [macOS](#macos)
  - [Linux (Ubuntu/Debian)](#linux-ubuntudebian)
  - [Linux (Fedora/RHEL)](#linux-fedorarhel)
  - [Windows](#windows)
- [API Key Setup](#api-key-setup)
- [Verification](#verification)
- [Alternative Installation Methods](#alternative-installation-methods)
- [Troubleshooting Installation](#troubleshooting-installation)

## Prerequisites

### Python Version

Nano PDF requires **Python 3.10 or newer**.

**Check your Python version:**
```bash
python --version
# or
python3 --version
```

If you need to install or update Python:
- **macOS**: Use Homebrew: `brew install python@3.11`
- **Linux**: Use your package manager: `sudo apt install python3.11`
- **Windows**: Download from [python.org](https://www.python.org/downloads/)

### Pip (Python Package Manager)

Pip usually comes with Python. Verify it's installed:
```bash
pip --version
# or
pip3 --version
```

If pip is missing:
```bash
python -m ensurepip --upgrade
```

## Platform-Specific Installation

### macOS

#### Step 1: Install Homebrew (if not already installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### Step 2: Install System Dependencies

```bash
brew install poppler tesseract
```

**What these do:**
- **poppler**: Provides tools for PDF rendering (pdftotext, pdfimages)
- **tesseract**: OCR engine for text extraction

#### Step 3: Install Nano PDF

**Option A: Using pip (recommended)**
```bash
pip install nano-pdf
```

**Option B: Using pipx (isolated installation)**
```bash
# Install pipx first if needed
brew install pipx
pipx ensurepath

# Install Nano PDF
pipx install nano-pdf
```

**Option C: Using uvx (run without installing)**
```bash
# Install uv first
brew install uv

# Run directly (downloads on first use)
uvx nano-pdf edit myfile.pdf 1 "Your edit"
```

#### Step 4: Verify Installation

```bash
nano-pdf version
```

You should see: `Nano PDF v0.2.1` (or later)

---

### Linux (Ubuntu/Debian)

#### Step 1: Update Package Lists

```bash
sudo apt-get update
```

#### Step 2: Install System Dependencies

```bash
sudo apt-get install -y poppler-utils tesseract-ocr
```

**Optional: Install additional language packs for Tesseract**
```bash
# For French
sudo apt-get install tesseract-ocr-fra

# For Spanish
sudo apt-get install tesseract-ocr-spa

# List available languages
apt-cache search tesseract-ocr
```

#### Step 3: Install Python and Pip (if needed)

```bash
sudo apt-get install -y python3.10 python3-pip
```

#### Step 4: Install Nano PDF

```bash
pip3 install nano-pdf
```

**If you get a "externally-managed-environment" error:**
```bash
# Use pipx instead
sudo apt-get install pipx
pipx install nano-pdf
```

#### Step 5: Add to PATH (if needed)

```bash
# Add to your ~/.bashrc or ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"

# Reload shell
source ~/.bashrc
```

#### Step 6: Verify Installation

```bash
nano-pdf version
```

---

### Linux (Fedora/RHEL)

#### Step 1: Install System Dependencies

```bash
sudo dnf install poppler-utils tesseract
```

#### Step 2: Install Nano PDF

```bash
pip3 install nano-pdf
```

---

### Windows

#### Step 1: Install Python

1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **Important**: Check "Add Python to PATH" during installation
4. Verify: Open Command Prompt and run `python --version`

#### Step 2: Install Chocolatey (Package Manager)

Open **PowerShell as Administrator** and run:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

Or follow the [official Chocolatey installation guide](https://chocolatey.org/install).

#### Step 3: Install System Dependencies

In **PowerShell as Administrator**:

```powershell
choco install poppler tesseract
```

**Important**: After installation, close and reopen your terminal to refresh the PATH.

#### Step 4: Verify System Dependencies

```bash
pdftotext -v
tesseract --version
```

Both commands should display version information.

#### Step 5: Install Nano PDF

In a regular Command Prompt or PowerShell:

```bash
pip install nano-pdf
```

#### Step 6: Verify Installation

```bash
nano-pdf version
```

#### Alternative: Manual Installation of Dependencies

If Chocolatey doesn't work, you can install manually:

**Poppler:**
1. Download from [poppler-windows releases](https://github.com/oschwartz10612/poppler-windows/releases)
2. Extract to `C:\Program Files\poppler`
3. Add `C:\Program Files\poppler\Library\bin` to your PATH

**Tesseract:**
1. Download from [tesseract-ocr releases](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the installer
3. Note the installation path (usually `C:\Program Files\Tesseract-OCR`)
4. Add to PATH if not done automatically

**Adding to PATH on Windows:**
1. Search for "Environment Variables" in Start menu
2. Click "Environment Variables"
3. Under "System Variables", select "Path" and click "Edit"
4. Click "New" and add the path
5. Click "OK" on all dialogs
6. Restart your terminal

---

## API Key Setup

### Getting Your API Key

1. Visit [Google AI Studio](https://aistudio.google.com/api-keys)
2. Sign in with your Google account
3. Click "Create API Key" or "Get API Key"
4. **Enable billing** on your Google Cloud project
   - This is **required** for Gemini 3 Pro Image
   - Free tier keys will not work
   - See [pricing](https://ai.google.dev/pricing)

### Setting the API Key

You need to set your API key as an environment variable so Nano PDF can access it.

#### Option 1: Temporary (Current Session Only)

**macOS/Linux:**
```bash
export GEMINI_API_KEY="your_api_key_here"
```

**Windows (Command Prompt):**
```cmd
set GEMINI_API_KEY=your_api_key_here
```

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your_api_key_here"
```

**Limitation**: You'll need to set this every time you open a new terminal.

#### Option 2: Permanent (Recommended)

**macOS/Linux:**

Add to your shell configuration file (`~/.bashrc`, `~/.zshrc`, or `~/.bash_profile`):

```bash
# Open your shell config file
nano ~/.zshrc  # or ~/.bashrc for bash

# Add this line
export GEMINI_API_KEY="your_api_key_here"

# Save and reload
source ~/.zshrc
```

**Windows:**

1. Search for "Environment Variables" in Start menu
2. Click "Environment Variables"
3. Under "User variables", click "New"
4. Variable name: `GEMINI_API_KEY`
5. Variable value: `your_api_key_here`
6. Click "OK"
7. Restart your terminal

#### Option 3: Using .env File (For Development)

If you cloned the repository:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your key
nano .env

# Add this line:
GEMINI_API_KEY=your_api_key_here
```

**Note**: The .env file only works when running from the repository directory.

### Verifying API Key Setup

Test that your API key is set correctly:

**macOS/Linux:**
```bash
echo $GEMINI_API_KEY
```

**Windows (Command Prompt):**
```cmd
echo %GEMINI_API_KEY%
```

**Windows (PowerShell):**
```powershell
echo $env:GEMINI_API_KEY
```

You should see your API key printed (not blank).

## Verification

### Complete Installation Check

Run this command to verify everything is working:

```bash
nano-pdf version
```

Expected output: `Nano PDF v0.2.1`

### System Dependencies Check

The tool will automatically check for dependencies when you run a command. To test:

```bash
# Try to edit a non-existent file (it will check dependencies first)
nano-pdf edit test.pdf 1 "test"
```

If dependencies are missing, you'll see clear error messages with installation instructions.

### Manual Dependency Verification

**Check poppler:**
```bash
pdftotext -v
```
Should display version information.

**Check tesseract:**
```bash
tesseract --version
```
Should display version information.

## Alternative Installation Methods

### Installing from Source

For development or the latest features:

```bash
# Clone the repository
git clone https://github.com/gavrielc/Nano-PDF.git
cd Nano-PDF

# Install with pip
pip install -e .

# Or with uv (faster)
uv sync
```

### Using uvx (No Installation Required)

```bash
# Install uv
pip install uv

# Run Nano PDF directly
uvx nano-pdf edit myfile.pdf 1 "Your edit"
```

This downloads and runs Nano PDF without permanently installing it.

### Using Docker (Experimental)

If you're comfortable with Docker:

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

RUN pip install nano-pdf

ENV GEMINI_API_KEY=""

ENTRYPOINT ["nano-pdf"]
```

Build and run:
```bash
docker build -t nano-pdf .
docker run -v $(pwd):/workspace -e GEMINI_API_KEY="your_key" nano-pdf edit /workspace/file.pdf 1 "Edit"
```

## Troubleshooting Installation

### "nano-pdf: command not found"

**Cause**: The installation directory is not in your PATH.

**Solution**:

1. Find where pip installed it:
   ```bash
   pip show nano-pdf
   ```
   Look for the "Location" field.

2. Add to PATH:
   ```bash
   # Add to ~/.bashrc or ~/.zshrc
   export PATH="$HOME/.local/bin:$PATH"
   ```

3. Reload shell:
   ```bash
   source ~/.bashrc
   ```

### "No module named 'nano_pdf'"

**Cause**: Python can't find the installed package.

**Solutions**:

1. Make sure you're using the right Python:
   ```bash
   python3 -m pip install nano-pdf
   ```

2. Check if it's installed:
   ```bash
   pip list | grep nano-pdf
   ```

3. Try reinstalling:
   ```bash
   pip uninstall nano-pdf
   pip install nano-pdf
   ```

### "error: externally-managed-environment"

**Cause**: Modern Linux distros prevent system-wide pip installs.

**Solution**: Use pipx or a virtual environment:

```bash
# Option 1: Use pipx
pipx install nano-pdf

# Option 2: Use a virtual environment
python -m venv nano-pdf-env
source nano-pdf-env/bin/activate
pip install nano-pdf
```

### "Permission denied" errors

**Cause**: Trying to install to system directories without admin rights.

**Solution**: Install to user directory:

```bash
pip install --user nano-pdf
```

### Poppler or Tesseract not found

**Symptoms**: Error message about missing pdftotext or tesseract.

**Solution**: 

1. Verify they're installed:
   ```bash
   which pdftotext
   which tesseract
   ```

2. If not found, reinstall system dependencies (see platform-specific instructions above)

3. On Windows, ensure they're in your PATH

4. Restart your terminal after installation

### Different Python versions

If you have multiple Python versions:

```bash
# Use specific Python version
python3.11 -m pip install nano-pdf

# Then run with that version
python3.11 -m nano_pdf.main edit file.pdf 1 "Edit"
```

### Tesseract language data missing

**Symptom**: OCR errors or warnings about missing language data.

**Solution**: Install language packs:

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr-eng  # English
```

**macOS:**
```bash
brew install tesseract-lang
```

**Windows:**
- Reinstall Tesseract with "Additional language data" option selected

### Import errors after installation

**Solution**: Clear pip cache and reinstall:

```bash
pip cache purge
pip uninstall nano-pdf
pip install --no-cache-dir nano-pdf
```

## Getting Help

If you're still having trouble:

1. Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Search [existing issues](https://github.com/gavrielc/Nano-PDF/issues)
3. Open a [new issue](https://github.com/gavrielc/Nano-PDF/issues/new) with:
   - Your OS and version
   - Python version (`python --version`)
   - Installation method used
   - Complete error message
   - Steps you've already tried

## Next Steps

Once installed, head to the [User Guide](USER_GUIDE.md) to learn how to use Nano PDF!
