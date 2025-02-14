import qrcode
import barcode
from django.conf import settings
from barcode.writer import ImageWriter
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from io import BytesIO
from weasyprint import HTML


def generate_invoice(order, payment):
    """Generates a branded invoice PDF with QR code and barcode."""

    # Generate QR code for order tracking
    qr = qrcode.make(f"Oder ID: {order.id}")
    qr_path = f"{settings.MEDIA_ROOT}/qrcodes/order_{order.id}.png"
    qr.save(qr_path)
    
    # Generate barcode for order reference
    barcode_class = barcode.get_barcode_class('code128')
    barcode_instance = barcode_class(f"{order.id}", writer=ImageWriter())
    barcode_path = f"{settings.MEDIA_ROOT}/barcodes/order_{order.id}.png"
    barcode_instance.save(barcode_path)

    # Load HTML invoice template with branding
    context = {
        "order": order,
        "payment": payment,
        "qr_code": qr_path,
        "barcode": barcode_path,
        "logo": f"{settings.STATIC_URL}images/logo.png"
    }
    html_string = render_to_string("emails/invoice.html", context)

    # Convert HTML to PDF
    pdf_file = BytesIO()
    HTML(string=html_string).write_pdf(pdf_file)

    return pdf_file.getvalue()


def send_payment_email(order, payment, failure=False, refund=False):
    """Sends email notifications for payment events."""

    subject = "Payment Successful" if not failure and not refund else "Payment Issue"

    context = {"order": order, "payment": payment, "failure": failure, "refund": refund}
    email_html_content = render_to_string("emails/payment_notification.html", context)

    email = EmailMultiAlternatives(
        subject=subject,
        body="Invoice attached.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.user.email],
    )
    email.attach_alternative(email_html_content, "text/html")

    if not failure and not refund:
        invoice_pdf = generate_invoice(order, payment)
        email.attach(f"Invoice_{order.id}.pdf", invoice_pdf, "application/pdf")

    email.send()