from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product
from django.db import transaction

User = get_user_model()

class Order(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Canceled", "Canceled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")

    def save(self, *args, **kwargs):
        """
        Update stock when the order is placed.
        Restore stock when the order is canceled.
        """
        with transaction.atomic():
            if self.pk:
                old_order = Order.objects.select_for_update().get(pk=self.pk)
                
                # Restore stock if order is canceled
                if old_order.status == "Pending" and self.status == "Canceled":
                    self.product.restore_stock(self.quantity)
                
                # Deduct stock if order moves to Completed
                elif old_order.status != "Completed" and self.status == "Completed":
                    if not self.product.update_stock(self.quantity):
                        raise ValueError("Insufficient stock")
                
            super().save(*args, **kwargs)
            
    def __str__(self):
        return f"Order {self.id} | {self.user.email} | {self.status}"
    

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through="CartItem")


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"Coupon {self.code} ({self.discount}% Off)"