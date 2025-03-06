from django.db import models, transaction
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from products.models import Product

User = get_user_model()


class Coupon(models.Model):
    """Coupon for product-specific discounts."""
    code = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Coupon {self.code} ({self.discount}% Off) for {self.product.name if self.product else 'Any Product'}"


class Order(models.Model):
    """Order containing multiple products while ensuring stock management rules."""
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Canceled", "Canceled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """Calculate total amount, validate status, and handle order cancellation stock restoration."""
        is_new = self.pk is None  # Check if the order is new

        if not is_new:
            try:
                old_order = Order.objects.select_for_update().get(pk=self.pk)

                # Prevent modifying a canceled order
                if old_order.status == "Canceled" and self.status == "Canceled":
                    raise ValidationError({"detail": "This order has already been canceled and cannot be modified."})

                # Prevent restoring a canceled order
                if old_order.status == "Canceled" and self.status != "Canceled":
                    raise ValidationError({"detail": "You cannot restore a canceled order. Please create a new order."})

                # Prevent canceling a completed order
                if old_order.status == "Completed" and self.status == "Canceled":
                    raise ValidationError({"detail": "A completed order cannot be canceled."})

                # Prevent reverting a completed order back to pending
                if old_order.status == "Completed" and self.status == "Pending":
                    raise ValidationError({"detail": "A completed order cannot be reverted to pending."})

                # When transitioning from a non-canceled status to "Canceled", restore stock
                if old_order.status != "Canceled" and self.status == "Canceled":
                    for item in self.items.all():
                        item.product.restore_stock(item.quantity)
                    
                    self.total_amount = 0
                else:
                    self.total_amount = sum(item.total_price for item in self.items.all())

            except Order.DoesNotExist:
                pass  # Ignore if the order does not exist (i.e., new order)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id} | {self.user.id} - {self.user.get_full_name()} | {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)

    def calculate_total_price(self):
        """Calculate total price with coupon discount."""
        discount = 0
        if self.coupon:
            discount = (self.coupon.discount / 100) * (self.product.price * self.quantity)
        return (self.product.price * self.quantity) - discount

    def save(self, *args, **kwargs):
        """Handle stock deduction and restoration on order item changes."""
        with transaction.atomic():
            if self.pk:  # Updating an existing order item
                old_item = OrderItem.objects.select_for_update().get(pk=self.pk)
                # Restore previous stock before re-validating
                self.product.restore_stock(old_item.quantity)
                # Handle quantity changes
                if not self.product.update_stock(self.quantity):
                    raise ValidationError({"detail": f"Insufficient stock for {self.product.name}."})

            else:
                # Check if the product already exists in the order
                existing_item = OrderItem.objects.filter(order=self.order, product=self.product).first()
                if existing_item:
                    new_quantity = existing_item.quantity + self.quantity
                    if not self.product.update_stock(self.quantity):
                        raise ValidationError({"detail": f"Insufficient stock for {self.product.name}."})

                    existing_item.quantity = new_quantity
                    existing_item.total_price = existing_item.calculate_total_price()
                    existing_item.save()
                    return

                # Deduct stock for new order items
                if not self.product.update_stock(self.quantity):
                    raise ValidationError({"detail": f"Insufficient stock for {self.product.name}."})

            self.total_price = self.calculate_total_price()
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"
