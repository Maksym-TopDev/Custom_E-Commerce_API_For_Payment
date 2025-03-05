from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import StockLog, Product


@admin.register(Product)
class ProductAdmin(MarkdownxModelAdmin):  
    list_display = ("id", "name", "price", "stock", "category")
    search_fields = ("name", "category__name") 
    list_filter = ()
    ordering = ("-id",)
    readonly_fields = ()


@admin.register(StockLog)
class StockLogAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "change_type", "quantity_changed", "new_stock_level", "timestamp")
    list_filter = ("change_type", "timestamp")
    search_fields = ("product__name", "change_type")
    ordering = ("-timestamp",)  
