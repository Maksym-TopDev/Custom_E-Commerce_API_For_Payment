from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import CategorySerializer, ProductSerializer, StockLogSerializer
from .models import Category, Product, StockLog
from .filters import StockLogFilter


# Create your views here.
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]


class StockLogListView(generics.ListAPIView):
    queryset = StockLog.objects.all().order_by("-timestamp")  # Show latest logs first
    serializer_class = StockLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Enable filtering by product and date
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = StockLogFilter
    ordering_fields = ["timestamp"]  # Allow ordering by timestamp