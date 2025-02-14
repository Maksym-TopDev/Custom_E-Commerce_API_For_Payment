import stripe
from django.conf import settings
from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Payment
from .serializers import PaymentSerializer
from orders.models import Order

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
class PaymentListCreateView(generics.ListCreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Ensures the payment is linked to the requesting user.
        """
        serializer.save(user=self.request.user)


class PaymentDetailView(generics.RetrieveUpdateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]