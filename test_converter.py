#!/usr/bin/env python3
"""
Quick test script for PDF to PowerPoint converter
Tests basic functionality without requiring API keys
"""

import sys
from pathlib import Path

# Test imports
print("Testing imports...")
try:
    from nano_pdf import ppt_converter, ai_utils, pdf_utils
    print("✓ All imports successful")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("\nPlease install dependencies:")
    print("  pip install -e .")
    sys.exit(1)

# Test PDF analyzer
print("\nTesting PDF analyzer...")
try:
    if not Path("sample_presentation.pdf").exists():
        print("⚠ sample_presentation.pdf not found")
        print("  Creating sample PDF...")
        import create_sample_pdf
        create_sample_pdf.create_sample_pdf()
    
    analyzer = ppt_converter.PDFAnalyzer("sample_presentation.pdf")
    total_pages = len(analyzer.plumber_pdf.pages)
    print(f"✓ PDF analyzer works - found {total_pages} pages")
    
    # Analyze first page
    page_structure = analyzer.analyze_page(0)
    print(f"  - Text elements: {len(page_structure.text_elements)}")
    print(f"  - Image elements: {len(page_structure.image_elements)}")
    print(f"  - Shape elements: {len(page_structure.shape_elements)}")
    
    analyzer.close()
    
except Exception as e:
    print(f"✗ PDF analyzer test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test PowerPoint builder
print("\nTesting PowerPoint builder...")
try:
    builder = ppt_converter.PowerPointBuilder()
    print("✓ PowerPoint builder initialized")
    
    # Add a test slide
    builder.add_page(page_structure)
    print("✓ Test slide added")
    
    # Save test output
    test_output = "test_output.pptx"
    builder.save(test_output)
    print(f"✓ PowerPoint saved to {test_output}")
    
    # Check file exists
    if Path(test_output).exists():
        file_size = Path(test_output).stat().st_size
        print(f"  - File size: {file_size:,} bytes")
    
except Exception as e:
    print(f"✗ PowerPoint builder test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test full conversion (without AI)
print("\nTesting full conversion (without AI)...")
try:
    output_file = "test_full_conversion.pptx"
    
    def progress(msg):
        print(f"  {msg}")
    
    ppt_converter.convert_pdf_to_pptx(
        pdf_path="sample_presentation.pdf",
        output_path=output_file,
        use_ai=False,  # No AI to avoid API key requirement
        progress_callback=progress
    )
    
    if Path(output_file).exists():
        file_size = Path(output_file).stat().st_size
        print(f"✓ Full conversion successful")
        print(f"  - Output: {output_file}")
        print(f"  - File size: {file_size:,} bytes")
    else:
        print("✗ Output file not created")
        sys.exit(1)
    
except Exception as e:
    print(f"✗ Full conversion test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("All tests passed! ✓")
print("=" * 70)
print("\nThe PDF to PowerPoint converter is working correctly.")
print("\nNext steps:")
print("  1. Try the CLI: nano-pdf convert sample_presentation.pdf")
print("  2. Run demos: python3 examples/convert_pdf_demo.py")
print("  3. For AI features, set GEMINI_API_KEY environment variable")
print()
