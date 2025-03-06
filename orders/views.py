from rest_framework import generics, permissions, status
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.views import APIView
from django.utils.timezone import now
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db import transaction

from .models import Order, OrderItem, Coupon
from .serializers import OrderSerializer, OrderItemSerializer, CouponSerializer
from products.models import Product


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
    

# Views
class OrderListCreateView(generics.ListCreateAPIView):
    """
    Stock deduction is managed by the OrderItem.save() logic via the serializer.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)
    
    def update(self, request, *args, **kwargs):
        order = self.get_object()
        if order.status in ["Completed", "Canceled"]:
            return Response({"detail": "Cannot modify a completed or canceled order."}, status=status.HTTP_400_BAD_REQUEST)
        if request.data.get("status") == "Completed":
            order.status = "Completed"
            order.save()
            return Response({"message": "Order marked as completed."})
        
        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            order = serializer.save()
        return Response(OrderSerializer(order).data)
    

class OrderItemListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return OrderItem.objects.all()
        return OrderItem.objects.filter(order__user=user).order_by("order", "id")

    def perform_create(self, serializer):
        with transaction.atomic():
            # Create the order item using our custom create method in the serializer.
            order_item = serializer.save()
            # Update the order's total amount after appending/updating items.
            order = order_item.order
            order.total_amount = sum(item.total_price for item in order.items.all())
            order.save()
            return order_item


class OrderItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return OrderItem.objects.all()
        return OrderItem.objects.filter(order__user=user)
    
    def update(self, request, *args, **kwargs):
        order_item = self.get_object()
        if order_item.order.status in ["Completed", "Canceled"]:
            return Response({"detail": "Cannot modify items in a completed or canceled order."},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(order_item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            order_item = serializer.save()
            order = order_item.order
            order.total_amount = sum(item.total_price for item in order.items.all())
            order.save()
        return Response(OrderItemSerializer(order_item).data)


class CouponListCreateView(generics.ListCreateAPIView):
    serializer_class = CouponSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return Coupon.objects.filter(active=True)
    

class CouponDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CouponSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Coupon.objects.all()


class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        order_data = request.data.get("order_items", [])

        if not order_data:
            return Response({"detail": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            order_serializer = OrderSerializer(data={"user": user.id, "status": "Pending", "items": order_data})
            order_serializer.is_valid(raise_exception=True)
            order = order_serializer.save(user=user)
        
        return Response({
            "message": "Order placed successfully!",
            "order_id": order.id,
            "total_price": order.total_amount
        }, status=status.HTTP_201_CREATED)
