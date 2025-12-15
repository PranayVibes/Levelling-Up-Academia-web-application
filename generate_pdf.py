from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import pandas as pd
import os

# Load results from CSV 
df = pd.read_csv('output/results.csv')

# Create PDF
print("Generating PDF report with ReportLab...")
doc = SimpleDocTemplate("LEVELLING_UP_ACADEMIA_FINAL_REPORT.pdf", pagesize=A4)
story = []
styles = getSampleStyleSheet()

# Title
title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, spaceAfter=30, alignment=1)
story.append(Paragraph("Levelling Up Academia", title_style))
story.append(Paragraph("Overcoming Flaws in Traditional Academic Metrics", styles['Heading2']))
story.append(Spacer(1, 20))

# Author Info
story.append(Paragraph("<b>Intern:</b> Pranay Bhandare<br/><b>PI:</b> Suraj Shetiya<br/><b>Date:</b> December 6, 2025", styles['Normal']))
story.append(Spacer(1, 40))

# Executive Summary
story.append(Paragraph("Executive Summary", styles['Heading2']))
summary = """This project introduces three novel academic metrics that overcome major flaws in the classic h-index: recency bias, collaboration inflation, and inconsistency. Empirical evaluation on 10 world-famous researchers shows our metrics provide fairer, more robust assessment."""
story.append(Paragraph(summary, styles['Normal']))
story.append(Spacer(1, 20))

# Results Table
story.append(Paragraph("Results Summary", styles['Heading2']))
data = [['Researcher', 'h-index', 'Freshness-Weighted h', 'CRI', 'CLS']] + df[['Name', 'h-index', 'Freshness-Weighted h', 'CRI (Collab-Resilient)', 'CLS (Consistency Score)']].values.tolist()
table = Table(data)
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 12),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
]))
story.append(table)
story.append(Spacer(1, 20))

# Plots
story.append(Paragraph("Visual Comparison", styles['Heading2']))
for img_file in ['output/freshness_vs_h_index.png', 'output/consistency_analysis.png']:
    if os.path.exists(img_file):
        img = Image(img_file, width=6*inch, height=4*inch)
        story.append(img)
        story.append(Spacer(1, 10))

# Conclusion
story.append(Paragraph("Conclusion", styles['Heading2']))
conclusion = """The proposed metrics successfully address the known limitations of traditional indices. Freshness-Weighted h-index favors recent impact, CRI resists mega-collaboration inflation, and CLS rewards sustained excellence. This system represents a significant step toward fairer academic evaluation."""
story.append(Paragraph(conclusion, styles['Normal']))

# Build PDF
doc.build(story)
print("PDF Generated Successfully!")
print("File name: LEVELLING_UP_ACADEMIA_FINAL_REPORT.pdf")
