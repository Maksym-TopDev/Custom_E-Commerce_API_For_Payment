from rest_framework import generics, permissions
from .models import Order, Cart, CartItem, Coupon
from .serializers import OrderSerializer, CartSerializer, CartItemSerializer, CouponSerializer

# Create your views here.
class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Ensures order is linked to the requesting user.
        """
        serializer.save(user=self.request.user)


class OrderDetailView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]


class CartView(generics.RetrieveUpdateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return Cart.objects.get(user=self.request.user)
    

class CartItemView(generics.CreateAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]


class CouponListView(generics.ListAPIView):
    queryset = Coupon.objects.filter(active=True)
    serializer_class = CouponSerializer
    permission_classes = [permissions.AllowAny]