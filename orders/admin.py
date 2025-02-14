from django.contrib import admin
from .models import Order, Cart, CartItem, Coupon

# Register your models here.
class CartItemInline(admin.TabularInline):
    """
    Allows CartItems to be managed within a Cart admin panel.
    """
    model = CartItem
    extra = 0  # Prevents adding extra empty rows


class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "quantity", "total_amount", "status")
    search_fields = ("user__email", "product__name", "status")
    list_filter = ("status",)
    ordering = ("-id",)
    readonly_fields = ("total_amount",)  # Prevents manual editing of total amount

admin.site.register(Order, OrderAdmin)


class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user")
    search_fields = ("user__email",)
    inlines = [CartItemInline]  # Inline CartItems in Cart

admin.site.register(Cart, CartAdmin)


class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "product", "quantity")
    search_fields = ("cart__user__email", "product__name")

admin.site.register(CartItem, CartItemAdmin)


class CouponAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "discount", "valid_from", "valid_to", "active")
    search_fields = ("code",)
    list_filter = ("active", "valid_from", "valid_to")
    ordering = ("-valid_from",)

admin.site.register(Coupon, CouponAdmin)