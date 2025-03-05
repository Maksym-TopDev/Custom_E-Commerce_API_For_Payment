from django.contrib import admin
from .models import Order, OrderItem, Coupon

class OrderItemInline(admin.TabularInline):
    """
    Allows OrderItems to be managed within an Order admin panel.
    """
    model = OrderItem
    extra = 0  # Prevents adding extra empty rows


class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total_amount", "status", "created_at")
    search_fields = ("user__email", "status")
    list_filter = ("status", "created_at")
    ordering = ("-created_at",)
    readonly_fields = ("total_amount",)
    inlines = [OrderItemInline]  # Allows managing order items within an order


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "quantity", "total_price")
    search_fields = ("order__user__email", "product__name")
    list_filter = ("order__status",)
    ordering = ("-id",)

    def total_price(self, obj):
        return obj.get_total_price()
    total_price.short_description = "Total Price"  # Renames column in the admin panel


class CouponAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "product", "discount", "valid_from", "valid_to", "active")
    search_fields = ("code", "product__name")
    list_filter = ("active", "valid_from", "valid_to")
    ordering = ("-valid_from",)


# Register models in the Django admin panel
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Coupon, CouponAdmin)
