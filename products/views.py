from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import BasePermission, SAFE_METHODS

from .serializers import CategorySerializer, ProductSerializer, StockLogSerializer
from .models import Category, Product, StockLog
from .filters import StockLogFilter


class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission that allows any user to view objects (safe methods)
    but only allows admin users to create, update, or delete.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


# Create your views here.
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

    @swagger_auto_schema(operation_description="Update a product (Full Update)")
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Partially update a product")
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class StockLogListView(generics.ListAPIView):
    queryset = StockLog.objects.all().order_by("-timestamp")
    serializer_class = StockLogSerializer
    permission_classes = [permissions.IsAdminUser]

    # Enable filtering by product and date
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = StockLogFilter
    ordering_fields = ["timestamp"] 