from django.urls import path
from . import views
from .webhooks import stripe_webhook

urlpatterns = [
    path("payments/", views.PaymentListCreateView.as_view(), name="payment-list"),
    path("payments/<int:pk>/", views.PaymentDetailView.as_view(), name="payment-detail"),
    path("webhook/", stripe_webhook, name="stripe-webhook"),
]

"""Routes:"""
    # - GET/POST /payments/ → List & create payments
    # - GET/PUT /payments/<id>/ → View & update payment details