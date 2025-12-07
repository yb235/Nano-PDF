#!/usr/bin/env python3
"""
Demo script showing PDF to PowerPoint conversion capabilities
This demonstrates the Nano PDF converter with various options
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from nano_pdf import ppt_converter, ai_utils


def demo_basic_conversion():
    """Demonstrate basic PDF to PPT conversion"""
    print("=" * 70)
    print("DEMO 1: Basic PDF to PowerPoint Conversion")
    print("=" * 70)
    print()
    
    pdf_file = "sample_presentation.pdf"
    output_file = "demo_basic_output.pptx"
    
    if not os.path.exists(pdf_file):
        print(f"ERROR: {pdf_file} not found. Please create it first:")
        print("  python3 create_sample_pdf.py")
        return
    
    print(f"Converting: {pdf_file}")
    print(f"Output: {output_file}")
    print()
    
    def progress(msg):
        print(f"  {msg}")
    
    try:
        ppt_converter.convert_pdf_to_pptx(
            pdf_path=pdf_file,
            output_path=output_file,
            use_ai=False,  # Basic conversion without AI
            progress_callback=progress
        )
        print()
        print(f"✓ SUCCESS: Created {output_file}")
        print("  Open it in PowerPoint to see the converted slides!")
        print()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        print()


def demo_ai_enhanced_conversion():
    """Demonstrate AI-enhanced conversion with chart extraction"""
    print("=" * 70)
    print("DEMO 2: AI-Enhanced Conversion with Chart Extraction")
    print("=" * 70)
    print()
    
    pdf_file = "sample_presentation.pdf"
    output_file = "demo_ai_enhanced_output.pptx"
    
    if not os.path.exists(pdf_file):
        print(f"ERROR: {pdf_file} not found. Please create it first:")
        print("  python3 create_sample_pdf.py")
        return
    
    print(f"Converting: {pdf_file}")
    print(f"Output: {output_file}")
    print(f"AI Features: Chart detection and data extraction")
    print()
    print("NOTE: This requires GEMINI_API_KEY to be set")
    print()
    
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠ WARNING: GEMINI_API_KEY not set. Skipping AI demo.")
        print("  Set your API key: export GEMINI_API_KEY='your_key'")
        print()
        return
    
    def progress(msg):
        print(f"  {msg}")
    
    try:
        ppt_converter.convert_pdf_to_pptx(
            pdf_path=pdf_file,
            output_path=output_file,
            use_ai=True,  # Enable AI features
            ai_utils_module=ai_utils,
            progress_callback=progress
        )
        print()
        print(f"✓ SUCCESS: Created {output_file}")
        print("  Charts should be editable - click a chart and select 'Edit Data'")
        print()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        print()


def demo_analyze_pdf_structure():
    """Demonstrate PDF structure analysis"""
    print("=" * 70)
    print("DEMO 3: PDF Structure Analysis")
    print("=" * 70)
    print()
    
    pdf_file = "sample_presentation.pdf"
    
    if not os.path.exists(pdf_file):
        print(f"ERROR: {pdf_file} not found.")
        return
    
    print(f"Analyzing: {pdf_file}")
    print()
    
    try:
        analyzer = ppt_converter.PDFAnalyzer(pdf_file)
        
        total_pages = len(analyzer.plumber_pdf.pages)
        print(f"Total pages: {total_pages}")
        print()
        
        # Analyze first page
        print("Analyzing Page 1...")
        page_structure = analyzer.analyze_page(0)
        
        print(f"  Page dimensions: {page_structure.width:.1f} x {page_structure.height:.1f}")
        print(f"  Background color: RGB{page_structure.background_color}")
        print(f"  Text elements: {len(page_structure.text_elements)}")
        print(f"  Image elements: {len(page_structure.image_elements)}")
        print(f"  Shape elements: {len(page_structure.shape_elements)}")
        print()
        
        # Show some text samples
        if page_structure.text_elements:
            print("  Sample text elements:")
            for i, text_elem in enumerate(page_structure.text_elements[:5]):
                print(f"    {i+1}. '{text_elem.text[:50]}...' "
                      f"(font: {text_elem.font_name}, size: {text_elem.font_size:.1f}pt)")
        print()
        
        analyzer.close()
        print("✓ Analysis complete")
        print()
        
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        print()


def demo_chart_detection():
    """Demonstrate chart detection capabilities"""
    print("=" * 70)
    print("DEMO 4: Chart Detection and Analysis")
    print("=" * 70)
    print()
    
    pdf_file = "sample_presentation.pdf"
    
    if not os.path.exists(pdf_file):
        print(f"ERROR: {pdf_file} not found.")
        return
    
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠ WARNING: GEMINI_API_KEY not set. Cannot run chart detection demo.")
        print()
        return
    
    print(f"Detecting charts in: {pdf_file}")
    print()
    
    try:
        from PIL import Image
        import io
        
        analyzer = ppt_converter.PDFAnalyzer(pdf_file)
        chart_detector = ppt_converter.ChartDetector(ai_utils)
        
        # Analyze page 2 (which has a chart in the sample)
        page_num = 1  # 0-indexed
        print(f"Analyzing page {page_num + 1}...")
        
        page_structure = analyzer.analyze_page(page_num)
        
        # Get page image
        page_image = Image.open(io.BytesIO(
            analyzer.fitz_pdf[page_num].get_pixmap().tobytes("png")
        ))
        
        print(f"  Detecting charts...")
        charts = chart_detector.detect_charts(page_structure, page_image)
        
        print(f"  Found {len(charts)} chart(s)")
        print()
        
        for i, chart in enumerate(charts):
            print(f"  Chart {i+1}:")
            print(f"    Type: {chart.chart_type}")
            print(f"    Title: {chart.title}")
            print(f"    Position: ({chart.x:.1f}, {chart.y:.1f})")
            print(f"    Size: {chart.width:.1f} x {chart.height:.1f}")
            print(f"    Categories: {chart.categories}")
            print(f"    Series: {len(chart.series)}")
            for series in chart.series:
                print(f"      - {series.get('name', 'Unknown')}: {series.get('values', [])}")
            print()
        
        analyzer.close()
        print("✓ Chart detection complete")
        print()
        
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        print()


def print_menu():
    """Print demo menu"""
    print()
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "Nano PDF: PDF to PowerPoint Demos" + " " * 20 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    print("Available demos:")
    print()
    print("  1. Basic Conversion         - Simple PDF to PPT without AI")
    print("  2. AI-Enhanced Conversion   - With chart detection & extraction")
    print("  3. Structure Analysis       - Analyze PDF elements")
    print("  4. Chart Detection          - Detect and analyze charts with AI")
    print("  5. Run All Demos            - Execute all demonstrations")
    print("  q. Quit")
    print()


def main():
    """Main demo runner"""
    
    # Check if sample PDF exists
    if not os.path.exists("sample_presentation.pdf"):
        print()
        print("⚠ Sample PDF not found!")
        print()
        print("Please create it first by running:")
        print("  python3 create_sample_pdf.py")
        print()
        response = input("Create it now? (y/n): ")
        if response.lower() == 'y':
            import subprocess
            subprocess.run(["python3", "create_sample_pdf.py"])
        else:
            return
    
    while True:
        print_menu()
        choice = input("Select a demo (1-5, q): ").strip()
        print()
        
        if choice == '1':
            demo_basic_conversion()
        elif choice == '2':
            demo_ai_enhanced_conversion()
        elif choice == '3':
            demo_analyze_pdf_structure()
        elif choice == '4':
            demo_chart_detection()
        elif choice == '5':
            demo_basic_conversion()
            demo_analyze_pdf_structure()
            demo_ai_enhanced_conversion()
            demo_chart_detection()
        elif choice.lower() == 'q':
            print("Thanks for trying Nano PDF!")
            print()
            break
        else:
            print("Invalid choice. Please try again.")
            print()
        
        if choice in ['1', '2', '3', '4', '5']:
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()
