from io import BytesIO
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def render_project_pdf(title: str, lines: list[str]) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle(title)
    pdf.drawString(72, 740, title)
    y = 710
    for line in lines:
        pdf.drawString(72, y, line[:100])
        y -= 18
    pdf.save()
    return buffer.getvalue()


def render_budget_xlsx(rows: list[dict]) -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = 'Budget'
    sheet.append(['Category', 'Description', 'Estimate', 'Actual', 'Vendor'])
    for row in rows:
        sheet.append([row.get('category'), row.get('description'), row.get('estimate'), row.get('actual'), row.get('vendor')])
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()
