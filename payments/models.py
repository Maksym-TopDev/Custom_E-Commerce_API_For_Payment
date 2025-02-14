from django.db import models
import stripe
from django.conf import settings
from orders.models import Order

stripe.api_key = settings.STRIPE_SECRET_KEY

class Payment(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Failed", "Failed"),
        ("Refunded", "Refunded"),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")

    def create_payment_intent(self):
        """Create a Stripe PaymentIntent and save the intent ID."""
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(self.amount * 100),
                currency="usd",
                metadata={"order_id": self.order.id},
            )
            self.stripe_payment_intent = intent.id
            self.status = "Pending"
            self.save()
        except stripe.error.StripeError as e:
            print(f"Stripe Error: {str(e)}")

    def save(self, *args, **kwargs):
        """Automatically updates order status when payment is completed."""
        if self.status == "Completed":
            self.order.status = "Completed"
            self.order.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment: {self.id} | Order: {self.order.id} | {self.status}"