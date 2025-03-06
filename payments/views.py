import stripe
from django.conf import settings
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from orders.models import Order
from .models import Payment
from .serializers import PaymentSerializer
from .mpesa_service import MpesaAPI

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
class PaymentListCreateView(generics.ListCreateAPIView):
    """
    Expected fields when creating a payment:
      - order
      - stripe_payment_intent
      - amount
      - status
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Ensures the payment is linked to the requesting user.
        serializer.save(user=self.request.user)


class PaymentDetailView(generics.RetrieveUpdateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]


class MpesaPaymentView(APIView):
    """
    Endpoint to initiate an Mpesa payment via STK Push.
    Expects a POST request with:
      - phone_number: The mobile number to be charged.
      - amount: The amount to be charged.

    This view calls MpesaAPI.initiate_stk_push() (from mpesa-service.py) to start the payment process.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        phone_number = request.data.get("phone_number")
        amount = request.data.get("amount")

        if not phone_number or not amount:
            return Response ({"error": "Phone number and amount are required"}, status=status.HTTP_400_BAD_REQUEST)

        if phone_number.startswith("+"):
            phone_number = phone_number[1:]

        try:
            amount_value = int(amount)
        except ValueError:
            return Response({"error": "Invalid amount. Amount must be an integer."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Call the MpesaAPI service to initiate an STK push.
        mpesa_response = MpesaAPI.initiate_stk_push(
            phone_number=phone_number,
            amount=amount_value,
            account_reference="OrderPayment",      # Customize as needed
            transaction_desc="Payment for order"     # Customize as needed
        )

        if "error" in mpesa_response:
            return Response(mpesa_response, status=status.HTTP_400_BAD_REQUEST)

        response_data = {
            "message": "Mpesa payment initiated successfully.",
            "phone_number": phone_number,
            "amount": amount_value,
            "transaction_response": mpesa_response,
            "status": "pending"
        }
        return Response(response_data, status=status.HTTP_200_OK)


class WebhookView(APIView):
    """
    Endpoint to handle webhook notifications from external payment services.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        payload = request.data
        return Response({"message": "Webhook received", "data": payload}, status=status.HTTP_200_OK)