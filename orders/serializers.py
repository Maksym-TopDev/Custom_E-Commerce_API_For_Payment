from rest_framework import serializers
from .models import Order, Cart, CartItem, Coupon
from decimal import Decimal
from products.models import Product

class OrderSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=Decimal("1"))

    def validate(self, data):
        """Checks if enough stock is available before placing an order."""
        product = data.get("product")
        quantity = data.get("quantity")

        if product.stock < quantity:
            raise serializers.ValidationError("Not enough stock available.")
        return data
    

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ("id", "user", "products")


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ("id", "cart", "product", "quantity")


class CouponSerializer(serializers.ModelSerializer):
    """Serializer for Coupon model with validation for discount range."""
    discount = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=Decimal("0"), max_value=Decimal("100"))

    class Meta:
        model = Coupon
        fields = ("id", "code", "discount", "valid_from", "valid_to", "active")