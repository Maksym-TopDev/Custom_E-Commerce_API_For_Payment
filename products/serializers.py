from rest_framework import serializers
from decimal import Decimal
from .models import Category, Product, StockLog

class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255)  

    def validate_name(self, value):
        return value.lower()

    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    category_name = serializers.ReadOnlyField(source="category.name")
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0.01"))
    stock = serializers.IntegerField(min_value=Decimal("0"))

    def validate_name(self, value):
        if len(value) < 3:
            return serializers.ValidationError("Product name must be at least 3 characters long.")
        return value

    class Meta:
        model = Product
        fields = ["id", "name", "description", "category", "category_name", "price", "stock"]


class StockLogSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    timestamp = serializers.DateTimeField(read_only=True)

    class Meta:
        model = StockLog
        fields = ("id", "product", "product_name", "change_type", "quantity_changed", "new_stock_level", "timestamp")
        read_only_fields = ("timestamp",)  # Timestamp should not be manually set

    def validate_quantity_changed(self, value):
        """Ensure quantity change is a positive integer."""
        if value <= 0:
            raise serializers.ValidationError("Quantity changed must be greater than zero.")
        return value