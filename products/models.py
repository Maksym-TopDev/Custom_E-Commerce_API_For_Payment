from django.db import models, IntegrityError
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from django.utils.timezone import now
from django.db.models import F

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def save(self, *args, **kwargs):
        self.name = self.name.lower()

        try:
            super().save(*args, **kwargs)
        except IntegrityError:
            # Optional: You can log the error or just pass to silently ignore
            pass

    def __str__(self):
        return self.name
    
    """
    This constraint prevents the database from accepting duplicates 
    based on case-insensitive comparisons.
    """

    class Meta:
        indexes = [
        models.Index(name="idx_name_lower", fields=["name"])
    ]
        constraints = [
            models.UniqueConstraint(
                fields=["name"], 
                name="unique_category_name",
            )
        ]
        verbose_name_plural = "Categories" 


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = MarkdownxField()
    category = models.ForeignKey(Category, related_name="products" ,on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()

    def formatted_description(self):
        """Returns the description as HTML for rendering in templates."""
        return markdownify(self.description)
    
    def update_stock(self, quantity):
        """Deduct stock safely using atomic update to prevent race conditions."""
        updated_count = Product.objects.filter(
            id=self.id, stock__gte=quantity
        ).update(stock=F("stock") - quantity)

        return updated_count > 0  # True if stock was successfully updated

    def restore_stock(self, quantity):
        """Restore stock when an order is canceled using update()."""
        Product.objects.filter(pk=self.pk).update(stock=F("stock") + quantity)
    
    def __str__(self):
        return f"{self.name} - {self.category.name} | Stock: {self.stock}"


class StockLog(models.Model):
    """Logs stock changes for tracking inventory adjustments."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    change_type = models.CharField(max_length=50)  # e.g., "Payment Success", "Refund", "Added", "Removed"
    quantity_changed = models.IntegerField()
    new_stock_level = models.IntegerField()
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.product.name} -> {self.change_type} -> {self.quantity_changed} items"