from rest_framework import serializers
from decimal import Decimal
from .models import Order, OrderItem, Coupon
from products.models import Product


class CouponSerializer(serializers.ModelSerializer):
    coupon_for = serializers.ReadOnlyField(source="product.name")
    
    class Meta:
        model = Coupon
        fields = "__all__"


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for individual order items."""
    product_name = serializers.ReadOnlyField(source="product.name")
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["id", "order", "product", "product_name", "quantity", "coupon", "total_price"]
        read_only_fields = ["total_price"]

    def get_total_price(self, obj):
        return f"{obj.total_price:,.2f}"
    
    def validate(self, data):
        """Ensure stock is available before adding an order item."""
        product = data["product"]
        quantity = data["quantity"]

        # If updating an existing item, include its current quantity in the available stock calculation.
        if self.instance:
            previous_quantity = self.instance.quantity
            available_stock = product.stock + previous_quantity
        else:
            available_stock = product.stock

        if quantity > available_stock:
            raise serializers.ValidationError({"quantity": f"Only {product.stock} items available in stock."})

        coupon = data.get("coupon", None)
        if coupon:
            # If the coupon has a product set, ensure it matches the order item product.
            if coupon.product and coupon.product.id != product.id:
                raise serializers.ValidationError({"coupon": f"This coupon is not applicable for the product {product.name}"})
        return data

    # Custom create() to append quantities is an item already exists
    def create(self, validated_data):
        validated_data.pop("id", None)
        order = validated_data.get("order")
        product = validated_data.get("product")
        quantity = validated_data.get("quantity")
        coupon = validated_data.get("coupon", None)

        # Check if an OrderItem for the same order and product already exists.
        existing_item = OrderItem.objects.filter(order=order, product=product).first()
        if existing_item:
            # Increase the quantity instead of creating a new item.
            existing_item.quantity += quantity
            existing_item.total_price = existing_item.calculate_total_price()
            existing_item.save()    # This will update total_price via the model's save()
            return existing_item
        else:
            # No matching item exists, so create a new OrderItem.
            new_item = OrderItem.objects.create(**validated_data)
            return new_item   
       
    
class OrderSerializer(serializers.ModelSerializer):
    """Serializer for orders with multiple items."""
    items = OrderItemSerializer(many=True)
    total_amount = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = ["id", "user", "status", "total_amount", "items"]

    def to_representation(self, instance):
        """Format total_price with commas in the API response."""
        data = super().to_representation(instance)
        data["total_amount"] = f"{instance.total_amount:,.2f}"
        return data

    def create(self, validated_data):
        """Create an order with its items, relying on OrderItem.save() for stock deduction."""
        items_data = validated_data.pop("items")
        order = Order.objects.create(**validated_data)
        total_price = 0

        # Create order items using the model's save() to ensure stock is updated once.
        for item_data in items_data:
            item_data["order"] = order
            order_item = OrderItemSerializer().create(item_data)
            total_price += order_item.total_price

        order.total_amount = total_price
        order.save()
        return order

    def update(self, instance, validated_data):
        """Update an order while ensuring stock consistency."""
        if instance.status in ["Completed", "Canceled"]:
            raise serializers.ValidationError({"detail": "Cannot modify a completed or canceled order."})
        
        items_data = validated_data.pop("items", None)

        # Update order fields.
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if items_data:
            for item_data in items_data:
                # If an item has an ID, update it.
                item_id = item_data.get("id")
                if item_id:
                    order_item = OrderItem.objects.get(id=item_id, order=instance)
                    old_quantity = order_item.quantity
                    new_quantity = item_data.get("quantity", old_quantity)
                    if old_quantity != new_quantity:
                        quantity_difference = new_quantity - old_quantity
                        if quantity_difference > 0:
                            if order_item.product.stock < quantity_difference:
                                raise serializers.ValidationError({"detail": f"Insufficient stock for {order_item.product.name}."})
                        else:
                            order_item.product.restore_stock(abs(quantity_difference))
                        order_item.quantity = new_quantity
                        order_item.total_price = order_item.calculate_total_price()
                        order_item.save()
                else:
                    item_data["order"] = instance
                    OrderItemSerializer().create(item_data)
        # Recalculate the total order amount from all items.
        instance.total_amount = sum(item.total_price for item in instance.items.all())
        instance.save()
        return instance
    