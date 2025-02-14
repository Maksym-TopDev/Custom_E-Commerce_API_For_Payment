import stripe
import logging
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import JsonResponse
from rest_framework import status
from orders.models import Order
from .models import Payment
from .utils import send_payment_email
from products.models import StockLog


logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
def stripe_webhook(request):
    """Handles incoming Stripe webhook events."""

    payload = request.body
    sig_header = request.headers.get("Stripe-Signature")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        # Verify the request is from Stripe
        event = stripe_webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        logger.error("Invalid webhook signature.")
        return JsonResponse({"error": "Invalid webhook signature"}, status=status.HTTP_400_BAD_REQUEST)

    # Handle specific Stripe events
    if event["type"] == "payment_intent.succeeded":
        handle_payment_success(event["data"]["object"])
    elif event["type"] == "payment_intent.payment_failed":
        handle_payment_failure(event["data"]["object"])
    elif event["type"] == "charge.refunded":
        handle_refund(event["data"]["object"])

    return JsonResponse({"status": "success"}, status=status.HTTP_200_OK)
    

def handle_payment_success(payment_intent):
    """Marks a payment as successful , updates stock, and sends an invoice."""
    payment = Payment.objects.filter(stripe_payment_intent=payment_intent["id"]).first()
    if payment:
        payment.status = "Completed"
        payment.save()

        order = payment.order
        if order:
            order.status = "completed"
            order.product.stock -= order.quantity   # Reduce stock
            order.product.save()
            order.save()

            # Log stock update
            StockLog.objects.create(
                product=order.product,
                change_type="Payment Success",
                quantity_changed=-order.quantity,
                new_stock_level=order.product.stock
            )

            logger.info(f"Stock updated: {order.product.name} reduced by {order.quantity}. New stock: {order.product.stock}")

        send_payment_email(payment.order, payment)


def handle_payment_failure(payment_intent):
    """Marks a payment as failed and sends an email notification."""
    payment = Payment.objects.filter(stripe_payment_intent=payment_intent["id"]).first()
    if payment:
        payment.status = "Failed"
        payment.save()
        send_payment_email(payment.order, payment, failure=True)
        logger.warning(f"Payment failed for Order {payment.order.id}. Payment Intent: {payment_intent['id']}")


def handle_refund(charge):
    """Marks a payment as refunded restores stock, and sends an email."""
    payment = Payment.objects.filter(stripe_payment_intent=charge["payment_intent"]).first()
    if payment:
        payment.status = "Refunded"
        payment.save()

        order = payment.order
        if order:
            order.status = "refunded"
            order.product.stock += order.quantity  # Restore stock
            order.product.save()
            order.save()

             # Log stock restoration
            StockLog.objects.create(
                product=order.product,
                change_type="Refund",
                quantity_changed=order.quantity,
                new_stock_level=order.product.stock
            )
            
            logger.info(f"Stock restored: {order.product.name} increased by {order.quantity}. New stock: {order.product.stock}")

        send_payment_email(payment.order, payment, refund=True)
