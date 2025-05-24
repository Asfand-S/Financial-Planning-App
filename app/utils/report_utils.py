# app/utils/report_utils.py

import os
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.platypus import Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing, _DrawingEditorMixin
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

class PieChart(_DrawingEditorMixin,Drawing):
    def __init__(self, data=[1, 1], size=5*cm, *args,**kw):
        Drawing.__init__(self, size, size, *args,**kw)
        self._add(self,Pie(),name='pie',validate=None,desc=None)
        self.pie.height              = size
        self.pie.width               = size
        self.pie.slices.strokeColor  = colors.white
        self.pie.slices.strokeWidth  = 1
        if data == [0, 0]:
            self.pie.data            = [100]
            self.pie.slices[0].fillColor = colors.grey
        else:
            self.pie.data            = data
            color_list = ['#1e3a8a', '#2f5bb0', '#449ad0', '#12afe2', '#7dddf2']
            for i,v in enumerate(self.pie.data): self.pie.slices[i].fillColor = colors.HexColor(color_list[i % 5])

# Register fonts
def register_fonts():
    # Get the base directory of this file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Go up one level to the app directory
    app_dir = os.path.abspath(os.path.join(base_dir, '..'))
    
    # Construct full font paths
    font_dir = os.path.join(app_dir, 'static', 'fonts')
    regular_font = os.path.join(font_dir, 'Inter-Regular.ttf')
    bold_font = os.path.join(font_dir, 'Inter-Bold.ttf')
    
    # Register fonts
    pdfmetrics.registerFont(TTFont('Inter', regular_font))
    pdfmetrics.registerFont(TTFont('InterBold', bold_font))

def generate_report(data: dict):
    register_fonts()

    year = data["year"]
    income_items = data["incomes"]
    expense_items = data["expenses"]
    total_income = data["total_income"]
    total_expenses = data["total_expenses"]
    monthly_income = data["monthly_income"]
    monthly_expenses = data["monthly_expenses"]
    balance = data["balance"]
    monthly_balance = data["monthly_balance"]

    # Styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='BlueBold14Center', fontName='InterBold', fontSize=14, textColor=colors.HexColor('#0752B4'), spaceAfter=8, alignment=1))
    styles.add(ParagraphStyle(name='BlueBold14', fontName='InterBold', fontSize=12, textColor=colors.HexColor('#0752B4'), leading=16, spaceAfter=4))
    styles.add(ParagraphStyle(name='BlackBold12', fontName='InterBold', fontSize=10, textColor=colors.black, leading=14))
    styles.add(ParagraphStyle(name='Normal11', fontName='Inter', fontSize=10, textColor=colors.black, leading=14))
    styles.add(ParagraphStyle(name='White11', fontName='Inter', fontSize=10, textColor=colors.white, leading=14))

    # Helper function for 2-column table
    def make_table(data, header):
        table_data = [[Paragraph(header, styles['White11']), '']]
        for item in data:
            table_data.append([
                Paragraph(item['source'], styles['Normal11']),
                f"€ {item['amount']:,.2f}".replace(',', ' ')
            ])
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0752B4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor("#0752B4")),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (1, -1), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('COLWIDTHS', (0, 0), (0, -1), 14 * cm),
        ])
        table = Table(table_data, style=style, colWidths=[15*cm, None])
        table.spaceBefore = 8
        return table

    # Document setup
    flowables = []

    flowables.append(Paragraph("Μελέτη", styles['BlueBold14Center']))
    flowables.append(Spacer(1, 12))
    flowables.append(Paragraph("Ποιά είναι η τρέχουσα χρηματοοικονομική σας κατάσταση;", styles['BlueBold14']))
    flowables.append(Paragraph("Σε αυτό το τμήμα της μελέτης θα σας δείξουμε πώς διαμορφώνεται η τρέχουσα οικονομική σας κατάσταση.", styles['BlackBold12']))
    flowables.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey, spaceBefore=10))

    flowables.append(Spacer(1, 12))
    flowables.append(Paragraph(f"Ποιά είναι τα εισοδήμα και οι υποχρεώσεις σας για το {year};", styles['BlueBold14']))
    flowables.append(Paragraph(f"Παρακάτω μπορείτε να δείτε τη σύνθεση του ετήσιου εισοδήματός σας το {year}.", styles['BlackBold12']))

    flowables.append(make_table(income_items, "Τύπος εισοδήματος"))
    flowables.append(Spacer(1, 12))
    flowables.append(Paragraph(f"Το μέσο μηνιαίο εισόδημά σας το {year} είναι € {monthly_income}", styles['BlackBold12']))

    flowables.append(Spacer(1, 12))
    flowables.append(Paragraph(f"Από το εισόδημά σας, αφαιρείτε τα έξοδά σας. Τα έξοδά σας το {year}, θα είναι:", styles['BlackBold12']))
    flowables.append(make_table(expense_items, "Τύπος εξόδου"))

    flowables.append(Spacer(1, 12))
    flowables.append(Paragraph(f"Οι μέσες μηνιαίες δαπάνες σας το {year} είναι € {monthly_expenses}", styles['BlackBold12']))
    flowables.append(Spacer(1, 12))
    flowables.append(Paragraph("Το ποσό που απομένει μετά την αφαίρεση όλων των εξόδων, ονομάζεται υπόλοιπο προϋπολογισμού.", styles['BlackBold12']))

    # Summary Table
    summary_data = [
        [Paragraph('Συνολικό ετήσιο εισόδημα', style=styles['Normal11']), f"€ {total_income}"],
        [Paragraph('Συνολικά ετήσια έξοδα', style=styles['Normal11']), f"€ {total_expenses}"],
        [Paragraph('Συνολικό υπόλοιπο προϋπολογισμού ανά έτος', styles['White11']), f"€ {balance}"]
    ]
    summary_style = TableStyle([
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#0752B4')),
        ('TEXTCOLOR', (0, 2), (-1, 2), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor("#0752B4")),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ])
    summary_table = Table(summary_data, style=summary_style, colWidths=[15*cm, None])
    flowables.append(Spacer(1, 12))
    flowables.append(summary_table)

    # Pie Charts
    table_data = [
        ["Κατανομή Εισοδήματος", "", "Κατανομή Εξόδων"],
        [PieChart([18000, 6000]), "", PieChart([3000, 5000])]
    ]
    charts_table = Table(table_data, colWidths=[9*cm, 0.6*cm, 9*cm])
    charts_table.setStyle(TableStyle([
        # ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor("#0752B4")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, -1), "InterBold"),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (0, 1), 0.1, colors.HexColor("#0752B4")),
        ('BOX', (2, 0), (2, 1), 0.1, colors.HexColor("#0752B4")),
    ]))
    charts_table.spaceBefore = 10
    flowables.append(charts_table)

    # Final summary
    flowables.append(Spacer(1, 24))
    flowables.append(Paragraph(f"Το υπόλοιπο προϋπολογισμού σε αυτό το σενάριο ανά μήνα το {year} είναι € {monthly_balance}", styles['BlackBold12']))

    # Build PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=1*cm,
        leftMargin=1*cm,
        topMargin=1*cm,
        bottomMargin=1*cm
    )
    doc.build(flowables)
    buffer.seek(0)
    return buffer

if __name__ == "__main__":
    generate_report()
