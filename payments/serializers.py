from rest_framework import serializers
from .models import Payment
from decimal import Decimal


class PaymentSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0.01"))

    class Meta:
        model = Payment
        fields = ("id", "order", "stripe_payment_intent", "amount", "status")