from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Product, StockLog

@receiver(pre_save, sender=Product)
def capture_old_stock(sender, instance, **kwargs):
    """
    Store the old stock value before saving the product.
    """
    try:
        instance._old_stock = Product.objects.get(pk=instance.pk).stock
    except Product.DoesNotExist:
        instance._old_stock = None  # New product, no old stock


@receiver(post_save, sender=Product)
def log_stock_change(sender, instance, created, **kwargs):
    """
    Automatically create a StockLog entry after a product's stock is updated.
    """
    if created:
        StockLog.objects.create(
            product=instance,
            change_type="Initial Stock",
            quantity_changed=instance.stock,
            new_stock_level=instance.stock
        )
    elif instance._old_stock is not None and instance._old_stock != instance.stock:
        change = instance.stock - instance._old_stock
        change_type = "Stock Added" if change > 0 else "Stock Deducted"

        StockLog.objects.create(
            product=instance,
            change_type=change_type,
            quantity_changed=abs(change),
            new_stock_level=instance.stock
        )
