"""
Create a sample PDF with various elements for testing the PDF to PPT converter
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import matplotlib.pyplot as plt
import io
from PIL import Image as PILImage


def create_chart_image():
    """Create a sample chart using matplotlib"""
    fig, ax = plt.subplots(figsize=(6, 4))
    
    categories = ['Q1', 'Q2', 'Q3', 'Q4']
    values_2023 = [1.2, 1.5, 1.8, 2.1]
    values_2024 = [1.5, 1.9, 2.3, 2.6]
    
    x = range(len(categories))
    width = 0.35
    
    ax.bar([i - width/2 for i in x], values_2023, width, label='2023', color='#4472C4')
    ax.bar([i + width/2 for i in x], values_2024, width, label='2024', color='#ED7D31')
    
    ax.set_xlabel('Quarter')
    ax.set_ylabel('Revenue ($M)')
    ax.set_title('Quarterly Revenue Comparison')
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    # Save to bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    return buf


def create_sample_pdf(filename='sample_presentation.pdf'):
    """Create a sample PDF with multiple pages and elements"""
    
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=36,
        textColor=colors.HexColor('#1F4788'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=18,
        textColor=colors.HexColor('#5B9BD5'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=24,
        textColor=colors.HexColor('#1F4788'),
        spaceAfter=20,
        fontName='Helvetica-Bold'
    )
    
    # Page 1: Title Slide
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("Quarterly Business Review", title_style))
    story.append(Paragraph("Q4 2024 Performance Analysis", subtitle_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Presented by: The Analytics Team", styles['Normal']))
    story.append(Paragraph("December 2024", styles['Normal']))
    
    # Page break
    from reportlab.platypus import PageBreak
    story.append(PageBreak())
    
    # Page 2: Content with Chart
    story.append(Paragraph("Revenue Performance", heading_style))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph(
        "Our revenue has shown consistent growth throughout 2024, "
        "with Q4 reaching an all-time high of $2.6M. This represents "
        "a 24% increase year-over-year.",
        styles['BodyText']
    ))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Add chart
    chart_img = create_chart_image()
    from reportlab.platypus import Image as RLImage
    img = RLImage(chart_img, width=5*inch, height=3.5*inch)
    story.append(img)
    
    # Page break
    story.append(PageBreak())
    
    # Page 3: Key Metrics Table
    story.append(Paragraph("Key Performance Metrics", heading_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Create table
    data = [
        ['Metric', 'Q3 2024', 'Q4 2024', 'Change'],
        ['Revenue ($M)', '2.3', '2.6', '+13%'],
        ['Customers', '1,450', '1,680', '+16%'],
        ['Average Deal Size ($K)', '158', '155', '-2%'],
        ['Customer Satisfaction', '4.2/5', '4.5/5', '+7%'],
    ]
    
    table = Table(data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph(
        "<b>Highlights:</b> Strong growth in customer acquisition and satisfaction. "
        "Slight decrease in average deal size due to strategic focus on mid-market segment.",
        styles['BodyText']
    ))
    
    # Page break
    story.append(PageBreak())
    
    # Page 4: Summary and Next Steps
    story.append(Paragraph("Summary & Next Steps", heading_style))
    story.append(Spacer(1, 0.3*inch))
    
    bullet_points = [
        "<b>Strong Performance:</b> Exceeded revenue targets by 8%",
        "<b>Customer Growth:</b> Successfully expanded customer base",
        "<b>Product Innovation:</b> Launched 3 major features in Q4",
        "<b>Team Expansion:</b> Grew team by 15% to support growth",
    ]
    
    for point in bullet_points:
        story.append(Paragraph(f"• {point}", styles['BodyText']))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("<b>Q1 2025 Priorities:</b>", styles['Heading3']))
    story.append(Spacer(1, 0.2*inch))
    
    priorities = [
        "Expand enterprise sales team",
        "Launch new product vertical",
        "Improve customer onboarding process",
        "Increase marketing investment in key regions",
    ]
    
    for i, priority in enumerate(priorities, 1):
        story.append(Paragraph(f"{i}. {priority}", styles['BodyText']))
        story.append(Spacer(1, 0.1*inch))
    
    # Build PDF
    doc.build(story)
    print(f"Sample PDF created: {filename}")


if __name__ == "__main__":
    create_sample_pdf()
