from django.urls import path
from . import views

urlpatterns = [
    path("categories/", views.CategoryListCreateView.as_view(), name="category-list"),
    path("categories/<int:pk>/", views.CategoryDetailView.as_view(), name="category-detail"),
    path("products/", views.ProductListCreateView.as_view(), name="product-list"),
    path("products/<int:pk>/", views.ProductDetailView.as_view(), name="product-detail"),
    path("stock-logs/", views.StockLogListView.as_view(), name="stock-log-list"),
]

"""Routes:"""
    # - GET/POST /categories/ → List & create categories
    # - GET/PUT/DELETE /categories/<id>/ → Manage a category
    # - GET/POST /products/ → List & create products
    # - GET/PUT/DELETE /products/<id>/ → Manage a product
    # - GET /stock-logs/ → View stock log history
