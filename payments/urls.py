from django.urls import path
from . import views
from .webhooks import stripe_webhook

urlpatterns = [
    path("payments/", views.PaymentListCreateView.as_view(), name="payment-list"),
    path("payments/<int:pk>/", views.PaymentDetailView.as_view(), name="payment-detail"),
    path("webhook/", stripe_webhook, name="stripe-webhook"),
    path("mpesa-pay/", views.MpesaPaymentView.as_view(), name="mpesa-pay"),
]