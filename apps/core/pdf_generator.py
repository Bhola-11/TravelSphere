"""
TravelSphere PDF Generation Engine: Day-by-Day Itineraries, Boarding Passes & Invoices.
"""
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class PDFGenerator:
    @staticmethod
    def generate_invoice_pdf(order) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        title_style = ParagraphStyle(
            name='InvoiceTitle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#0F172A'),
            spaceAfter=10
        )
        elements.append(Paragraph(f"<b>TravelSphere Official Tax Invoice</b>", title_style))
        elements.append(Paragraph(f"Invoice Reference: <b>INV-{order.booking_reference}</b> | Date: {order.created_at.strftime('%B %d, %Y')}", styles['Normal']))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E2E8F0'), spaceAfter=15))

        # Billing Info Table
        info_data = [
            [Paragraph("<b>Billed To:</b>", styles['Normal']), Paragraph("<b>Travel Concierge:</b>", styles['Normal'])],
            [Paragraph(f"{order.billing_name}<br/>{order.billing_email}<br/>{order.billing_phone}", styles['Normal']),
             Paragraph("TravelSphere Global Inc.<br/>742 Evergreen Terrace, Suite 500<br/>San Francisco, CA, USA", styles['Normal'])]
        ]
        info_table = Table(info_data, colWidths=[270, 270])
        elements.append(info_table)
        elements.append(Spacer(1, 15))

        # Line items
        items_data = [["Item Description", "Type", "Qty", "Unit Price", "Total"]]
        for item in order.line_items.all():
            items_data.append([
                Paragraph(item.title, styles['Normal']),
                item.item_type,
                str(item.quantity),
                f"${item.unit_price}",
                f"${item.total_price}"
            ])
        
        # Summary rows
        items_data.append(["", "", "", "Subtotal:", f"${order.subtotal_amount}"])
        items_data.append(["", "", "", "Tax & Levies:", f"${order.tax_amount}"])
        items_data.append(["", "", "", "Total Paid:", f"${order.total_amount}"])

        t = Table(items_data, colWidths=[220, 80, 40, 90, 110])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("<i>Thank you for choosing TravelSphere for your global voyage.</i>", styles['Italic']))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
