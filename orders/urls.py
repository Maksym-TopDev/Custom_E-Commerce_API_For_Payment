from django.urls import path
from . import views

urlpatterns = [
    path("orders/", views.OrderListCreateView.as_view(), name="order-list-create"),
    path("orders/<int:pk>/", views.OrderDetailView.as_view(), name="order-detail"),
    path("order-items/", views.OrderItemListCreateView.as_view(), name="order-item-list-create"),
    path("order-items/<int:pk>/", views.OrderItemDetailView.as_view(), name="order-item-detail"),
    path("coupons/", views.CouponListCreateView.as_view(), name="coupon-list-create"),
    path("coupons/<int:pk>/", views.CouponDetailView.as_view(), name="coupon-detail"),
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
]