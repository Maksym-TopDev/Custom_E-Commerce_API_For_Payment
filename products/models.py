from django.db import models
from django.utils.timezone import now

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    """
    This constraint prevents the database from accepting duplicates 
    based on case-insensitive comparisons.
    """
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name"], name="unique_category_name", condition=models.Q(name__iexact=models.F("name"))
            )
        ]
        verbose_name_plural = "Categories"  # Correct pluralization


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, related_name="products" ,on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()

    def update_stock(self, quantity):
        """ Deduct stock safely using transactions. """
        if self.stock >= quantity:
            self.stock = models.F("stock") - quantity
            self.save()
            return True
        return False
    
    def restore_stock(self, quantity):
        """ Restore stock when an order is canceled. """
        self.stock = models.F("stock") + quantity
        self.save()
    
    def __str__(self):
        return f"{self.name} - {self.category.name} | Stock: {self.stock}"


class StockLog(models.Model):
    """Logs stock changes for tracking inventory adjustments."""
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    change_type = models.CharField(max_length=50)  # e.g., "Payment Success", "Refund", "Added", "Removed"
    quantity_changed = models.IntegerField()
    new_stock_level = models.IntegerField()
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.product.name} - {self.change_type} - {self.quantity_changed} items"