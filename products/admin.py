from django.contrib import admin
from .models import StockLog, Product

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "stock", "category")
    search_fields = ("name", "category")
    list_filter = ()
    ordering = ("-id",)
    readonly_fields = ()

admin.site.register(Product, ProductAdmin)


class StockLogAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "change_type", "quantity_changed", "new_stock_level", "timestamp")
    list_filter = ("change_type", "timestamp")
    search_fields = ("product__name", "change_type")
    ordering = ("-timestamp",)  # Show newest changes first

admin.site.register(StockLog, StockLogAdmin)