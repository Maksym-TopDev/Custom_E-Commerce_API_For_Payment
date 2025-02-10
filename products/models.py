from django.db import models

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
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
            return True
        return False
    
    def __str__(self):
        return self.name