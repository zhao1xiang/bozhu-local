import os
import sys
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def convert_md_to_pdf(md_path, pdf_path):
    if not os.path.exists(md_path):
        print(f"Error: {md_path} not found.")
        return

    # Standard macOS Chinese font
    font_path = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
    if not os.path.exists(font_path):
        font_path = "/Library/Fonts/Arial Unicode.ttf"
    
    font_name = "ArialUnicode"
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont(font_name, font_path))
    else:
        print("Warning: Chinese font not found, falling back to Helvetica (no Chinese support).")
        font_name = "Helvetica"

    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(name='H1', parent=styles['Heading1'], fontName=f"{font_name}-Bold" if font_name == "Helvetica" else font_name, fontSize=24, spaceAfter=20, textColor=colors.HexColor("#2563eb")))
    styles.add(ParagraphStyle(name='H2', parent=styles['Heading2'], fontName=f"{font_name}-Bold" if font_name == "Helvetica" else font_name, fontSize=18, spaceBefore=15, spaceAfter=10, textColor=colors.HexColor("#1e293b")))
    styles.add(ParagraphStyle(name='NormalChinese', parent=styles['Normal'], fontName=font_name, leading=16))
    styles.add(ParagraphStyle(name='Caption', parent=styles['Normal'], fontName=font_name, fontSize=9, textColor=colors.grey, alignment=1))

    # Update default styles
    styles['Normal'].fontName = font_name
    styles['Heading3'].fontName = font_name

    story = []

    in_table = False
    table_data = []

    for line in lines:
        line = line.strip('\n')
        
        # Handle HR
        if line.strip() == '---':
            story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey, spaceBefore=10, spaceAfter=10))
            continue

        # Handle Images ![alt](path)
        img_match = re.match(r'!\[(.*?)\]\((.*?)\)', line.strip())
        if img_match:
            alt_text = img_match.group(1)
            img_path = img_match.group(2)
            if os.path.exists(img_path):
                try:
                    # Resize image to fit page width (approx 6 inches)
                    img = Image(img_path)
                    img_width = img.drawWidth
                    img_height = img.drawHeight
                    target_width = 6 * inch
                    if img_width > target_width:
                        factor = target_width / img_width
                        img.drawWidth = target_width
                        img.drawHeight = img_height * factor
                    
                    story.append(Spacer(1, 10))
                    story.append(img)
                    if alt_text:
                        story.append(Paragraph(alt_text, styles['Caption']))
                    story.append(Spacer(1, 10))
                except Exception as e:
                    print(f"Error loading image {img_path}: {e}")
            else:
                story.append(Paragraph(f"[Image not found: {img_path}]", styles['NormalChinese']))
            continue

        # Handle Tables (basic)
        if line.strip().startswith('|') and '|' in line:
            if '---' in line:
                continue
            cells = [c.strip() for c in line.split('|') if c.strip() or line.count('|') > 1]
            if cells:
                table_data.append(cells)
                in_table = True
            continue
        elif in_table:
            if table_data:
                t = Table(table_data, hAlign='LEFT')
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), font_name),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ]))
                story.append(t)
                story.append(Spacer(1, 12))
            table_data = []
            in_table = False

        # Handle Headers
        h1_match = re.match(r'^#\s+(.+)', line)
        if h1_match:
            story.append(Paragraph(h1_match.group(1), styles['H1']))
            continue

        h2_match = re.match(r'^##\s+(.+)', line)
        if h2_match:
            story.append(Paragraph(h2_match.group(1), styles['H2']))
            continue

        h3_match = re.match(r'^###\s+(.+)', line)
        if h3_match:
            story.append(Paragraph(h3_match.group(1), styles['Heading3']))
            continue

        # List items
        bullet_match = re.match(r'^\s*[\*\-]\s+(.+)', line)
        ordered_match = re.match(r'^\s*(\d+)\.\s+(.+)', line)

        if bullet_match or ordered_match:
            item_text = bullet_match.group(1) if bullet_match else ordered_match.group(2)
            item_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', item_text)
            item_text = re.sub(r'`(.*?)`', r'<font name="Courier">\1</font>', item_text)
            story.append(Paragraph(f"• {item_text}", styles['NormalChinese']))
            continue

        # Regular Text
        if line.strip():
            processed_text = line
            processed_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', processed_text)
            processed_text = re.sub(r'`(.*?)`', r'<font name="Courier">\1</font>', processed_text)
            story.append(Paragraph(processed_text, styles['NormalChinese']))
            story.append(Spacer(1, 6))

    doc.build(story)
    print(f"Successfully converted {md_path} to {pdf_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python custom_md_to_pdf.py <input.md> <output.pdf>")
    else:
        convert_md_to_pdf(sys.argv[1], sys.argv[2])
