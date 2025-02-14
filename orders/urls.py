from django.urls import path
from . import views

urlpatterns = [
    path("orders/", views.OrderListCreateView.as_view(), name="order-list"),
    path("orders/<int:pk>/", views.OrderDetailView.as_view(), name="order-detail"),
    path("cart/", views.CartView.as_view(), name="cart"),
    path("cart/items/", views.CartItemView.as_view(), name="cart-item"),
    path("coupons/", views.CouponListView.as_view(), name="coupon-list"),
]

"""Routes:""" 
    # - GET/POST /orders/ → List & create orders
    # - GET/PUT /orders/<id>/ → View & update an order
    # - GET/PUT /cart/ → View & update cart
    # - POST /cart/items/ → Add an item to cart
    # - GET /coupons/ → List active coupons