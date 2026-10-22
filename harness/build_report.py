"""Render the reviewed Markdown report using ReportLab (document tooling only)."""
from pathlib import Path
import re
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Preformatted

ROOT = Path(__file__).resolve().parents[1]


def paragraph_text(text):
    text = escape(text).replace('`', '')
    return re.sub(r'https://[^\s]+', lambda m: '<link href="' + m[0] + '">' + m[0] + '</link>', text)


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Copy', fontName='Helvetica', fontSize=9,
                          leading=12, spaceAfter=7))
styles.add(ParagraphStyle(name='CellCopy', fontName='Helvetica', fontSize=8.1,
                          leading=10.2, spaceAfter=0))
styles.add(ParagraphStyle(name='Commands', fontName='Courier', fontSize=8,
                          leading=11, spaceAfter=8))
story = []
lines = (ROOT / 'docs/D2-report.md').read_text(encoding='utf-8').splitlines()
i = 0
while i < len(lines):
    line = lines[i]
    if not line.strip():
        i += 1
        continue
    if line.startswith('```'):
        block = []
        i += 1
        while i < len(lines) and not lines[i].startswith('```'):
            block.append(lines[i])
            i += 1
        story.append(Preformatted('\n'.join(block), styles['Commands']))
    elif line.startswith('|'):
        rows = []
        while i < len(lines) and lines[i].startswith('|'):
            if not lines[i].startswith('| ---'):
                cells = lines[i].strip('|').split('|')
                rows.append([Paragraph(escape(c.strip()), styles['CellCopy']) for c in cells])
            i += 1
        widths = [124, 380] if len(rows[0]) == 2 else [224, 140, 140]
        table = Table(rows, colWidths=widths, repeatRows=1, hAlign='LEFT')
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e6edf5')),
            ('GRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#b7c3ce')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 7),
            ('RIGHTPADDING', (0, 0), (-1, -1), 7),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.extend([table, Spacer(1, 9)])
        continue
    elif line.startswith('# '):
        story.append(Paragraph(escape(line[2:]), styles['Title']))
    elif line.startswith('## '):
        if line.startswith('## Working') or line.startswith('## Latest live'):
            story.append(PageBreak())
        story.append(Paragraph(escape(line[3:]), styles['Heading2']))
    else:
        block = [line]
        while i+1 < len(lines) and lines[i+1].strip() and not lines[i+1].startswith(('#', '|', '```', '- ')):
            i += 1
            block.append(lines[i])
        story.append(Paragraph(paragraph_text(' '.join(block)), styles['Copy']))
    i += 1


def footer(canvas, doc):
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#526477'))
    canvas.drawString(54, 30, 'Snargent | D2 | Local synthetic-data experiment')
    canvas.drawRightString(558, 30, str(doc.page))


output = ROOT / 'output/pdf/D2-Snargent.pdf'
output.parent.mkdir(parents=True, exist_ok=True)
SimpleDocTemplate(str(output), pagesize=(612, 792), rightMargin=54, leftMargin=54,
                  topMargin=40, bottomMargin=46,
                  title='Snargent D2 - Attack Surface and Working Harness',
                  author='Snargent team').build(story, onFirstPage=footer, onLaterPages=footer)
print(output)

